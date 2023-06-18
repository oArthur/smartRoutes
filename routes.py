# novo exemplo
import json
import googlemaps
from ortools.constraint_solver import routing_enums_pb2
from ortools.constraint_solver import pywrapcp
from Key import API_KEY
import datetime


with open('config.json') as file:
    config = json.load(file)
def create_data_model(factory, trucks, deliveries):
    data = {}
    data['locations'] = [factory] + deliveries
    data['num_locations'] = len(data['locations'])
    data['num_trucks'] = len(trucks)
    data['vehicle_capacities'] = [truck['capacity'] for truck in trucks]
    data['demands'] = [0] + [delivery['quantity'] for delivery in deliveries]
    data['depot'] = 0
    data['departure_date'] = [factory['departure_date']]
    return data


def create_distance_matrix(gmaps, data):
    distance_matrix = [[0] * data['num_locations'] for _ in range(data['num_locations'])]
    for i in range(data['num_locations']):
        for j in range(data['num_locations']):
            origin = data['locations'][i]['coordinates']
            destination = data['locations'][j]['coordinates']
            result = gmaps.distance_matrix(origin, destination, mode='driving')
            distance = result['rows'][0]['elements'][0]['distance']['value']
            distance_matrix[i][j] = distance
    return distance_matrix


def optimize_routes(data):
    manager = pywrapcp.RoutingIndexManager(data['num_locations'], data['num_trucks'], data['depot'])
    routing = pywrapcp.RoutingModel(manager)

    def distance_callback(from_index, to_index):  # from_index, to_index
        from_node = manager.IndexToNode(from_index)
        to_node = manager.IndexToNode(to_index)
        return data['distance_matrix'][from_node][to_node]

    transit_callback_index = routing.RegisterTransitCallback(distance_callback)
    # transit_callback_index = routing.RegisterTransitCallback(
    # lambda from_index, to_index: data['distance_matrix'][from_index][to_index])
    routing.SetArcCostEvaluatorOfAllVehicles(transit_callback_index)

    def demand_callback(from_index):
        """Returns the demand of the node."""
        # Convert from routing variable Index to demands NodeIndex.
        from_node = manager.IndexToNode(from_index)
        return data['demands'][from_node]

    demand_callback_index = routing.RegisterUnaryTransitCallback(demand_callback)
    routing.AddDimensionWithVehicleCapacity(
        demand_callback_index,
        0,  # no slack
        data['vehicle_capacities'],  # vehicle maximum capacity
        True,  # start cumul to zero
        'capacity_')

    search_parameters = pywrapcp.DefaultRoutingSearchParameters()
    search_parameters.first_solution_strategy = (
        routing_enums_pb2.FirstSolutionStrategy.PATH_CHEAPEST_ARC)

    solution = routing.SolveWithParameters(search_parameters)

    if solution:
        routes = []
        for i in range(data['num_trucks']):
            index = routing.Start(i)
            route = [manager.IndexToNode(index)]
            while not routing.IsEnd(index):
                index = solution.Value(routing.NextVar(index))
                route.append(manager.IndexToNode(index))
            routes.append(route)
        return routes
    else:
        return None


def calculate_departure_dates(routes, data, gmaps):
    departure_dates = []
    #str_date = data['departure_date'][0]  # pega a data de saida dos caminhoes do json.
    date_now = datetime.datetime.now()
    for i, route in enumerate(routes):
        total_duration = 0
        for j in range(len(route) - 1):
            origin = data['locations'][route[j]]['coordinates']
            destination = data['locations'][route[j + 1]]['coordinates']
            result = gmaps.directions(origin, destination, mode='driving')
            duration = result[0]['legs'][0]['duration']['value']
            total_duration += duration

        #return_date = datetime.datetime.strptime(str_date, '%Y-%m-%d').date()
        duracao_formatada = datetime.timedelta(seconds=total_duration)
        #departure_date = return_date - duracao_formatada
        departure_date = date_now - duracao_formatada
        # Condiciona as datas de saida serem a partir do dia solicitado.
        departure_date += datetime.timedelta(days=1)
        departure_dates.append(departure_date)
    return departure_dates

def gerador_saida_json(routes, departure_dates):
    output_data = []
    trucks = config['trucks']
    deliveries = config['deliveries']

    for i, route in enumerate(routes):
        truck = trucks[i]
        departure_date = departure_dates[i]
        deliveries_list = []

        for i, location in enumerate(route):
            if location == 0:
                if i == len(route) - 1:
                    deliveries_list.append("Fabrica")
            else:
                delivery = deliveries[location - 1]
                deliveries_list.append({
                    "local": delivery['location'],
                    "quantidade": delivery['quantity']
                })

        output_data.append({
            "caminhao": i ,
            "capacidade": truck['capacity'],
            "data_partida": departure_date.strftime('%Y-%m-%d %H:%M:%S'),
            "entregas": deliveries_list
        })

    with open('output.json', 'w') as file:
        json.dump(output_data, file, indent=4)


def main():
    # Extract configuration data
    factory = config['factory']
    trucks = config['trucks']
    deliveries = config['deliveries']

    # Create Google Maps client
    gmaps = googlemaps.Client(key=API_KEY) #API Key

    # Create data model
    data = create_data_model(factory, trucks, deliveries)

    # Create distance matrix
    data['distance_matrix'] = create_distance_matrix(gmaps, data)

    # Optimize routes
    routes = optimize_routes(data)
    print(routes)
    if routes is None:
        print("Não foi possível planejar a entrega com os caminhões disponíveis.")
    else:
        # Calculate departure dates
        # data['departure_date'] = 0  # Insira a data de retorno dos caminhões aqui, no lugar do 0 (apenas com numerais)
        departure_dates = calculate_departure_dates(routes, data, gmaps)

        # Print routes and departure dates
        for i, route in enumerate(routes):
            truck = trucks[i]
            departure_date = departure_dates[i]
            print(f"Rota para o Caminhão {i+1} (Capacidade: {truck['capacity']}):")
            print(f"Data de Partida: {departure_date.strftime('%Y-%m-%d %H:%M:%S')}")
            print("Entregas:")
            for i, location in enumerate(route):
                if location == 0:
                    if i == len(route) - 1:
                        print("Fábrica\n")
                    else:
                        print(f"Fábrica -> ", end='')
                else:
                    delivery = deliveries[location - 1]
                    print(f"{delivery['location']} (Quantidade: {delivery['quantity']}) -> ", end='')
            print("\n")
        gerador_saida_json(routes, departure_dates)


if __name__ == '__main__':
    main()