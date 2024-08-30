from pydantic import BaseModel, EmailStr, Field
from typing import List, Optional

class StaffName(BaseModel):
    first: str
    second: str

class StaffRoles(BaseModel):
    roles: List[str]
    available_dates: List[str]
    available_hours: int

class StaffBase(BaseModel):
    username: StaffName
    email: EmailStr

class StaffCreate(StaffBase):
    password: str
    user_data: StaffRoles

class StaffDisplay(StaffBase):
    id: str = Field(None, alias='_id')
    user_data: StaffRoles

    class Config:
        json_schema_extra  = {
            "example": {
                "username": {
                    "first": "Sai",
                    "second": "Zaw"
                },
                "email": "newuser@example.com",
                "password": "your password",
                "user_data": {
                    "roles": ["Kitchen Porter", "Fryer"],
                    "available_dates": ["1", "3", "6"],
                    "available_hours": 20
                }
            }
        }

class StaffUpdate(StaffBase):
    username: Optional[StaffName] = None
    email: Optional[EmailStr] = None
    user_data: Optional[StaffRoles] = None

class StaffInDB(StaffBase):
    hashed_password: str
    user_data: StaffRoles
