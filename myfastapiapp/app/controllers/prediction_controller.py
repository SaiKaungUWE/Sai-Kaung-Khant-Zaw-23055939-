from fastapi import APIRouter, Depends, HTTPException
from ..schemas.prediction_schema import ForecastResponse, Forecast
from ..services.prediction_service import generate_and_save_forecasts
from ..dependencies.database_connector import get_database_dependency, DBConnector
from datetime import datetime
from typing import List

router = APIRouter()

@router.post("/forecast/generate")
async def generate_forecast(db=Depends(get_database_dependency)):
    try:
        forecast_data = await generate_and_save_forecasts()
        return {"message": "Forecast generation successful", "data": forecast_data}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to generate forecast: {str(e)}")

@router.get("/forecast/", response_model=ForecastResponse)
async def read_all_forecasts(db=Depends(get_database_dependency)):
    try:
        forecast_data = await db["forecast"].find().to_list(None)
        return ForecastResponse(forecasts=forecast_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to retrieve forecasts: {str(e)}")
    
@router.get("/forecast/{start_date}/{end_date}", response_model=List[Forecast])
async def fetch_forecast(start_date: str, end_date: str):
    start = datetime.strptime(start_date, "%Y-%m-%d")
    end = datetime.strptime(end_date, "%Y-%m-%d")
    try:
        forecast_data = await DBConnector.fetch_forecast(start.strftime("%Y-%m-%d"), end.strftime("%Y-%m-%d"))
        return [Forecast(date=item['date'], forecast=item['forecast']) for item in forecast_data]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
