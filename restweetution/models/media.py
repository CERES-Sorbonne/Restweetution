from pydantic import BaseModel
from typing import Optional, Literal

MediaType = Literal["video", "animated_gif", "photo"]


class MediaMetrics(BaseModel):
    view_count: Optional[int]


class Media(BaseModel):
    height: Optional[int]
    width: Optional[int]
    url: Optional[str]
    duration_ms: Optional[int]
    media_key: str
    type: MediaType
    preview_image_url: Optional[str]
    public_metrics: Optional[MediaMetrics]
