from model import RenderSettings,SceneInfo,RenderEngine,ColorSettings  

import logging
import sys

def mouseWheelEvent(canvas,event):
    canvas.yview_scroll(int(-1*(event.delta/120)), "units")

def getOutputFormat(i):
    out = ''
    if i == 0:
        out = 'TARGA'
    elif i == 1:
        out = 'IRIS'
    elif i == 4:
        out = 'JPEG'   
    elif i == 7:
        out = 'IRIZ'   
    elif i == 14:
        out = 'RAWTGA'   
    elif i == 15:
        out = 'AVI_RAW'   
    elif i == 16:
        out = 'AVI_JPEG'   
    elif i == 17:
        out = 'PNG'   
    elif i == 20:
        out = 'BMP'   
    elif i == 21:
        out = 'HDR'
    elif i == 22:
        out = 'TIFF'
    elif i == 23:
        out = 'OPEN_EXR'
    elif i == 24:
        out = 'FFMPEG'
    elif i == 26:
        out = 'CINEON'
    elif i == 27:
        out = 'DPX'
    elif i == 28:
        out = 'OPEN_EXR_MULTILAYER'
    elif i == 29:
        out = 'DDS'
    elif i == 30:
        out = 'JP2' 
    elif i == 31:
        out = 'H264'  
    elif i == 32:
        out = 'XVID'  
    elif i == 33:
        out = 'THEORA'  
    elif i == 34:
        out = 'PSD'  
    else:
        out = 'X_could not read output format' 
    
    return out

def getOS():
    from  reMa_exception import OSNotSupportedException

    os = sys.platform
    if os == 'win32':
        return 'w'
    elif os == 'linux':
        return 'l'
    elif os == 'darwin':
        return 'm'
    else:
        raise OSNotSupportedException

class Colors():
    header = '#1f1f1f'
    widget = '#3b3b3b'
    widget2 = '#545454'
    fontColor = '#ebebeb'
    background = '#0e0e0e'
    accent = '#197ED8'
    red = '#B72E2E'

    




class BlendReader:
    import blendfile
    from  reMa_exception import BlenderVersionException,NoCameraException

    def __init__(self,blendPath):
        
        self.blendPath = blendPath
        self.scenes = []

    def readBlendFile(self):
        sceneInfos = []
        with self.blendfile.open_blend(self.blendPath) as blend: 
            version = blend.header.version
            if version < 280:
                raise self.BlenderVersionException
            #Suche Blend Datei nach allen Scenen ab
            scenes = [b for b in blend.blocks if b.code == b'SC']
            for scene in scenes:
                objBlocks = []
                cams = []
                sceneName = scene[b'id',b'name'][2:].decode('utf-8')
                logging.debug('Found scene: %s',sceneName)
                #Master Collection = Scene Collection, jede Blender Scene hat genau eine Master Collection
                master = scene.get_pointer(b'master_collection')
                logging.debug('Found master collection: %s',master[b'id',b'name'][2:].decode('utf-8'))
                #Suche Nach allen Objekten in der Master Collection
                self.searchForObjects(master,blend,objBlocks)
                #Suche nach allen Kinds Collections innerhalb der Master Collection
                #searcjCollections ist ein rekusiver aufruf
                self.searchCollections(master,blend,objBlocks)
                if objBlocks:
                    self.getAllCameras(objBlocks,cams)
                aCamera = scene.get_pointer(b'camera')
                if not aCamera:
                    raise self.NoCameraException()
                aCameraName = [aCamera[b'id',b'name'][2:].decode('utf-8')]
                RSettings = self.readRenderSettings(scene)
                sceneInfos.append(SceneInfo(sceneName,cams,aCameraName,RSettings))
                #sceneBlocks.append(SceneDataBlock(scene,cams,aCamera,RSettings))

        return sceneInfos

    def searchForObjects(self,collection,blend,objBlocks):
        #Gibt die SpeicherAdresse des ersten Kindobjekts aus, 0 = es gibt keins
        collectionObjAdd = collection[b'gobject',b'first']
        while collectionObjAdd != 0:
            collectionObj = blend.find_block_from_offset(collectionObjAdd)
            obj = collectionObj.get_pointer(b'ob')
            logging.debug('--Found object: %s',obj[b'id',b'name'][2:].decode('utf-8'))
            objBlocks.append(obj)
            collectionObjAdd = collectionObj[b'next']


    def searchCollections(self,master,blend,objBlocks):
        #Gibt die Speicheradresse der ersten Kindscollections aus, 0 = es gibt keins
        collectionChildAdd = master[b'children',b'first']
        while collectionChildAdd != 0:
            collectionChild = blend.find_block_from_offset(collectionChildAdd)
            collection = collectionChild.get_pointer(b'collection')
            logging.debug('Found collection: %s',collection[b'id',b'name'][2:].decode('utf-8'))
            self.searchForObjects(collection,blend,objBlocks)
            collectionChildAdd = collectionChild[b'next']
            self.searchCollections(collection,blend,objBlocks)

    def readRenderSettings(self,scene):
        #path =          scene[b'r', b'pic'].decode('utf-8')
        frame_start =   scene[b'r', b'sfra']
        frame_end =     scene[b'r', b'efra']
        size =          scene[b'r', b'size']
        engine =        scene[b'r', b'engine'].decode('utf-8')
        x_size =        scene[b'r', b'xsch']
        y_size =        scene[b'r', b'ysch']
        fps_info =      scene[b'r',b'frs_sec']
        outputPath =    scene[b'r', b'pic'].decode('utf-8')
        # muss noch gecheckt werden ob output != '' ist, sonst upsi dupsi im code dann später alter vallah 
        output=         getOutputFormat(int(scene[b'r',b'im_format',b'imtype']))
        colorSettings = self.readColorManagement(scene)
        return RenderSettings(frame_start,frame_end,fps_info,x_size,y_size,size,output,outputPath,RenderEngine(engine),colorSettings)
    
    def readColorManagement(self,scene):
        view_transform = scene[b'view_settings',b'view_transform'].decode('utf-8')
        look = scene[b'view_settings',b'look'].decode('utf-8')
        exposure = scene[b'view_settings',b'exposure']
        gamma = scene[b'view_settings',b'gamma']
        return ColorSettings(view_transform,look,exposure,gamma)


    def getAllCameras(self,objs,cams):
        for o in objs:
            if o[b'type'] == 11:
                cams.append(o[b'id',b'name'][2:].decode('utf-8'))

