from sqlalchemy import Column, Integer, String, ForeignKey, Float, Boolean
from sqlalchemy.dialects.postgresql import ARRAY, TIMESTAMP
from sqlalchemy.orm import relationship

# class Tweet(Base):

#     def __repr__(self):
#         return "<Book(title='{}', author='{}', pages={}, published={})>" \
#             .format(self.title, self.author, self.pages, self.published)
from restweetution.storage.postgres_storage.models.custom_base import Base


class Tweet(Base):
    __tablename__ = 'tweet'

    id = Column(String, primary_key=True)
    text = Column(String)
    created_at = Column(TIMESTAMP(timezone=True))
    author_id = Column(String, nullable=True)
    conversation_id = Column(String, nullable=True)
    in_reply_to_user_id = Column(String, nullable=True)
    referenced_tweets = relationship('ReferencedTweet', cascade="all,delete,delete-orphan", backref='_parent')  # one-to-many
    attachments = relationship('Attachment', cascade="all,delete,delete-orphan", back_populates="_parent", uselist=False)  # one-to-one
    geo = relationship('Geo', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    context_annotations = relationship('ContextAnnotation', cascade="all,delete,delete-orphan", backref='_parent')  # one-to-many
    entities = relationship('TweetEntities', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    withheld = relationship('TweetWithheld', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    public_metrics = relationship('TweetPublicMetrics', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    organic_metrics = relationship('TweetOrganicMetrics', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    promoted_metrics = relationship('TweetPromotedMetrics', cascade="all,delete,delete-orphan", back_populates='_parent', uselist=False)  # one-to-one
    possibly_sensitive = Column(Boolean, nullable=True)
    lang = Column(String, nullable=True)
    source = Column(String, nullable=True)
    reply_settings = Column(String, nullable=True)

    def update(self, data):
        super().update(data)
        self.update_one_to_many('referenced_tweets', ReferencedTweet, data)
        self.update_one_to_one('attachments', Attachment, data)
        self.update_one_to_one('geo', Geo, data)
        self.update_one_to_many('context_annotations', ContextAnnotation, data)
        self.update_one_to_one('entities', TweetEntities, data)
        self.update_one_to_one('withheld', TweetWithheld, data)
        self.update_one_to_one('public_metrics', TweetPublicMetrics, data)
        self.update_one_to_one('organic_metrics', TweetOrganicMetrics, data)
        self.update_one_to_one('promoted_metrics', TweetPromotedMetrics, data)


class TweetPublicMetrics(Base):
    __tablename__ = 'tweet_public_metrics'
    _parent_id = Column(String, ForeignKey('tweet.id'), primary_key=True)
    _parent = relationship('Tweet', back_populates='public_metrics')

    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)
    quote_count = Column(Integer)


class TweetOrganicMetrics(Base):
    __tablename__ = 'tweet_organic_metrics'
    _parent_id = Column(String, ForeignKey('tweet.id'), primary_key=True)
    _parent = relationship('Tweet', back_populates='organic_metrics')

    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)


class TweetPromotedMetrics(Base):
    __tablename__ = 'tweet_promoted_metrics'
    _parent_id = Column(String, ForeignKey('tweet.id'), primary_key=True)
    _parent = relationship('Tweet', back_populates='promoted_metrics')

    retweet_count = Column(Integer)
    reply_count = Column(Integer)
    like_count = Column(Integer)


class TweetWithheld(Base):
    __tablename__ = 'tweet_withheld'
    _parent_id = Column(String, ForeignKey('tweet.id'), primary_key=True)
    _parent = relationship('Tweet', back_populates='withheld')

    copyright = Column(Boolean)
    country_codes = Column(ARRAY(String))
    scope = Column(String)


class Geo(Base):
    __tablename__ = 'geo'
    _parent_id = Column(String, ForeignKey('tweet.id'), primary_key=True)
    _parent = relationship('Tweet', back_populates='geo')

    coordinates_type = Column(String, nullable=True)
    coordinates_coordinates = Column(ARRAY(Float), nullable=True)
    place_id = Column(String, nullable=True)

    def update(self, data):
        super().update(data)
        self.update_value('coordinates.type', data)
        self.update_value('coordinates.coordinates', data)


class Attachment(Base):
    __tablename__ = 'attachment'
    _parent_id = Column(String, ForeignKey("tweet.id"), primary_key=True)
    _parent = relationship("Tweet", back_populates="attachments")

    media_keys = Column(ARRAY(String), nullable=True)
    poll_ids = Column(ARRAY(String), nullable=True)


class TweetEntities(Base):
    __tablename__ = 'tweet_entities'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('tweet.id'))
    _parent = relationship('Tweet', back_populates='entities')

    annotations = relationship('TweetAnnotation', backref='_parent')
    urls = relationship('TweetUrl', backref='_parent')
    hashtags = relationship('TweetHashtag', cascade="all,delete,delete-orphan", backref='_parent')
    mentions = relationship('TweetMention', cascade="all,delete,delete-orphan", backref='_parent')
    cashtags = relationship('TweetCashtag', cascade="all,delete,delete-orphan", backref='_parent')

    def update(self, data):
        super().update(data)
        self.update_one_to_many('annotations', TweetAnnotation, data)
        self.update_one_to_many('urls', TweetUrl, data)
        self.update_one_to_many('hashtags', TweetHashtag, data)
        self.update_one_to_many('mentions', TweetMention, data)
        self.update_one_to_many('cashtags', TweetCashtag, data)


class TweetAnnotation(Base):
    __tablename__ = 'tweet_annotation'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('tweet_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    probability = Column(Float)
    type = Column(String)
    normalized_text = Column(String)


class TweetUrl(Base):
    __tablename__ = 'tweet_url'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('tweet_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    url = Column(String)
    expanded_url = Column(String)
    display_url = Column(String)
    unwound_url = Column(String)


class TweetHashtag(Base):
    __tablename__ = 'tweet_hashtag'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('tweet_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)


class TweetMention(Base):
    __tablename__ = 'tweet_mention'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('tweet_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    username = Column(String)


class TweetCashtag(Base):
    __tablename__ = 'tweet_cashtag'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(Integer, ForeignKey('tweet_entities._id'))

    start = Column(Integer)
    end = Column(Integer)
    tag = Column(String)


class Domain(Base):
    __tablename__ = 'domain'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)


class Entity(Base):
    __tablename__ = 'entity'
    id = Column(String, primary_key=True)
    name = Column(String)
    description = Column(String, nullable=True)


class ContextAnnotation(Base):
    __tablename__ = 'context_annotation'
    __id = Column(Integer, primary_key=True)  # internal id for ORM
    tweet_id = Column(String, ForeignKey('tweet.id'))
    domain_id = Column(String, ForeignKey('domain.id'))
    domain = relationship('Domain')
    entity_id = Column(String, ForeignKey('entity.id'))
    entity = relationship('Entity')

    def update(self, data):
        super().update(data)
        self.update_many_to_one('domain', Domain, data)
        self.update_many_to_one('entity', Entity, data)


class ReferencedTweet(Base):
    __tablename__ = 'referenced_tweet'
    __id = Column(Integer, primary_key=True)  # internal id for ORM
    type = Column(String)
    id = Column(String)
    parent_id = Column(String, ForeignKey('tweet.id'))
