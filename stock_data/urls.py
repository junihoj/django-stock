from django.urls import path
from .views import fetch_stock_data, backtest, health_check

urlpatterns = [
    path("", health_check, name="health-check"),
    path("fetch-stock/<str:symbol>/", fetch_stock_data, name="fetch_stock_data"),
    path("backtest/<str:symbol>/<int:investment>/", backtest, name="backtest"),
]
