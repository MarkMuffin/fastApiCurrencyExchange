from sqlalchemy import Column, create_engine, String, Date, Float
from fastapi_utils.guid_type import GUID, GUID_DEFAULT_SQLITE

from app.database import Base

engine = create_engine('postgresql+psycopg2://postgres:postgres@localhost/')


class CurrencyPairModel(Base):
    __tablename__ = 'currency_pairs'
    id = Column(GUID, primary_key=True, default=GUID_DEFAULT_SQLITE)
    from_currency = Column(String)
    to_currency = Column(String)
    date = Column(Date)
    rate = Column(Float)

    def as_dict(self):
        return {c.name: str(getattr(self, c.name)) for c in self.__table__.columns}
