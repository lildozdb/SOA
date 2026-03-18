import grpc
import flight_pb2
import flight_pb2_grpc

def run():
    print("Подключаемся к серверу на порту 50051")
    with grpc.insecure_channel('localhost:50051') as channel:
        stub = flight_pb2_grpc.FlightServiceStub(channel)
        print("Отпрпавляем запрос на поиск рейсов")
        request = flight_pb2.SearchFlightsRequest(
            origin="MOW",
            destination="LED",
            date="2026-03-20"
        )

        try:
            response = stub.SearchFlights(request)
            print("Ответ получен")
            print(response)
            print("Ответ пустой")
        except grpc.RpcError as e:
            print(f"Ошибка grpc: {e.code()} - {e.details}")
    
if __name__ == '__main__':
    run()