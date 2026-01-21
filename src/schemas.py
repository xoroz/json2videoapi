from pydantic import BaseModel, HttpUrl
from typing import List, Optional, Literal, Union
from enum import Enum

class JobStatus(str, Enum):
    QUEUED = "queued"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"

class JobResponse(BaseModel):
    job_id: str
    status: JobStatus
    message: Optional[str] = None
    error: Optional[str] = None
    progress: Optional[int] = 0
    output_file: Optional[str] = None


class TextStyle(BaseModel):
    fontSize: Optional[Union[str, int]] = "72px"
    fontFamily: Optional[str] = "Roboto"
    textAlign: Optional[str] = "center"
    fontWeight: Optional[str] = "bold"
    color: Optional[str] = "#ffffff"
    backgroundColor: Optional[str] = None
    
    class Config:
        extra = "allow"

class Caption(BaseModel):
    start: float
    end: float
    text: str

class SubtitleStyle(BaseModel):
    marginV: Optional[int] = None
    marginH: Optional[int] = None
    color: Optional[str] = "#ffffff"
    fontSize: Optional[int] = 50
    fontFamily: Optional[str] = "Poppins"
    textTransform: Optional[Literal["uppercase", "lowercase", "capitalize"]] = None
    mode: Optional[Literal["one-word", "progressive", "karaoke"]] = None

    class Config:
        extra = "allow"

class Subtitle(BaseModel):
    styles: Optional[SubtitleStyle] = None
    captions: List[Caption]

class Visual(BaseModel):
    type: Literal["TEXT", "IMAGE", "VIDEO", "GIF", "SVG"]
    
    # Common properties
    id: Optional[str] = None
    position: Optional[str] = "center-center"
    anchor: Optional[str] = "center-center"
    track: Optional[int] = 0
    opacity: Optional[float] = 1.0
    angle: Optional[float] = 0.0
    flipH: Optional[bool] = False
    flipV: Optional[bool] = False
    x: Optional[float] = None
    y: Optional[float] = None
    width: Optional[float] = None
    height: Optional[float] = None
    
    # Timing
    enterBegin: Optional[float] = None
    enterEnd: Optional[float] = None
    exitBegin: Optional[float] = None
    exitEnd: Optional[float] = None
    duration: Optional[float] = None # For media items

    # Animations
    enterAnimation: Optional[str] = None
    exitAnimation: Optional[str] = None
    
    # Transitions (for background sequences)
    transition: Optional[str] = None
    transitionDuration: Optional[float] = None
    transitionId: Optional[str] = None

    # Processing
    cropParams: Optional[dict] = None
    chromaKey: Optional[dict] = None
    filter: Optional[dict] = None
    zoom: Optional[bool] = None

    # TEXT specific
    text: Optional[str] = None
    html: Optional[str] = None
    style: Optional[TextStyle] = None
    
    # Media specific (IMAGE, VIDEO, GIF, SVG)
    src: Optional[str] = None
    svg: Optional[str] = None # Content of SVG
    resize: Optional[Literal["contain", "cover", "stretch"]] = None
    
    # VIDEO/AUDIO specific
    volume: Optional[float] = 1.0
    speed: Optional[float] = 1.0
    videoBegin: Optional[float] = None
    videoEnd: Optional[float] = None
    videoDuration: Optional[float] = None

    class Config:
        extra = "allow"

class Audio(BaseModel):
    src: str
    volume: Optional[float] = 1.0
    audioBegin: Optional[float] = 0.0
    audioEnd: Optional[float] = None

class VideoProject(BaseModel):
    name: str # e.g. "my-video"
    resolution: Optional[str] = "hd"
    width: Optional[int] = None
    height: Optional[int] = None
    backgroundColor: Optional[str] = "#000000"
    duration: float
    visuals: List[Visual] = []
    audios: List[Audio] = []
    subtitle: Optional[Subtitle] = None
    outputFormat: Optional[str] = "mp4"
