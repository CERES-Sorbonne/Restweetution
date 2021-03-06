from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY, JSONB

from restweetution.storage.postgres_storage.models import Base


class Place(Base):
    __tablename__ = 'place'
    full_name = Column(String)
    id = Column(String, primary_key=True)
    contained_within = Column(ARRAY(String), nullable=True)
    country = Column(String, nullable=True)
    country_code = Column(String, nullable=True)
    geo = Column(JSONB, nullable=True)
    name = Column(String, nullable=True)
    place_type = Column(String, nullable=True)

    def update(self, data):
        super().update(data)
        self.geo = data['geo']
