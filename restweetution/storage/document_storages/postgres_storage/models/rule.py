from sqlalchemy import Column, String, ForeignKey
from sqlalchemy.orm import relationship

from restweetution.storage.document_storages.postgres_storage.models import Base


class Rule(Base):
    __tablename__ = 'rule'
    id = Column(String, primary_key=True)
    tag = Column(String)
    value = Column(String)
    tweets = relationship('CollectedTweet', back_populates='_parent', cascade='all, delete-orphan')

    def update(self, data):
        data['tweets'] = [{'tweet_id': x} for x in data['tweet_ids']]
        super().update(data)
        self.update_one_to_many('tweets', CollectedTweet, data)

    def to_dict(self):
        data = super().to_dict()
        data['tweet_ids'] = [t.tweet_id for t in self.tweets]
        return data

class CollectedTweet(Base):
    __tablename__ = 'collected_tweet'
    _parent_id = Column(String, ForeignKey('rule.id'), primary_key=True)
    _parent = relationship('Rule', back_populates='tweets')

    tweet_id = Column(String, ForeignKey('tweet.id'), primary_key=True)
