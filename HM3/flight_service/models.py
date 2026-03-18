import uuid
from sqlalchemy import Column, String, Integer, Numeric, DateTime, Enum, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import enum
from database import Base

class FlightStatus(enum.Enum):
    SCHEDULED = "SCHEDULED"
    DEPARTED = "DEPARTED"
    CANCELLED = "CANCELLED"
    COMPLETED = "COMPLETED"

class ReservationStatus(enum.Enum):
    ACTIVE = "ACTIVE"
    RELEASED = "RELEASED"
    EXPIRED = "EXPIRED"

class DBFlight(Base):
    __tablename__ = "flights"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_number = Column(String(50), nullable=False)
    airline = Column(String(100), nullable=False)
    origin = Column(String(10), nullable=False)
    destination = Column(String(10), nullable=False)
    departure_time = Column(DateTime, nullable=False)
    arrival_time = Column(DateTime, nullable=False)
    total_seats = Column(Integer, nullable=False)
    available_seats = Column(Integer, nullable=False)
    price = Column(Numeric(12,2), nullable=False)
    status = Column(Enum(FlightStatus, name="flight_status"), default=FlightStatus.SCHEDULED, nullable=False)

class DBSeatReservation(Base):
    __tablename__ = "seat_reservations"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    flight_id = Column(UUID(as_uuid=True), ForeignKey("flights.id"), nullable=False)
    booking_id = Column(UUID(as_uuid=True), nullable=False)
    seat_count = Column(Integer, nullable=False)
    status = Column(Enum(ReservationStatus, name="reservation_status"), default=ReservationStatus.ACTIVE, nullable=False)
    
