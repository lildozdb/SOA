import uuid
from datetime import datetime, timedelta
from database import SessionLocal
from models import DBFlight, FlightStatus

def seed_flight():
    db = SessionLocal()
    
    new_flight = DBFlight(
        id=uuid.uuid4(),
        flight_number="SU-123",
        airline="Aeroflot",
        origin="MOW",
        destination="LED",
        departure_time=datetime.utcnow() + timedelta(days=1),
        arrival_time=datetime.utcnow() + timedelta(days=1, hours=1, minutes=30),
        total_seats=150,
        available_seats=150,
        price=5000.00,
        status=FlightStatus.SCHEDULED
    )
    
    db.add(new_flight)
    db.commit()
    print("Тестовый рейс успешно добавлен в базу данных!")
    print(f"ID РЕЙСА: {new_flight.id}\n")
    db.close()

if __name__ == "__main__":
    seed_flight()