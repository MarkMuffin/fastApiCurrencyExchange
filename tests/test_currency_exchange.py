import pytest
from fastapi import HTTPException

from app.currency_exchange import get_all_history_currency_pair, get_rate_for_date
from app.database import SessionLocal


class TestCurrencyExchange:

    session = SessionLocal()

    def test_get_all_history_data(self):
        history = get_all_history_currency_pair(from_currency="EUR", to_currency="USD", db=self.session)
        assert history

    def test_get_wrong_pair_history_data(self):
        with pytest.raises(HTTPException):
            history = get_all_history_currency_pair(from_currency="IDDQ", to_currency="MMM", db=self.session)

    def test_get_reverse_history_data(self):
        history = get_all_history_currency_pair(from_currency="USD", to_currency="EUR", db=self.session)
        assert history

    def test_get_rate_simple(self):
        rate = get_rate_for_date(from_currency="EUR", to_currency="USD", date="2020-01-03", db=self.session)
        assert rate["rate"] == 1.1165

    def test_get_rate_with_graf(self):
        rate = get_rate_for_date(from_currency="NZD", to_currency="JPY", date="2020-01-03", db=self.session)
        assert rate["rate"] == 72.0042095759964

    def test_get_rate_invalid_data(self):
        with pytest.raises(HTTPException):
            rate = get_rate_for_date(from_currency="EUR", to_currency="USD", date="9999-01-03", db=self.session)

    def test_fet_rate_no_currency(self):
        with pytest.raises(HTTPException):
            rate = get_rate_for_date(from_currency="NZD", to_currency="RUB", date="2020-01-03", db=self.session)
