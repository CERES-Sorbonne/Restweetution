from sqlalchemy import Column, String, Boolean, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP, ARRAY
from sqlalchemy.orm import relationship

from restweetution.storage.postgres_storage.models.custom_base import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(String, primary_key=True)
    name = Column(String)
    username = Column(String)
    created_at = Column(TIMESTAMP(timezone=True))
    description = Column(String, nullable=True)
    entities_url_urls = relationship('UrlUrl', backref='_parent')
    entities_description = relationship('UserDescriptionEntities', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    location = Column(String, nullable=True)
    pinned_tweet_id = Column(String, nullable=True)
    profile_image_url = Column(String, nullable=True)
    protected = Column(Boolean, nullable=True)
    public_metrics = relationship('UserPublicMetrics', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    url = Column(String, nullable=True)
    verified = Column(Boolean, nullable=True)
    withheld = relationship('UserWithheld', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one)

    def update(self, data):
        super().update(data)
        self.update_one_to_many('entities.url.urls', UrlUrl, data)
        self.update_one_to_one('entities.description', UserDescriptionEntities, data)
        self.update_one_to_one('public_metrics', UserPublicMetrics, data)
        self.update_one_to_one('withheld', UserWithheld, data)


class UrlUrl(Base):
    __tablename__ = 'user_url_url'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('user.id'))

    start = Column(Integer)
    end = Column(Integer)
    url = Column(String)
    expanded_url = Column(String)
    display_url = Column(String)
    unwound_url = Column(String)


class UserDescriptionEntities(Base):
    __tablename__ = 'user_description_entities'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('user.id'))
    _parent = relationship('User', back_populates='entities_description')

    urls = relationship('DescriptionUrl', cascade="all,delete,delete-orphan", backref='_parent')
    hashtags = relationship('UserHashtag', cascade="all,delete,delete-orphan", backref='_parent')
    mentions = relationship('UserMention', cascade="all,delete,delete-orphan", backref='_parent')
    cashtags = relationship('UserCashtag', cascade="all,delete,delete-orphan", backref='_parent')

    def update(self, data):
        super().update(data)
        self.update_one_to_many('urls', UrlUrl, data)
        self.update_one_to_many('hashtags', UserHashtag, data)
        self.update_one_to_many('mentions', UserMention, data)
        self.update_one_to_many('cashtags', UserCashtag, data)


class DescriptionUrl(Base):
    __tablename__ = 'user_description_url'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('user_description_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    url = Column(String)
    expanded_url = Column(String)
    display_url = Column(String)
    unwound_url = Column(String)


class UserHashtag(Base):
    __tablename__ = 'user_hashtag'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('user_description_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)


class UserMention(Base):
    __tablename__ = 'user_mention'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('user_description_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    username = Column(String)


class UserCashtag(Base):
    __tablename__ = 'user_cashtag'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('user_description_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)


class UserPublicMetrics(Base):
    __tablename__ = 'user_public_metrics'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('user.id'))
    _parent = relationship('User', back_populates='public_metrics')

    followers_count = Column(Integer)
    following_count = Column(Integer)
    tweet_count = Column(Integer)
    listed_count = Column(Integer)


class UserWithheld(Base):
    __tablename__ = 'user_withheld'
    _parent_id = Column(String, ForeignKey('user.id'), primary_key=True)
    _parent = relationship('User', back_populates='withheld')

    copyright = Column(Boolean)
    country_codes = Column(ARRAY(String))
    scope = Column(String)
