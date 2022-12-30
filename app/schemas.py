from pydantic import BaseModel


class CurrencyPairCreateUpdateSchema(BaseModel):
    from_currency: str
    to_currency: str
    date: str
    rate: float

    class Config:
        orm_mode = True
        allow_population_by_field_name = True
        arbitrary_types_allowed = True
