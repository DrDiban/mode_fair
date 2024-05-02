from pyomo.environ import *
import math

from utils import calculate_euclidean_distance, find_start_points, find_route_path, show_result

# Data
customer = {
    0: {"latitude": 4.4184, "longitude": 114.0932, "demand": 0},
    1: {"latitude": 4.3555, "longitude": 113.9777, "demand": 5},
    2: {"latitude": 4.3976, "longitude": 114.0049, "demand": 8},
    3: {"latitude": 4.3163, "longitude": 114.0764, "demand": 3},
    4: {"latitude": 4.3184, "longitude": 113.9932, "demand": 6},
    5: {"latitude": 4.4024, "longitude": 113.9896, "demand": 5},
    6: {"latitude": 4.4142, "longitude": 114.0127, "demand": 8},
    7: {"latitude": 4.4804, "longitude": 114.0734, "demand": 3},
    8: {"latitude": 4.3818, "longitude": 114.2034, "demand": 6},
    9: {"latitude": 4.4935, "longitude": 114.1828, "demand": 5},
    10: {"latitude": 4.4932, "longitude": 114.1322, "demand": 8},
    11: {"latitude": 4.4184, "longitude": 114.0932, "demand": 0},
}

vehicle = {
    1: {"capacity": 25, "cost": 1.2},
    2: {"capacity": 30, "cost": 1.5}
}


# Create a Concrete Model
mdl = ConcreteModel()

# Sets
N = list(range(1,12))
V = [0] + N
Car = [1, 2]
A = [(i, j, v) for i in V for j in V if i!=j  for v in Car]
B = [(i, v) for i in V  for v in Car]

# Parameters
c = {(i, j, v): calculate_euclidean_distance(customer, i, j) for i, j, v in A if i!=j}

# Decision Variables
mdl.x = Var(A, domain=Binary)
mdl.cap = Var(B, domain=NonNegativeReals)

# Objective Function
mdl.obj = Objective(expr=sum(mdl.x[i, j, v] * vehicle[v]["cost"] * c[i, j, v] for i, j, v in A if i!=j), sense=minimize)


# Constraint 1 - Each customer visited only once
mdl.demand_constraint = ConstraintList()
def demand_constraint_rule(mdl, i):
    if i == 0 or i == len(customer)-1:
        return Constraint.Skip
    return sum(mdl.x[i, j, v] for j in N if j != i if j!=0 for v in Car) == 1
for i in N:
    mdl.demand_constraint.add(demand_constraint_rule(mdl, i))


# Constraint 2 - If there an inlet to a customer ensure there is an outlet
mdl.route_constraint = ConstraintList()
def route_constraint_rule(mdl, i, v):
    if i ==len(customer)-1:
        return Constraint.Skip
    return sum(mdl.x[h, i, v] for h in V if h != i if h!=len(customer)-1) == sum(mdl.x[i, h, v] for h in V if h != i if h!=0)
    
for i in N:
    for v in Car:
        mdl.route_constraint.add(route_constraint_rule(mdl, i, v))


# Constraint 3 - Vehicle capacity constraint
mdl.capacity_constraints = ConstraintList()
def capacity_constraints_rule(mdl, i, j, v):
    if i==j:
        return Constraint.Skip
    # print(p,i,j,v, "opopo")
    # print(sum(mdl.cap[p, w, i, v] for w in V  if w!=i))
    return mdl.cap[j,v] >= mdl.cap[i,v] + mdl.x[i,j,v]*customer[j]["demand"] - vehicle[v]["capacity"]*(1-mdl.x[i,j,v])

for i in V:
    for j in V:
        for v in Car:
            mdl.capacity_constraints.add(capacity_constraints_rule(mdl, i, j, v))

# Constraint 4 - Lower bound for vehicle capacity constraint
mdl.capacity_flow_lower_constraints = ConstraintList()
def capacity_flow_lower_constraints_rule(mdl, i, v):
    return mdl.cap[i, v] >= customer[i]["demand"]

for i in V:
    for v in Car:
        mdl.capacity_flow_lower_constraints.add(capacity_flow_lower_constraints_rule(mdl, i, v))

# Constraint 5 - Upper bound for vehicle capacity constraint
mdl.capacity_flow_upper_constraints = ConstraintList()
def capacity_flow_upper_constraints_rule(mdl, i, v):
    return mdl.cap[i, v] <= vehicle[v]["capacity"]

for i in V:
    for v in Car:
        mdl.capacity_flow_upper_constraints.add(capacity_flow_upper_constraints_rule(mdl, i, v))

solver = SolverFactory('cbc', executable='/opt/homebrew/opt/cbc/bin/cbc')
results = solver.solve(mdl)

start_points = find_start_points(mdl,V, Car)
route_details = find_route_path(N, V, start_points, mdl, c, customer, vehicle)

print(show_result(route_details))

# Solve the Model

if __name__ == "main":
    print("Model is solving")
    
