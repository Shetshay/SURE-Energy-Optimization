from pyomo.environ import ConcreteModel, Var, Objective, minimize, Constraint, NonNegativeReals, SolverFactory, Param, Binary
from pyomo.opt.results import TerminationCondition
# Define the time_periods range
time_periods = range(1, 25)  # Represents a 24-hour period

# Create the ConcreteModel
model = ConcreteModel()

# Define decision variables
model.p = Var(time_periods, within=NonNegativeReals)  # Energy usage decision variable
model.x1 = Var(time_periods, domain=NonNegativeReals, bounds=(0, 1))  # Fan status decision variable

# Define Pcharge value (replace this with the appropriate value)
Pcharge = 5000  # For example, assuming the charging capacity is 5000 watts

# Define the upper bound for Pdischarge (replace this with the appropriate value)
Pdischarge_upper_bound = -1000  # For example, assuming the maximum discharge is -1000 watts

# Define the battery variable with the proper bounds
model.x2 = Var(domain=NonNegativeReals, bounds=(Pdischarge_upper_bound, Pcharge))

# Take input for energy prices from the user and store them in a dictionary
energy_prices = 24.0

# Define the parameter P using the user-given energy prices
model.P = Param(time_periods, initialize=energy_prices)

# Fixed temperature value for each hour of the day (all set to 75)
fixed_temperature = 75.0

# Create the temperature variables and set them to the fixed value of 75
model.T = Var(time_periods, within=NonNegativeReals, initialize=fixed_temperature)

# Create binary variable for fan status
model.y = Var(time_periods, domain=Binary)

# Create the objective function using the defined parameter
model.objective = Objective(expr=sum(model.P[t] * model.p[t] for t in time_periods), sense=minimize)

# Define the temperature constraint
def temperature_rule(model, t):
    M = 100  # A big-M constant to linearize the constraint
    return model.x1[t] * M >= model.p[t] * (84 - 38 * (t+1)) - model.T[t] * M
model.temperature_constraint = Constraint(time_periods, rule=temperature_rule)

# Constraint to link x1 and y variables (y[t] = 1 if x1[t] = 1)
def fan_status_rule(model, t):
    return model.x1[t] - model.y[t] == 0
model.fan_status_constraint = Constraint(time_periods, rule=fan_status_rule)

# Solve the optimization problem
solver = SolverFactory('glpk')
results = solver.solve(model)

# After solving the optimization problem
if results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimal Solution Found")
    total_cost = model.objective.expr()
    total_energy_usage = sum(model.p[t].value for t in time_periods)
    print(f"Total cost: {total_cost}")
    print(f"Total energy usage: {total_energy_usage}")
    for t in time_periods:
        print(f"Time period {t}:")
        print(f"  Fan status (x1): {model.x1[t].value}")
        print(f"  Energy usage (p): {model.p[t].value}")
        print(f"  Temperature (T): {model.T[t].value}")
    print(f"Battery status (x2): {model.x2.value}")
    print(f"Total cost: {model.objective.expr()}")
else:
    print("No optimal solution found.")

