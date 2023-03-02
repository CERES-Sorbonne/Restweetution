import json

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_storage.models import Base


class CustomData(Base):
    __tablename__ = 'custom_data'

    key = Column(String, primary_key=True)
    id = Column(String, primary_key=True)
    data = Column(JSONB)

    def update(self, data):
        super().update(data)
        self.data = json.loads(json.dumps(data['data'], default=str))
