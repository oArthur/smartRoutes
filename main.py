from rotas import otimizar_rotas
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from Key import API_KEY
import googlemaps
import json


gmaps = googlemaps.Client(key=API_KEY)
with open('config.json') as file:
    data = json.load(file)


if __name__ == '__main__':
    #otimizar_rotas(data)
    factory_location = data['factory']['coordinates']
    truck_capacity = [truck['capacity'] for truck in data['trucks']]
    delivery_locations = [delivery['coordinates'] for delivery in data['deliveries']]
    delivery_quantities = [delivery['quantity'] for delivery in data['deliveries']]

    lista_distancias = []
    for i in range(len(delivery_locations)):
        print(f"Ponto Nº:{i}.")
        print(f"Partida: {factory_location}\nDestino: {delivery_locations[i]}")
        directions_result = gmaps.directions(factory_location,delivery_locations[i] , mode="driving")
        distancia = directions_result[0]['legs'][0]['distance']['text']
        lista_distancias.append(distancia)


    print(lista_distancias)

