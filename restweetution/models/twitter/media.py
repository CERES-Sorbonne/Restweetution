from typing import Optional, Literal, List, Any

from pydantic import BaseModel

MediaType = Literal["video", "animated_gif", "photo"]


class PublicMetrics(BaseModel):
    view_count: Optional[int]


class NonPublicMetrics(BaseModel):
    playback_0_count: int
    playback_100_count: int
    playback_25_count: int
    playback_50_count: int
    playback_75_count: int


class OrganicMetrics(BaseModel):
    playback_0_count: int
    playback_100_count: int
    playback_25_count: int
    playback_50_count: int
    playback_75_count: int
    view_count: int


class PromotedMetrics(BaseModel):
    playback_0_count: int
    playback_100_count: int
    playback_25_count: int
    playback_50_count: int
    playback_75_count: int
    view_count: int


class Media(BaseModel):
    media_key: str
    type: Optional[MediaType]
    url: Optional[str]
    duration_ms: Optional[int]
    height: Optional[int]
    non_public_metrics: Optional[NonPublicMetrics]
    organic_metrics: Optional[OrganicMetrics]
    preview_image_url: Optional[str]
    promoted_metrics: Optional[PromotedMetrics]
    public_metrics: Optional[PublicMetrics]
    width: Optional[int]
    alt_text: Optional[str]
    variants: Optional[List[Any]]

    def get_url(self):
        if self.url:
            return self.url
        if not self.variants:
            return None
        valid = [v for v in self.variants if v['content_type'] == 'video/mp4']
        if not valid:
            return None
        valid = sorted(valid, key=lambda v: int(v['bit_rate']), reverse=True)
        return valid[0]['url']
