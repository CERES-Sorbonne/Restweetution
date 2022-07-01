from sqlalchemy import Column, Integer
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storage.postgres_storage.models import Base


class Error(Base):
    __tablename__ = 'error'
    _id = Column(Integer, primary_key=True)
    data = Column(JSONB)
