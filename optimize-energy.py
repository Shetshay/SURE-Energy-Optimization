import pyomo.environ as pyo
import numpy as np
import os
from time import sleep
from pyomo.environ import *
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
os.system("clear")
minutes=np.arange(24) + 1
print("minutes are:\n",minutes)
print("first index of minutes is: \n",minutes[0])
mmo = np.arange(23)+1
# print("-----------------------------\n")
# print("t is : \n",t)
model = pyo.ConcreteModel()
#model.J = pyo.RangeSet(24)



price_data  = [15.80878884, 14.15487435, 13.47277117, 13.07886282,
               13.50686048, 15.25860189, 18.80682313, 21.54721756,
               22.17456447, 20.16044649, 18.29488389, 18.02504128, 
               18.90207813, 18.37364576, 19.25127214, 22.56946201, 
               26.06895408, 30.11379375, 34.15859549, 32.86878767, 
               29.58415874 ,26.67728094, 22.51799112, 18.27328537]
price_data = np.round(price_data,2)
# Defining the price array as a Set
f = np.array(price_data)
model.c = pyo.Set(initialize=f)
model.J=pyo.Set(initialize= minutes)
print("The model J is: \n",model.J.pprint())

print("First element of J is: \n",model.J[1] )



# Defining temperature a Variable
init_dict = {(1):83}
model.T = pyo.Var(model.J, domain=pyo.NonNegativeReals, bounds = (54, 80), initialize=init_dict)
# print(model.T.pprint())

# Defining the decision variable as Variable
model.x = pyo.Var(model.J, domain=pyo.NonNegativeIntegers, bounds=(0, 1), initialize = 0)
# print(model.x.pprint())
# Defining cost function as summation of power times price of power
def obj_expression(model):
    return sum(model.c[j] * model.x[j] for j in model.J) 
model.OBJ = pyo.Objective(expr=obj_expression)

print("The objective function is: \n",model.OBJ.pprint())

# # Defining tempearrure dynamic equation as a constraint. 
# # The temperature will increase by 3 degrees if fan is ON
# # and will decrease by 7 degrees if fan is OFF
def temperature_dynamics_constraint_rule(model, j):
    if j != 24:
        return model.T[j+1] == (model.T[j] - 7)*model.x[j] + (model.T[j] + 3)*(1-model.x[j])
    return pyo.Constraint.Skip

    




model.temperature_dynamics_constraint_rule = pyo.Constraint(model.J, expr=temperature_dynamics_constraint_rule)
print(model.temperature_dynamics_constraint_rule.pprint())

# print("Before upper limit constraint \n")
# # Defining upper temperature limit as a constraint using temp dynamic equation
# def temperature_upperbound_constraint_rule(model,j): 
#     for j in model.J:
#         return model.x[j] >= 0.1*model.T[j] - 7.2 
# model.temperature_upperbound_constraint_rule = pyo.Constraint(model.J, rule=temperature_upperbound_constraint_rule)


# # Defining lower temperature limit as a constraint using temp dynamic equation
# def temperature_lowerbound_constraint_rule(model,j): 
#     for j in model.J:
#         return model.x[j] <= 0.1*model.T[j] - 4.2 
# model.temperature_lowerbound_constraint_rule = pyo.Constraint(model.J, rule=temperature_lowerbound_constraint_rule)


model.display()      # will show you the values of ALL of the model variables and expressions, including the OBJ value
print("This is the model dispaly before calling the solver\n")
# print("Before calling solver\n")
# print("------------------")







scip_available = pyo.SolverFactory('scip').available()
print("scip available: ", scip_available)


optimizer = pyo.SolverFactory("scip")
#print("Before calling solve \n")
results  = optimizer.solve(model)
print(results)
if results.solver.termination_condition == TerminationCondition.optimal:
    print("Optimization was successful.")
else:
    print("Optimization did not converge to an optimal solution.")


model.display()
model.OBJ.display()
print(model.OBJ.expr())
print("This is the value of objective function after optimization\n")
print("This is the value of objecgive function", value(model.OBJ)) #after
print("ABOVE ME IS THE ANSWER")

print("Printing x results:\n")
print(model.x.pprint())
xresults=np.arange(24) + 1
Tresults=np.arange(24) + 1
for j in model.J:
    if j!=25:
        xresults[j-1] = model.x[j].value
        Tresults[j-1] = model.T[j].value
        print("j is:",j, "xresult[j] is:", xresults[j-1],"Tresults[j] is: ", Tresults[j-1])

# for j in model.J:
#     if j!=24:
#         Tresults[j] = model.T[j].value
print(Tresults)

# Create the subplots
fig, axs = plt.subplots(3, 1, figsize=(8, 10))

# Subplot 1
axs[0].set_title("ON/OFF Status")
axs[0].set_xlabel("time step")
axs[0].set_ylabel("ON/OFF")
xt = np.arange(24) + 1
axs[0].bar(xt, xresults)
axs[0].set_xticks(xt)  # Set the x-axis ticks to 1 to 24
axs[0].grid()

# Subplot 2
axs[1].set_title("Price data")
axs[1].set_xlabel("time step")
axs[1].set_ylabel("Price")
axs[1].bar(xt, f)
axs[1].set_xticks(xt)  # Set the x-axis ticks to 1 to 24
axs[1].grid()

# Subplot 3
axs[2].set_title("Temperature data")
axs[2].set_xlabel("time step")
axs[2].set_ylabel("Temperature")
axs[2].plot(xt, Tresults)
axs[2].set_xticks(xt)  # Set the x-axis ticks to 1 to 24
axs[2].grid()

plt.tight_layout()  # Adjust subplots to avoid overlapping labels
plt.show()
