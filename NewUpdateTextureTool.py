# PYTHON CODE SAMPLE GARRETT HOYOS
# NEW/UPDATE TEXTURE TOOL: This was created in Python, implemented in Houdini for the BYU 
# Senior Film "OWNED". It is a tool made into a one click button so that a texture artist 
# can seamlessly put their texture map into the pipeline.

# This decreases potential for an artist to mess up the pipeline so they don't go into the actual
# file structure.
# It increases consistency in the film as it converts their image file to a .exr while renaming
# their texture maps for naming convention across the film.  

def newTexture():
    # Get a list of assets 
    assetList = glob.glob(os.path.join(os.environ['ASSETS_DIR'], '*'))
    selections = []
    for aL in assetList:
        # Basename takes last folder in path.
        selections.append(os.path.basename(aL)) 
        # Sort alphabetically
    selections.sort()
    # Present artist with current list of digital assets
    answer = ui.listWindow(selections, wmessage='Choose an asset to add/update texture')
    if answer:
        answer = answer[0]
        assetName = selections[answer]
        assetImageDir = os.path.join(os.environ['ASSETS_DIR'], assetName, 'images')

        # Direct user to geometry file path of asset
        sdir = '$JOB/PRODUCTION/assets/'+assetName+'/geo/bjsonFiles'
        geoPath = ui.fileChooser(start_dir=sdir, wtitle='Choose Asset Geometry for Texture', mode=fileMode.Read, extensions='*.bjson, *.obj')
        geoName, ext = os.path.splitext(os.path.basename(geoPath))

        # Present artist list of shading passes
        shadingPassList = ['diffuse','specular','bump','scalar_displacement','vector_displacement', 'opacity', 'single_SSS', 'multi_SSS', 'other']
        answer = ui.listWindow(shadingPassList, wmessage='Which texture will you be creating/updating?')
        if answer: 
            answer = answer[0]
            shadingPass = shadingPassList[answer]

            # Allow artist to choose texture map in user local directory   
            userDirectory = os.environ['USER_DIR']
            userTextureMap = ui.fileChooser(start_dir=userDirectory, wtitle='Browse to the Texture Map in your User Directory', image=True, extensions='*.jpg,*.jpeg,*.tiff,*.tif,*.png,*.exr') 
            userTextureMap = os.path.expandvars(userTextureMap)

            # Set Variables for texture paths
            newTexture = '/tmp/newTexture.png'
            convertedTexture = '/tmp/convertedTexture.png'
            finalTexture = '/tmp/finalTexture.exr'

            # Take any image and convert to a 16 bit PNG
            os.system('iconvert -d 16 ' +userTextureMap+ newTexture)
            
            # Gamma correct for linear workflow except for displacement passes
            if shadingPass == 'diffuse' or shadingPass == 'specular' or shadingPass == 'single_SSS' or shadingPass == 'multi_SSS' or shadingPass == 'other':
                os.system('icomposite' +convertedTexture +'= gamma 0.4545454545' +newTexture) 
        
            # Convert to .exr with otimized settings
            os.system('iconvert -d half '+convertedTexture+finalTexture+' storage tile 64 tiley 65 compression zip')
           
            # Seperate extension from filename and rename texture to production pipeline name 
            finalTextureName, ext = os.path.splitext(os.path.basename(finalTexture))

            newTextureName = assetName+'_'+geoName+'_'+shadingPass+ext
 
            newfilepath = os.path.join(assetImageDir,newTextureName)
      # Place the new .exr file in the image directory of the asset 	
            shutil.copy(finalTexture,newfilepath)

            # Output final message
            ui.infoWindow('Your texture was saved to: '+newfilepath+' as a .exr image file')
