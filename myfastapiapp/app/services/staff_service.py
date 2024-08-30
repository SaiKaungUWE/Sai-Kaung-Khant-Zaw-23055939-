from ..schemas.staff_schema import StaffCreate,StaffUpdate
from ..dependencies.database_connector import get_database_dependency
from bson import ObjectId
from ..utilities.hash_utils import hash_password
import traceback

async def create_staff(db, staff: StaffCreate):
    staff_collection = db["staff"]
    # Ensuring we convert Pydantic model to dict properly and explicitly reordering fields
    staff_data = {
        "username": staff.username.dict(),
        "email": staff.email,
        "hashed_password": hash_password(staff.password),  # Hash the password and insert it here
        "user_data": staff.user_data.dict()
    }

    result = await staff_collection.insert_one(staff_data)
    staff_data['_id'] = str(result.inserted_id)  # Convert ObjectId to string
    return {"id": staff_data['_id'], **staff_data}

async def get_staff(db, staff_id: str):
    staff_collection = db["staff"]
    staff = await staff_collection.find_one({"_id": ObjectId(staff_id)})
    if staff:
        staff["_id"] = str(staff["_id"])
    return staff

async def update_staff(db, staff_id: str, update_data: StaffUpdate):
    staff_collection = db["staff"]
    update_dict = {k: v for k, v in update_data.dict(exclude_unset=True).items() if v is not None}
    if update_dict:
        await staff_collection.update_one({"_id": ObjectId(staff_id)}, {"$set": update_dict})
    return await get_staff(db, staff_id)


async def delete_staff(db, staff_id: str):
    staff_collection = db["staff"]
    await staff_collection.delete_one({"_id": ObjectId(staff_id)})
    return {"message": "Staff deleted"}

async def get_all_staff(db):
    staff_collection = db["staff"]
    staff_list = await staff_collection.find().to_list(None)  # Retrieves all documents
    return staff_list  # Each item needs to be converted to dict if not automatically handled

