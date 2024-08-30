from fastapi import APIRouter, Depends
from ..schemas.staff_schema import StaffCreate, StaffDisplay, StaffUpdate
from ..services.staff_service import create_staff, get_staff, update_staff, delete_staff
from ..dependencies.database_connector import get_database_dependency
from typing import List

router = APIRouter()

@router.post("/staff/", response_model=StaffDisplay)
async def create_staff_endpoint(staff: StaffCreate, db=Depends(get_database_dependency)):
    return await create_staff(db, staff)

@router.get("/staff/{staff_id}", response_model=StaffDisplay)
async def read_staff(staff_id: str, db=Depends(get_database_dependency)):
    return await get_staff(db, staff_id)

@router.put("/staff/{staff_id}", response_model=StaffDisplay)
async def update_staff_endpoint(staff_id: str, staff: StaffUpdate, db=Depends(get_database_dependency)):
    return await update_staff(db, staff_id, staff)

@router.delete("/staff/{staff_id}")
async def delete_staff_endpoint(staff_id: str, db=Depends(get_database_dependency)):
    return await delete_staff(db, staff_id)

@router.get("/staff/", response_model=List[StaffDisplay])
async def read_all_staff(db=Depends(get_database_dependency)):
    staff_collection = db["staff"]
    staff_list = await staff_collection.find().to_list(None)
    for staff in staff_list:
        staff["_id"] = str(staff["_id"])
    return staff_list
