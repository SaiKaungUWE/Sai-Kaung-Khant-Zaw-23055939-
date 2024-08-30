from pydantic import BaseModel, Field
from typing import List

class Forecast(BaseModel):
    date: str = Field(..., example="2024-08-12")
    forecast: float = Field(..., example=2500.0)

class ForecastResponse(BaseModel):
    forecasts: List[Forecast]

    class Config:
        json_schema_extra = {
            "example": {
                "forecasts": [
                    {"date": "2024/08/12", "forecast": 2500.0},
                    {"date": "2024/08/13", "forecast": 2600.0},
                    {"date": "2024/08/14", "forecast": 2400.0},
                    {"date": "2024/08/15", "forecast": 2300.0},
                    {"date": "2024/08/16", "forecast": 2200.0},
                    {"date": "2024/08/17", "forecast": 2100.0},
                    {"date": "2024/08/18", "forecast": 2000.0}
                ]
            }
        }
