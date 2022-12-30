import collections
import heapq

from fastapi import Depends, HTTPException, status, Response, APIRouter
from sqlalchemy.orm import Session

from app.database import get_db
from app.models import CurrencyPairModel
from app.schemas import CurrencyPairCreateUpdateSchema


router = APIRouter()


@router.post('/currency_pair')
def create_currency_pair(payload: CurrencyPairCreateUpdateSchema, db: Session = Depends(get_db)):
    new_pair = CurrencyPairModel(**payload.dict())
    db.add(new_pair)
    db.commit()
    db.refresh(new_pair)
    return {"status": "success", "new_pair": new_pair}


@router.get('/currency_pair/{currency_pair_id}')
def read_currency_pair(currency_pair_id: str, db: Session = Depends(get_db)):
    currency_pair = db.query(CurrencyPairModel).filter(CurrencyPairModel.id == currency_pair_id).first()
    if not currency_pair:
        return {'error': 'currency pair not found'}
    return currency_pair.as_dict()


@router.patch('/currency_pair/{currency_pair_id}')
def update_currency_pair(currency_pair_id: str, payload: CurrencyPairCreateUpdateSchema, db: Session = Depends(get_db)):
    currency_query = db.query(CurrencyPairModel).filter(CurrencyPairModel.id == currency_pair_id)
    currency = currency_query.first()

    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No pair with this id: {currency_pair_id} found',
        )
    update_data = payload.dict(exclude_unset=True)
    currency_query.filter(CurrencyPairModel.id == currency_pair_id).update(update_data, synchronize_session=False)
    db.commit()
    db.refresh(currency)
    return {"status": "success", "currency_pair": currency}


@router.delete('/currency_pair/{currency_pair_id}')
def delete_currency_pair(currency_pair_id: str, db: Session = Depends(get_db)):
    currency_query = db.query(CurrencyPairModel).filter(CurrencyPairModel.id == currency_pair_id)
    currency = currency_query.first()
    if not currency:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No currency pair with this id: {currency_pair_id} found'
        )
    currency_query.delete(synchronize_session=False)
    db.commit()
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.get('/history')
def get_all_history_currency_pair(from_currency: str, to_currency: str, db: Session = Depends(get_db)):

    currency_query_direct = (
        db.query(CurrencyPairModel).filter(CurrencyPairModel.to_currency == to_currency)
        .filter(CurrencyPairModel.from_currency == from_currency)
    )
    history_list = currency_query_direct.all()
    response = {x.as_dict()["date"]: x.as_dict()["rate"] for x in history_list}
    if response:
        return response

    # Reverse currency exchange rate
    currency_query_reversed = (
        db.query(CurrencyPairModel).filter(CurrencyPairModel.to_currency == from_currency)
        .filter(CurrencyPairModel.from_currency == to_currency)
    )

    for currency in currency_query_reversed.all():
        currency = currency.as_dict()
        if currency["rate"] != 0:
            response.update({currency["date"]: 1 / float(currency["rate"])})
        else:
            response.update({currency["date"]: 0})

    if not response:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No history for currency pair {from_currency}/{to_currency} found'
        )
    return response


@router.get('/get_rate')
def get_rate_for_date(from_currency: str, to_currency: str, date: str, db: Session = Depends(get_db)):
    currency_query = (
        db.query(CurrencyPairModel).filter(CurrencyPairModel.date == date)
        .filter(CurrencyPairModel.from_currency == from_currency)
        .filter(CurrencyPairModel.to_currency == to_currency)
    )
    currency_query_rate = currency_query.first()
    if currency_query_rate:
        return {"rate": float(currency_query_rate.as_dict()["rate"])}

    currency_query = (db.query(CurrencyPairModel).filter(CurrencyPairModel.date == date)).all()
    currency_query = [x.as_dict() for x in currency_query]
    if not currency_query:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No data for {to_currency}/{to_currency} on {date} found'
        )

    edges = []
    for currency in currency_query:
        rate = float(currency["rate"])
        edges.append((currency["from_currency"], currency["to_currency"], rate))
        # not so sure about this
        if rate != 0:
            edges.append((currency["to_currency"], currency["from_currency"], 1 / rate))

    rate = shortest_path(edges, from_currency, to_currency)
    if rate == float("inf"):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f'No currency rate for {to_currency}/{to_currency} for {date} found'
        )
    return {"rate": rate}


def shortest_path(edges, source, sink):
    # create a weighted DAG - {node:[(cost,neighbour), ...]}
    graph = collections.defaultdict(list)
    for l, r, c in edges:
        graph[l].append((c, r))
    # create a priority queue and hash set to store visited nodes
    queue, visited = [(1, source, [])], set()
    heapq.heapify(queue)
    # traverse graph with BFS
    while queue:
        (cost, node, path) = heapq.heappop(queue)
        # visit the node if it was not visited before
        if node not in visited:
            visited.add(node)
            path = path + [node]
            # hit the sink
            if node == sink:
                return cost
            # visit neighbours
            for c, neighbour in graph[node]:
                if neighbour not in visited:
                    heapq.heappush(queue, (cost*c, neighbour, path))
    return float("inf")
