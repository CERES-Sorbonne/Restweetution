from sqlalchemy import Column, Integer, String
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storage.postgres_storage.models import Base


class Error(Base):
    __tablename__ = 'error'

    id = Column(Integer, primary_key=True)
    error_name = Column(String)
    traceback = Column(String)
    data = Column(JSONB)

