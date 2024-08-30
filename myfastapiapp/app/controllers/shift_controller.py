from fastapi import APIRouter, HTTPException
from ..schemas.shift_schema import ShiftResponse, StaffShifts
from ..services.shift_service import generate_shifts
from ..dependencies.database_connector import DBConnector
from typing import List
import logging
from datetime import datetime, timedelta

router = APIRouter()

@router.post("/shifts/generate", response_model=ShiftResponse)
async def generate_shift_endpoint():
    try:
        result = await generate_shifts()  # Assuming this returns a dictionary with a "shifts" key
        shifts = result.get('shifts', [])
        
        # Ensure the shifts are formatted correctly
        if not isinstance(shifts, list):
            raise ValueError("Expected 'shifts' to be a list.")
        
        structured_shifts = ShiftResponse(message="Shifts generated successfully", staff_shifts=shifts)
        
        return structured_shifts
    except Exception as e:
        logging.error(f"Failed to generate shifts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/shifts/", response_model=List[StaffShifts])
async def get_all_shifts():
    try:
        shifts = await DBConnector.fetch_all_shifts()
        return shifts
    except Exception as e:
        logging.error(f"Failed to fetch shifts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
    
@router.get("/shifts/weekly")
async def get_weekly_shifts(start_date: str):
    try:
        start = datetime.strptime(start_date, '%Y-%m-%d')
        end = start + timedelta(days=6)

        # Fetch shifts within a specific date range
        shifts = await DBConnector.fetch_shifts_by_date_range(start.isoformat(), end.isoformat())
        return shifts
    except Exception as e:
        logging.error(f"Failed to fetch weekly shifts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/staff/shifts/{email}", response_model=StaffShifts)
async def get_staff_shifts(email: str):
    try:
        staff_shifts = await DBConnector.fetch_shifts_for_staff_by_email(email)
        if not staff_shifts:
            raise HTTPException(status_code=404, detail="Staff not found")
        return staff_shifts
    except Exception as e:
        logging.error(f"Failed to fetch staff shifts: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
