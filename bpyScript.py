import bpy
import sys
import json
path = sys.argv[5]
def changeRsettings(scene,rSettings):
    
    scene.render.resolution_x = rSettings['x']
    scene.render.resolution_y = rSettings['y']
    scene.render.resolution_percentage =rSettings['size']
    
    scene.frame_start = rSettings['startFrame']
    scene.frame_end = rSettings['endFrame']

    scene.render.fps = rSettings['fps']
    
    engine = ''
    if 'RenderEngine.CYCLES'== rSettings['engine']: 
        engine = 'CYCLES'
    elif 'RenderEngine.EEVEE'== rSettings['engine']: 
        engine = 'BLENDER_EEVEE'
    elif 'RenderEngine.WORKBENCH'== rSettings['engine']: 
        engine = 'BLENDER_WORKBENCH'

    scene.render.engine = engine
    
    

    #scene.render.image_settings.file_format = rSettings['output']
    
def checkJob(job):
    return job['path'] ==  bpy.data.filepath.replace('\\','/')   



def switchCamera(scene,cam):
    scene.camera =scene.objects[cam]


def renderScene(jobScene):
    rSettings = jobScene['rSettings']
    bpy.context.window.scene = bpy.data.scenes[jobScene['name']]
    scene = bpy.context.scene  
    changeRsettings(scene,rSettings)
    
    if rSettings['isCamBurst']:
        for cam in jobScene['cameras']:
            switchCamera(scene,cam)
            path = f'/{scene.name}/{cam}/{cam}_{scene.name}' if rSettings['isCamOwnFolder'] else f'/{scene.name}_{cam}'
            scene.render.filepath = rSettings['outputPath']+path
            bpy.ops.render.render(animation=True, use_viewport=True)  
    else:
        for cam in jobScene['aCamera']:
            switchCamera(scene,cam)
            path = f'/{scene.name}/{cam}/{cam}_{scene.name}' if rSettings['isCamOwnFolder'] else f'/{scene.name}_{cam}'
            scene.render.filepath = rSettings['outputPath']+path
            bpy.ops.render.render(animation=True, use_viewport=True)
        





with open(path,'r') as f:
    jobs = json.load(f)
for job in jobs:
    if checkJob(job):
        break

        
for scene in job['scenes']:
    if scene['isActiv']:
        renderScene(scene)
