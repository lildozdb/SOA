from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
import grpc
import uuid

from database import get_db
from models import DBBooking, BookingStatus
from schemas import BookingCreate

import flight_pb2
import flight_pb2_grpc

app = FastAPI(title="Booking Service")

channel = grpc.insecure_channel('flight_service:50051')
flight_client = flight_pb2_grpc.FlightServiceStub(channel)

@app.post("/api/v1/bookings/")
def create_booking(booking: BookingCreate, db: Session = Depends(get_db)):
    booking_id = uuid.uuid4()
    try:
        grpc_request = flight_pb2.ReserveSeatsRequest(
            flight_id=str(booking.flight_id),
            seat_count=booking.seat_count,
            booking_id=str(booking_id)
        )
        grpc_response = flight_client.ReserveSeats(grpc_request)
        
        if grpc_response.status != flight_pb2.ReservationStatus.ACTIVE:
            raise HTTPException(status_code=400, detail="Мест нет")
            
    except grpc.RpcError as e:
        raise HTTPException(status_code=500, detail=f"Ошибка gRPC: {e.details()}")

    try:
        new_booking = DBBooking(
            id=booking_id,
            user_id=booking.user_id,
            flight_id=booking.flight_id,
            passenger_name=booking.passenger_name,
            passenger_email=booking.passenger_email,
            seat_count=booking.seat_count,
            total_price=booking.total_price,
            status=BookingStatus.CONFIRMED
        )
        db.add(new_booking)
        db.commit()
        
    except Exception as e:
        print(f"ОШИБКА СОХРАНЕНИЯ: {e}. Запускаем откат во Flight Service...")
        db.rollback()
        
        rollback_request = flight_pb2.ReleaseReservationRequest(booking_id=str(booking_id))
        flight_client.ReleaseReservation(rollback_request)
        
        raise HTTPException(
            status_code=500, 
            detail="Ошибка сохранения брони. Места во Flight Service успешно возвращены (Saga)."
        )
    
    return {"message": "Успешно!", "booking_id": new_booking.id}
