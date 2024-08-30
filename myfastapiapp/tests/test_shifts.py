from fastapi import APIRouter, Depends, HTTPException
from ..schemas.shift_schema import ShiftResponse, ShiftRequest
from ..services.shift_service import generate_shifts
from ..dependencies.database_connector import get_database_dependency
from typing import List
import logging

router = APIRouter()

@router.post("/shifts/generate", response_model=ShiftResponse)
async def generate_shift_endpoint(db=Depends(get_database_dependency)):
    try:
        shifts = await generate_shifts()
        if not shifts:  # Handle None or empty list explicitly
            shifts = []
        print("Generated shifts data:", shifts)  # Debugging line to inspect the shifts data
        return {"message": "Shifts generated successfully", "shifts": shifts}
    except Exception as e:
        logging.error(f"Failed to generate shifts: {e}", exc_info=True)
        print("Error generating shifts:", str(e))  # More detailed error logging
        raise HTTPException(status_code=500, detail=str(e))


logger = logging.getLogger(__name__)

@router.get("/shifts/", response_model=List[ShiftResponse])
async def get_all_shifts(db=Depends(get_database_dependency)):
    try:
        shifts = await db.fetch_all_shifts()
        logger.debug(f"Shifts fetched: {shifts}")
        if not shifts:
            shifts = []
        return {"message": "Shifts retrieved successfully", "shifts": shifts}
    except Exception as e:
        logger.error(f"Failed to fetch shifts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
