from pathlib import Path

import pandas as pd

SRC_DIR = Path(__file__).parent
import sys
sys.path.append(SRC_DIR.parent.as_posix())

from app.models import CurrencyPairModel
from app.database import SessionLocal


def populate_data():
    session = SessionLocal()

    df = pd.read_csv(SRC_DIR / "exchange.csv")
    df = df.melt(id_vars=['Date'])

    df["from_currency"] = df.variable.apply(lambda x: x.split("/")[0])
    df["to_currency"] = df.variable.apply(lambda x: x.split("/")[1])

    df = df.drop(columns=["variable"]).rename({"Date": "date", "value": "rate"}, axis=1)
    for _, row in df.iterrows():
        model_row = CurrencyPairModel(**row.to_dict())
        session.add(model_row)
        session.commit()
        session.refresh(model_row)


if __name__ == '__main__':
    populate_data()
