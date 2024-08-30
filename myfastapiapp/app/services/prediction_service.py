import joblib
from pathlib import Path
import pandas as pd
from ..dependencies.database_connector import DBConnector
from datetime import datetime, timedelta

MODEL_PATH = Path(__file__).resolve().parent.parent / "prophet_model" / "for_fastapi_enhanced_prophet_model.pkl"
model = joblib.load(MODEL_PATH)

def determine_staff_needed(forecast):
    # Determine the number of staff needed based on the forecast value
    if forecast <= 2038:
        return 3
    elif forecast <= 3038:
        return 4
    elif forecast <= 4038:
        return 4
    elif forecast <= 6038:
        return 5
    elif forecast <= 8038:
        return 6
    else:
        return 6

async def generate_and_save_forecasts():
    today = datetime.utcnow()
    two_weeks_later = today + timedelta(days=13)
    
    existing_dates = await DBConnector.fetch_existing_forecast_dates(today.strftime("%Y-%m-%d"), two_weeks_later.strftime("%Y-%m-%d"))
    existing_dates_set = set(existing_dates)
    
    weather_data = await DBConnector.get_weather_data(today.strftime("%Y-%m-%d"), two_weeks_later.strftime("%Y-%m-%d"))
    if not weather_data:
        print("No weather data available for the specified range.")
        return
    new_weather_data = [data for data in weather_data if data['date'] not in existing_dates_set]

    if not new_weather_data:
        print("All forecasts are up to date.")
        return

    input_data = pd.DataFrame({
        'ds': pd.to_datetime([item['date'] for item in new_weather_data], format="%Y-%m-%d"),
        'temperature': [item['feelslike'] for item in new_weather_data],
        'icon': [item['icon'] for item in new_weather_data]
    })

    # Convert icon to dummy variables
    icon_dummies = pd.get_dummies(input_data['icon'])
    expected_icons = ['clear-day', 'cloudy', 'partly-cloudy-day', 'rain', 'snow']  # Add other categories as necessary
    for icon in expected_icons:
        if icon not in icon_dummies.columns:
            icon_dummies[icon] = 0
    input_data = pd.concat([input_data.drop('icon', axis=1), icon_dummies], axis=1)

    forecast = model.predict(input_data)
    forecast_data = [{'date': row['ds'].strftime("%Y-%m-%d"), 
                      'forecast': round(row['yhat']),
                      'staff_needed': determine_staff_needed(round(row['yhat']))
                      } for index, row in forecast.iterrows()]
    
    await DBConnector.save_forecast_results(forecast_data)
    print("Forecasts saved to the database.")
