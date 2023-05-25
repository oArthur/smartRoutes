from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from Key import API_KEY
import googlemaps

def otimizar_rotas(data):
    gmaps = googlemaps.Client(key=API_KEY) # Inicializa o cliente da API do Google Maps

    # Extrai os dados do arquivo JSON
    factory_location = data['factory']['coordinates']
    truck_capacity = [truck['capacity'] for truck in data['trucks']]
    delivery_locations = [delivery['coordinates'] for delivery in data['deliveries']]
    delivery_quantities = [delivery['quantity'] for delivery in data['deliveries']]

    # Calcula as distâncias entre os locais usando a API do Google Maps, lendo ponto a ponto das localizaces fornecidads pelo json.
    lista_distancias = []
    for i in range(len(delivery_locations)):
        #print(f"Ponto Nº:{i}.")
        #print(f"Partida: {factory_location}\nDestino: {delivery_locations[i]}")
        directions_result = gmaps.directions(factory_location, delivery_locations[i], mode="driving")
        distancia = directions_result[0]['legs'][0]['distance']['value']
        lista_distancias.append(distancia)

    # Configura o problema de roteamento
    num_locations = len(delivery_locations) + 1
    num_vehicles = len(truck_capacity)
    depot = 0

    routing = pywrapcp.RoutingModel(num_locations, num_vehicles, depot)
    transit_callback_index = routing.RegisterTransitCallback(lambda from_index, to_index: lista_distancias[from_index][to_index])
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
