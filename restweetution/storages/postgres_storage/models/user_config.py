import json

from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import JSONB

from restweetution.storages.postgres_storage.models import Base


class UserConfig(Base):
    __tablename__ = 'user_config'
    bearer_token = Column(String, primary_key=True)
    data = Column(JSONB)

    def update(self, data):
        super().update(data)
        self.data = json.loads(json.dumps(data, default=str))

    def to_dict(self):
        return self.data
