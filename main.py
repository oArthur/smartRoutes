from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from Key import API_KEY
import googlemaps
import json


# Carrega os dados do arquivo JSON
with open('config.json') as file:
    data = json.load(file)

# Inicializa o cliente da API do Google Maps
gmaps = googlemaps.Client(key=API_KEY)

# Inicializa o otimizador do OR-Tools
def optimize_routes(data):
    # Extrai os dados do arquivo JSON
    factory_location = data['factory']['coordinates']
    truck_capacity = [truck['capacity'] for truck in data['trucks']]
    delivery_locations = [delivery['coordinates'] for delivery in data['deliveries']]
    delivery_quantities = [delivery['quantity'] for delivery in data['deliveries']]

    # Calcula a matriz de distâncias entre os locais usando a API do Google Maps
    distance_matrix = []
    for from_loc in [factory_location] + delivery_locations:
        row = []
        for to_loc in [factory_location] + delivery_locations:
            directions_result = gmaps.directions(from_loc, to_loc, mode="driving")
            distance = directions_result[0]['legs'][0]['distance']['value']
            row.append(distance)
        distance_matrix.append(row)

    # Configura o problema de roteamento
    num_locations = len(delivery_locations) + 1
    num_vehicles = len(truck_capacity)
    depot = 0

    routing = pywrapcp.RoutingModel(num_locations, num_vehicles, depot)
    transit_callback_index = routing.RegisterTransitCallback(lambda from_index, to_index: distance_matrix[from_index][to_index])
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    # Configura as restrições
    for vehicle_id in range(num_vehicles):
        capacity_callback_index = routing.RegisterUnaryTransitCallback(lambda index: delivery_quantities[index])
        routing.AddDimensionWithVehicleCapacity(
            capacity_callback_index,
            0,  # no slack
            truck_capacity[vehicle_id],  # vehicle maximum capacity
            True,  # start cumul to zero
            f"capacity_{vehicle_id}"
        )

    # Executa a busca pela solução
    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC
    solution = routing.SolveWithParameters(search_parameters)

    # Verifica se foi encontrada uma solução válida
    if solution:
        # Extrai as informações da solução
        routes = []
        for vehicle_id in range(num_vehicles):
            index = routing.Start(vehicle_id)
            route = [routing.IndexToNode(index)]
            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                route.append(routing.IndexToNode(index))
            routes.append(route)

        # Calcula as datas de saída dos caminhões
        travel_times = []
        for route in routes:
            travel_time = 0
            for i in range(len(route) - 1):
                from_loc = delivery_locations[route[i]]
                to_loc = delivery_locations[route[i + 1]]
                directions_result = gmaps.directions(from_loc, to_loc, mode="driving")