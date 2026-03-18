import grpc
from concurrent import futures
import logging

import flight_pb2
import flight_pb2_grpc

from database import SessionLocal
from models import DBFlight, DBSeatReservation, FlightStatus, ReservationStatus

class SearchFlights(flight_pb2_grpc.FlightServiceServicer):
    def SearchFlights(self, request, context):
        db = SessionLocal()
        try:
            query = db.query(DBFlight).filter(
                DBFlight.origin == request.origin,
                DBFlight.destination == request.destination,
                DBFlight.status == FlightStatus.SCHEDULED
            )
            flights = query.all()
            
            response = flight_pb2.SearchFlightResponse()
            for f in flights:
                flight_resp = flight_pb2.GetFlightResponse(
                    id=str(f.id),
                    flight_number=f.flight_number,
                    airline=f.airline,
                    origin=f.origin,
                    destination=f.destination,
                    total_seats=f.total_seats,
                    available_seats=f.available_seats,
                    price=float(f.price),
                    status=flight_pb2.FlightStatus.Value(f.status.value)
                )
                flight_resp.departure_time.FromDatetime(f.departure_time)
                flight_resp.arrival_time.FromDatetime(f.arrival_time)

                response.flights.append(flight_resp)
            return response
        
        finally:
            db.close()
