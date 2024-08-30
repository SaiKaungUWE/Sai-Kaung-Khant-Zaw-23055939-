from motor.motor_asyncio import AsyncIOMotorClient
from datetime import datetime
from fastapi import HTTPException
import logging
from ..schemas.shift_schema import StaffShifts, Username, Shift
from pydantic import ValidationError

class DBConnector:
    client: AsyncIOMotorClient = None

    @classmethod
    def initialize(cls, uri: str):
        if cls.client is None:
            cls.client = AsyncIOMotorClient(uri)
            print("MongoDB client initialized")

    @classmethod
    def close_connection(cls):
        if cls.client is not None:
            cls.client.close()
            cls.client = None
            print("MongoDB client closed")

    '''@classmethod
    def save_forecast_results(cls, forecast_data):
        db = cls.client.scheduling_db
        return db.predict.insert_many(forecast_data)'''

    '''@classmethod
    async def get_weather_data(cls, start_date, end_date):
        db = cls.client.scheduling_db
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        try:
            cursor = db.weather.find({
                "date": {"$gte": start, "$lte": end}
            })
            return await cursor.to_list(length=None)
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))'''
    @classmethod
    async def get_weather_data(cls, start_date, end_date):
        db = cls.client.scheduling_db
        start = datetime.strptime(start_date, "%Y-%m-%d")
        end = datetime.strptime(end_date, "%Y-%m-%d")
        print(f"Querying from {start.strftime('%Y-%m-%d')} to {end.strftime('%Y-%m-%d')}")
        try:
            cursor = db.weather.find({
                "date": {"$gte": start.strftime("%Y-%m-%d"), "$lte": end.strftime("%Y-%m-%d")}
            }, {'date': 1, 'feelslike': 1, 'icon': 1})
            results = await cursor.to_list(length=None)
            print(f"Found {len(results)} results")
            return results
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
    
    @classmethod
    async def save_forecast_results(cls, forecast_data):
        db = cls.client.scheduling_db
        result = await db.forecast.insert_many(forecast_data)
        return result.inserted_ids
    
    @classmethod
    async def fetch_forecast(cls, start_date, end_date):
        logging.debug(f"Fetching forecasts between {start_date} and {end_date}")
        forecast_collection = cls.client.scheduling_db.forecast
        cursor = forecast_collection.find({"date": {"$gte": start_date, "$lte": end_date}})
        results = await cursor.to_list(length=None)
        logging.debug(f"Forecasts fetched: {results}")
        return results
    
    @classmethod
    async def fetch_forecast_for_shift(cls, start_date, end_date):
        forecast_collection = cls.client.scheduling_db.forecast
        forecasts = forecast_collection.find({
            "date": {"$gte": start_date, "$lte": end_date}
        })
        results = await forecasts.to_list(length=None)
        return results
    
    @classmethod
    async def fetch_all_staff_for_shift(cls):
        staff_collection = cls.client.scheduling_db.staff
        staff_data = await staff_collection.find().to_list(None)
        return staff_data
    
    @classmethod
    async def fetch_existing_forecast_dates(cls, start_date, end_date):
        db = cls.client.scheduling_db
        cursor = db.forecast.find(
            {"date": {"$gte": start_date, "$lte": end_date}},
            {"date": 1, "_id": 0}  # Only retrieve the date field
        )
        results = await cursor.to_list(length=None)
        return [result['date'] for result in results]  # Return a list of dates
    
    
    @classmethod
    async def fetch_all_shifts(cls):
        try:
            shift_collection = cls.client.scheduling_db.shifts
            raw_shifts = await shift_collection.find().to_list(None)  # Fetch all documents

            # Inspect the raw data
            logging.debug(f"Raw shifts data: {raw_shifts}")

            # Convert MongoDB documents to Pydantic model format
            shifts = [StaffShifts(
                username=Username(first=doc['username']['first'], second=doc['username']['second']),
                email=doc['email'],
                role=doc['role'],
                shifts=[Shift(date=shift['date'], time=shift['time']) for shift in doc.get('shift', [])]
            ) for doc in raw_shifts]

            logging.debug(f"Parsed shifts data: {shifts}")
            return shifts

        except ValidationError as e:
            logging.error(f"Pydantic validation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logging.error(f"Error fetching shifts from database: {e}")
            raise HTTPException(status_code=500, detail=str(e))
    
    @classmethod
    async def fetch_shifts_by_date_range(cls, start_date, end_date):
        shift_collection = cls.client.scheduling_db.shifts
        shifts = await shift_collection.find({
            'shift.date': {
                '$gte': start_date,
                '$lte': end_date
            }
        }).to_list(length=None)

        # Convert to Pydantic model format
        pydantic_shifts = [StaffShifts(
            username=Username(first=doc['username']['first'], second=doc['username']['second']),
            email=doc['email'],
            role=doc['role'],
            shift=[Shift(date=shift['date'], time=shift['time']) for shift in doc['shift']]
        ) for doc in shifts]

        return pydantic_shifts
    
    @classmethod
    async def save_shifts(cls, shifts):
        shift_collection = cls.client.scheduling_db.shifts
        # Remove any existing `_id` to allow MongoDB to generate a new one
        for shift in shifts:
            if '_id' in shift:
                del shift['_id']

        # Save shifts to MongoDB
        result = await shift_collection.insert_many(shifts)
        return {"message": "Shifts saved successfully", "inserted_ids": result.inserted_ids}
    
    @classmethod
    async def fetch_all_staff(cls):
        staff_collection = cls.client.scheduling_db.staff  # Adjust 'your_database_name' and 'staff' as necessary
        staff_data = await staff_collection.find().to_list(None)  # Retrieves all staff data
        return staff_data
    
    @classmethod
    async def fetch_shifts_for_staff_by_email(cls, email: str):
        try:
            shift_collection = cls.client.scheduling_db.shifts

            # Fetch the document for the specific staff member by email
            staff_doc = await shift_collection.find_one({"email": email})

            if not staff_doc:
                raise HTTPException(status_code=404, detail="Staff not found")

            # Inspect the fetched data
            logging.debug(f"Staff data for email {email}: {staff_doc}")

            # Convert MongoDB document to Pydantic model format
            staff_shifts = StaffShifts(
                username=Username(first=staff_doc['username']['first'], second=staff_doc['username']['second']),
                email=staff_doc['email'],
                role=staff_doc.get('role', 'Unknown Role'),
                shifts=[Shift(date=shift['date'], time=shift['time']) for shift in staff_doc.get('shift', [])]
            )

            logging.debug(f"Parsed staff shifts: {staff_shifts}")
            return staff_shifts

        except ValidationError as e:
            logging.error(f"Pydantic validation error: {e}")
            raise HTTPException(status_code=500, detail=str(e))
        except Exception as e:
            logging.error(f"Error fetching shifts for staff from database: {e}")
            raise HTTPException(status_code=500, detail=str(e))







def get_database():
    if DBConnector.client is not None:
        return DBConnector.client["scheduling_db"]
    else:
        raise Exception("Database client is not initialized")

# Dependency to inject the database session
def get_database_dependency():
    db = get_database()
    try:
        yield db
    finally:
        # Remove the db.client.close() to prevent closing the client
        pass
