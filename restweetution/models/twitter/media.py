from dataclasses import dataclass
from typing import Optional, Literal, List, Any

MediaType = Literal["video", "animated_gif", "photo"]


@dataclass
class PublicMetrics:
    view_count: Optional[int] = None


@dataclass
class NonPublicMetrics:
    playback_0_count: int
    playback_100_count: int
    playback_25_count: int
    playback_50_count: int
    playback_75_count: int


@dataclass
class OrganicMetrics:
    playback_0_count: int
    playback_100_count: int
    playback_25_count: int
    playback_50_count: int
    playback_75_count: int
    view_count: int


@dataclass
class PromotedMetrics:
    playback_0_count: int
    playback_100_count: int
    playback_25_count: int
    playback_50_count: int
    playback_75_count: int
    view_count: int


@dataclass
class Media:
    media_key: str
    type: Optional[MediaType] = None
    url: Optional[str] = None
    duration_ms: Optional[int] = None
    height: Optional[int] = None
    non_public_metrics: Optional[NonPublicMetrics] = None
    organic_metrics: Optional[OrganicMetrics] = None
    preview_image_url: Optional[str] = None
    promoted_metrics: Optional[PromotedMetrics] = None
    public_metrics: Optional[PublicMetrics] = None
    width: Optional[int] = None
    alt_text: Optional[str] = None
    variants: Optional[List[Any]] = None
