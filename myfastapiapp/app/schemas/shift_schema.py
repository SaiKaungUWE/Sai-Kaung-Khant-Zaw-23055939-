from pydantic import BaseModel
from typing import List

class Shift(BaseModel):
    date: str
    time: str

class Username(BaseModel):
    first: str
    second: str

class StaffShifts(BaseModel):
    username: Username
    email: str
    role: str
    shifts: List[Shift]  # Updated to match the generated data

class ShiftResponse(BaseModel):
    message: str
    staff_shifts: List[StaffShifts]  # Updated to match the response structure
