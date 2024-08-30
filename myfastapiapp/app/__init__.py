from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from .controllers.prediction_controller import router as prediction_router
from .controllers.shift_controller import router as shift_router
from .controllers.staff_controller import router as staff_router
from .dependencies.database_connector import DBConnector, get_database_dependency
from fastapi.middleware.cors import CORSMiddleware
from .services.prediction_service import generate_and_save_forecasts


app = FastAPI()

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=422,
        content={"detail": exc.errors(), "body": exc.body},
    )

app.include_router(prediction_router)
app.include_router(shift_router)
app.include_router(staff_router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

@app.get("/")
def read_root():
    return {"message": "Welcome to my FastAPI application!"}

@app.on_event("startup")
async def startup_db_client():
    DBConnector.initialize("mongodb://localhost:27017")  # Ensure this URI is correct or updated as needed
    await generate_and_save_forecasts()

@app.on_event("shutdown")
def shutdown_db_client():
    DBConnector.close_connection()
