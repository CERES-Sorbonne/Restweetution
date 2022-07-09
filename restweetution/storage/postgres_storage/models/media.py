from sqlalchemy import Integer, Column, String, ForeignKey
from sqlalchemy.dialects.postgresql import ARRAY, JSONB
from sqlalchemy.orm import relationship

from restweetution.storage.postgres_storage.models import Base


class MediaNonPublicMetrics(Base):
    __tablename__ = 'media_non_public_metrics'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('media.media_key'))
    _parent = relationship('Media', back_populates='non_public_metrics')

    playback_0_count = Column(Integer)
    playback_100_count = Column(Integer)
    playback_25_count = Column(Integer)
    playback_50_count = Column(Integer)
    playback_75_count = Column(Integer)


class MediaOrganicMetrics(Base):
    __tablename__ = 'media_organic_metrics'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('media.media_key'))
    _parent = relationship('Media', back_populates='organic_metrics')

    playback_0_count = Column(Integer)
    playback_100_count = Column(Integer)
    playback_25_count = Column(Integer)
    playback_50_count = Column(Integer)
    playback_75_count = Column(Integer)
    view_count = Column(Integer)


class MediaPromotedMetrics(Base):
    __tablename__ = 'media_promoted_metrics'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('media.media_key'))
    _parent = relationship('Media', back_populates='promoted_metrics')

    playback_0_count = Column(Integer)
    playback_100_count = Column(Integer)
    playback_25_count = Column(Integer)
    playback_50_count = Column(Integer)
    playback_75_count = Column(Integer)
    view_count = Column(Integer)


class MediaPublicMetrics(Base):
    __tablename__ = 'media_public_metrics'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('media.media_key'))
    _parent = relationship('Media', back_populates='public_metrics')

    view_count = Column(Integer)


class Media(Base):
    __tablename__ = 'media'
    media_key = Column(String, primary_key=True)
    type = Column(String)
    url = Column(String, nullable=True)
    duration_ms = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    non_public_metrics = relationship(
        'MediaNonPublicMetrics',
        cascade="all,delete,delete-orphan",
        back_populates='_parent',
        uselist=False)  # one-to-one
    organic_metrics = relationship(
        'MediaOrganicMetrics',
        cascade="all,delete,delete-orphan",
        back_populates='_parent',
        uselist=False)  # one-to-one
    preview_image_url = Column(String, nullable=True)
    promoted_metrics = relationship(
        'MediaPromotedMetrics',
        cascade="all,delete,delete-orphan",
        back_populates='_parent',
        uselist=False)  # one-to-one
    public_metrics = relationship(
        'MediaPublicMetrics',
        cascade="all,delete,delete-orphan",
        back_populates='_parent',
        uselist=False)  # one-to-one
    width = Column(Integer, nullable=True)
    alt_text = Column(String, nullable=True)
    variants = Column(ARRAY(JSONB), nullable=True)

    def update(self, data):
        super().update(data)
        self.update_one_to_one('non_public_metrics', MediaNonPublicMetrics, data)
        self.update_one_to_one('organic_metrics', MediaOrganicMetrics, data)
        self.update_one_to_one('promoted_metrics', MediaPromotedMetrics, data)
        self.update_one_to_one('public_metrics', MediaPublicMetrics, data)
        self.variants = data['variants']
