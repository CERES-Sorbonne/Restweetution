from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.dialects.postgresql import TIMESTAMP
from sqlalchemy.orm import relationship

from restweetution.storage.storages.postgres_storage.models import Base


class Poll(Base):
    __tablename__ = 'poll'

    id = Column(String, primary_key=True)
    options = relationship('PollOption', cascade="all,delete,delete-orphan", backref='_parent')  # one_to_many
    duration_minutes = Column(Integer, nullable=True)
    end_datetime = Column(TIMESTAMP(timezone=True), nullable=True)
    voting_status = Column(String, nullable=True)

    def update(self, data):
        super().update(data)
        self.update_one_to_many('options', PollOption, data)


class PollOption(Base):
    __tablename__ = 'poll_option'
    _id = Column(Integer, primary_key=True)
    _parent_id = Column(String, ForeignKey('poll.id'))

    position = Column(Integer)
    label = Column(String)
    votes = Column(Integer)
