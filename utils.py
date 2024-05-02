from pyomo.environ import *

import math

def calculate_euclidean_distance(customer, i, j):
    lat_diff = customer[i]["latitude"] - customer[j]["latitude"]
    long_diff = customer[i]["longitude"] - customer[j]["longitude"]
    val = 100 * math.sqrt(lat_diff**2 + long_diff**2)
    return val


def find_start_points(mdl,V, Car):
    start_points = []
    for j in V:
        if j == 0:
            continue
        for p in Car:
            if value(mdl.x[0,j,p]) == 1:
                start_points.append([0,j,p])
    return start_points


def find_route_path(N, V, start_points, mdl, c, customer, vehicle):
    full_details = {"routes": {}}
    total_overall_cost = 0
    total_overall_distance = 0
    for idx, start_point in enumerate(start_points):
        # start point is depot, end_point is depot and idx value is number of total customer + 1
        start_point, cur_point, vehicle_type = start_point
        end_point_index = len(N)
        cost_per_km = vehicle[vehicle_type]["cost"]

        #initialize values
        cur_path_route = [start_point, cur_point]
        cur_path_demand = [0, customer[cur_point]["demand"]]
        cur_path_distance = [0, c[0, cur_point, vehicle_type]]
        total_cur_route_cost = cur_path_distance[-1]*cost_per_km
        total_cur_route_demand = cur_path_demand[-1]
        total_cur_path_distance = cur_path_distance[-1]

        while cur_point!= end_point_index:
            for j in V:
                if cur_point == j:
                    continue
                if value(mdl.x[cur_point,j, vehicle_type]) == 1:
                    past_point = cur_point
                    cur_point = j
                    cur_path_route.append(cur_point)
                    cur_path_demand.append(customer[cur_point]["demand"])
                    cur_path_distance.append(c[past_point, cur_point, vehicle_type])

                    total_cur_route_cost += cur_path_distance[-1]*cost_per_km
                    total_cur_route_demand += cur_path_demand[-1]
                    total_cur_path_distance += cur_path_distance[-1]
        total_overall_cost += total_cur_route_cost
        total_overall_distance += total_cur_path_distance
                
        details = {"path_route" : cur_path_route,
                   "vehicle_type" :vehicle_type,
                   "cur_path_demand_list": cur_path_demand,
                   "cur_path_distance_list" : cur_path_distance,
                   "total_cur_route_cost" : total_cur_route_cost,
                   "total_cur_route_demand" : total_cur_route_demand,
                   "total_cur_path_distance" : total_cur_path_distance
                  }
        full_details["routes"][idx] = details
    full_details["total_overall_cost"] = total_overall_cost
    full_details["total_overall_distance"] = total_overall_distance
    return full_details


def generate_route_answer(route_result, idx):
    total_distance = round(route_result['total_cur_path_distance'], 2)
    total_cost = round(route_result['total_cur_route_cost'], 2)
    total_demand = round(route_result['total_cur_route_demand'], 2)
    vehicle_type = chr(route_result['vehicle_type']+96).upper()
    path_route = route_result['path_route']
    cur_path_distance_list = route_result['cur_path_distance_list']

    route_answer = ""
    route_answer += f"Vehicle {idx} (Type {vehicle_type}):\n"
    route_answer += f"Round Trip Distance: {total_distance} km, Cost RM {total_cost}, Demand: {total_demand}\n"
 
    path_route_answer = ""
    for idx, route in enumerate(path_route):
        if route == 0:
            path_route_answer += "Depot -> "
        elif idx == len(path_route)-1:
            path_route_answer += f"Depot ({round(cur_path_distance_list[-1],2)} km)\n\n"
        else:
            path_route_answer += f"C{route} ({round(cur_path_distance_list[idx],2)} km) -> "
    
    route_answer += path_route_answer 
    return route_answer


def show_result(result):
    total_distance = round(result['total_overall_distance'], 2)
    total_cost = round(result['total_overall_cost'], 2)
    result_routes = result["routes"]
    answer = ""
    answer += f"Total Distance = {total_distance} km\n"
    answer += f"Total Cost = RM {total_cost}\n\n"

    for idx in result_routes:
        answer += generate_route_answer(result_routes[idx], idx+1)

    return answer


