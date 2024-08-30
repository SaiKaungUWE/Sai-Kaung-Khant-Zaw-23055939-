from datetime import datetime, timedelta
from ..services.prediction_service import generate_forecasts

async def run_startup_tasks():
    today = datetime.utcnow()
    end_date = today + timedelta(days=14)  # Forecast for 14 days
    await generate_forecasts(today, end_date)
