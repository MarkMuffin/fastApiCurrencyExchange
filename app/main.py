import uvicorn
from fastapi import FastAPI

from app.currency_exchange import router
from app.database import engine
from app.models import Base


Base.metadata.create_all(engine)

app = FastAPI()

app.include_router(router, tags=['CurrencyExchange'], prefix='/api/currency_exchange')


@app.get("/api/healthchecker")
def root():
    return {"message": "Hello World"}


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
