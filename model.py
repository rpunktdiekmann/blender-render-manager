from dataclasses import dataclass
from enum import Enum

class RenderEngine(Enum):
    CYCLES = 'CYCLES'
    EEVEE = 'BLENDER_EEVEE'
    WORKBENCH = 'BLENDER_WORKBENCH'

@dataclass
class RenderSettings:
    startFrame: int
    endFrame: int
    fps: float
    x: int
    y: int
    size: int
    output: str
    outputPath: str
    engine: RenderEngine
    isCamBurst : bool = False
    isCamOwnFolder : bool = False

@dataclass
class SceneInfo:
    name : str
    cameras: list
    aCamera: list
    rSettings: RenderSettings
    isActiv: bool = False


class SceneDataBlock:
    def __init__(self,sceneBlock,cameraBlocks,aCamBlock,renderSettings):
        self.sceneBlock = sceneBlock
        self.cameraBlocks = cameraBlocks
        self.activeCamera = aCamBlock
        self.renderSettings = renderSettings


@dataclass
class Blender:

    name : str
    version : str
    path : str


    def __str__(self) -> str:
        return self.name

@dataclass
class ProgramSettings:

    blenderVersions : list 
    defaultBlenderVersion : Blender = None
        

@dataclass
class Job:
    path: str
    scenes: list
    isActiv: bool = True
    blender: Blender = None
    
