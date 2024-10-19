from django.urls import path
from .views import fetch_stock_data, backtest

urlpatterns = [
    path("fetch-stock/<str:symbol>/", fetch_stock_data, name="fetch_stock_data"),
    path("backtest/<str:symbol>/<int:investment>/", backtest, name="backtest"),
]
