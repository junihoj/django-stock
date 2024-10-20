# pylint: skip-file
import requests
import numpy as np
from django.conf import settings
from django.http import JsonResponse, FileResponse
from .models import StockData, StockPrediction
from datetime import datetime
import joblib
import matplotlib.pyplot as plt

from io import BytesIO

API_URL = "https://www.alphavantage.co/query"


def fetch_stock_data(request, symbol):
    params = {
        "function": "TIME_SERIES_DAILY",
        "symbol": symbol,
        "apikey": settings.ALPHA_VANTAGE_API_KEY,
    }
    response = requests.get(API_URL, params=params)

    if response.status_code == 200:
        data = response.json().get("Time Series (Daily)", {})
        for date_str, price_data in data.items():
            date = datetime.strptime(date_str, "%Y-%m-%d").date()

            StockData.objects.update_or_create(
                symbol=symbol,
                date=date,
                defaults={
                    "open_price": price_data["1. open"],
                    "close_price": price_data["4. close"],
                    "high_price": price_data["2. high"],
                    "low_price": price_data["3. low"],
                    "volume": price_data["5. volume"],
                },
            )
        return JsonResponse(
            {"status": "success", "message": "Data fetched successfully"}
        )
    return JsonResponse({"status": "error", "message": "Failed to fetch data"})


def backtest(request, symbol, investment, buy_moving_avg=50, sell_moving_avg=200):
    data = StockData.objects.filter(symbol=symbol).order_by("date")
    if not data.exists():
        return JsonResponse({"status": "error", "message": "No data available"})

    prices = np.array([float(d.close_price) for d in data])
    moving_avg_buy = np.convolve(
        prices, np.ones(buy_moving_avg) / buy_moving_avg, mode="valid"
    )
    moving_avg_sell = np.convolve(
        prices, np.ones(sell_moving_avg) / sell_moving_avg, mode="valid"
    )

    # Implement buy/sell logic
    position = 0  # 0 means no position, 1 means holding stock
    trades = []
    balance = investment

    for i in range(len(moving_avg_buy)):
        if position == 0 and prices[i] < moving_avg_buy[i]:
            position = 1
            buy_price = prices[i]
            trades.append(("buy", buy_price))
        elif position == 1 and prices[i] > moving_avg_sell[i]:
            position = 0
            sell_price = prices[i]
            balance += sell_price - buy_price  # update balance after sell
            trades.append(("sell", sell_price))

    total_return = balance - investment
    return JsonResponse(
        {"status": "success", "trades": trades, "total_return": total_return}
    )


def predict_stock(request, symbol, days=30):
    model = joblib.load("./model.pkl")
    data = StockData.objects.filter(symbol=symbol).order_by("-date")[:days]

    # Prepare data for the model
    prices = np.array([float(d.close_price) for d in data])
    predictions = model.predict(prices.reshape(-1, 1))

    for i, prediction in enumerate(predictions):
        StockPrediction.objects.create(
            symbol=symbol, date=data[i].date, predicted_price=prediction
        )

    return JsonResponse({"status": "success", "predictions": predictions.tolist()})


def generate_report_view(request, symbol):
    stock_data = StockData.objects.filter(symbol=symbol).order_by("date")
    predictions = StockPrediction.objects.filter(symbol=symbol).order_by("date")

    # Generate comparison plot
    dates = [data.date for data in stock_data]
    actuals = [data.close_price for data in stock_data]
    predicted = [pred.predicted_price for pred in predictions]

    plt.plot(dates, actuals, label="Actual")
    plt.plot(dates, predicted, label="Predicted", linestyle="--")

    plt.legend()
    plt.title(f"Stock Prices for {symbol}")
    plt.xlabel("Date")
    plt.ylabel("Price")

    # Save to PDF
    buffer = BytesIO()
    plt.savefig(buffer, format="pdf")
    buffer.seek(0)

    return FileResponse(buffer, as_attachment=True, filename="report.pdf")


def health_check(request):
    return JsonResponse({"HEALTH": "Oks"})
