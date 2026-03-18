from pydantic import BaseModel
import uuid

class BookingCreate(BaseModel):
    user_id: str
    flight_id: uuid.UUID
    passenger_name: str
    passenger_email: str
    seat_count: int
    total_price: float