def checkOS(master):
    from reMa_exception import OSNotSupportedException
    from exceptionWindows import CriticalWindow

    from utils import getOS
    try:
        getOS()
    except OSNotSupportedException as e:
        exceptWin = CriticalWindow(e.message,master)

def exportJob(jobs):
    import json
    from model import Job
    from dataclasses import asdict
    data = []
    for job in jobs:
        data.append(asdict(job))
    with open('export.json','w', encoding='utf-8') as f:
        j=json.dump(data,f,ensure_ascii=False, indent=4,separators=(',',':'),default=str)
    print(j)

def readVersionJSON(settings):
    import json
    from model import Blender
    with open('versions.json') as f:
        versions = json.load(f)
    for version in versions:
        b=Blender(**version)
        print('######## ',type(settings))
        settings.blenderVersions.append(b)

def writeToVersionJSON(versions):
    import json
    from dataclasses import asdict
    data = []
    for v in versions:
        data.append(asdict(v))
    with open('versions.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=4,separators=(',',': '))
    print('JSOM Dumping fertig')

def readSettingsJSON():
    import json
    from model import ProgramSettings
    from model import Blender
    with open('settings.json') as f:
        settings = json.load(f)
    ps = ProgramSettings(**settings)
    ps.defaultBlenderVersion = Blender(**ps.defaultBlenderVersion)
    print('*'*50)
    print(type(ps.defaultBlenderVersion))
    return ps

def writeToSettingsJSON(settings):
    import json
    from dataclasses import asdict
    print('#'*50,' ',type(settings))
    with open('settings.json', 'w', encoding='utf-8') as f:
        json.dump(asdict(settings), f, ensure_ascii=False, indent=4,separators=(',',': '))
    print('JSOM Dumping fertig')

def checkIsDigitInput(n):
    return n == '' or n.isdigit()

def createJob(filepath,master):
    from exceptionWindows import ExceptionWindow
    from model import Job
    from reMa_exception import BlenderVersionException, NoCameraException
    from utils import BlendReader

    reader = BlendReader(filepath)
    scs = []
    try:
        scs = reader.readBlendFile()
        return Job(filepath,scs)
    except BlenderVersionException as e:
        exceptWin = ExceptionWindow(e.message,master)
    except NoCameraException as e: 
        exceptWin = ExceptionWindow(e.message,master)

def convertEnumToStr(state):
    if state is RenderEngine.CYCLES:
        return 'Cycles'
    elif state is RenderEngine.EEVEE:
        return 'Eevee'
    elif state is RenderEngine.WORKBENCH:
        return 'Workbench'

def convertStrToEnum(state):
    if state == 'Eevee':
        return RenderEngine.EEVEE

    elif state == 'Cycles':
        return RenderEngine.CYCLES

    elif state == 'Workbench':
        return RenderEngine.WORKBENCH


def main():
    
    filepath = r'E:\zstd.blend'
    a = BlendReader(filepath)
    scs = a.readBlendFile()
    print(type(scs[0]))
    print(scs[0].rSettings.colorSettings.look)
    #print(getOS())
   

if '__main__' == __name__:
    main()



