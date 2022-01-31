from flask import Blueprint
from .views.currency_view import CurrenciesView, CurrencyView
from .views.rate_view import RatesView, RateView

currencies_view = CurrenciesView().as_view('currencies_view')
currency_view = CurrencyView().as_view('currency_view')
rate_view = RateView().as_view('rate_view')
rates_view = RatesView().as_view('rates_view')

rate_api = Blueprint('rate_api', __name__, url_prefix='/api/v1')
currency_api = Blueprint('currency_api', __name__, url_prefix='/api/v1')

# currencies
currency_api.add_url_rule('/currencies', view_func=currencies_view)
currency_api.add_url_rule('/currencies/<int:record_id>', view_func=currency_view)
# rates
rate_api.add_url_rule('/rates', view_func=rates_view)
rate_api.add_url_rule('/rates/<int:record_id>', view_func=rate_view)
