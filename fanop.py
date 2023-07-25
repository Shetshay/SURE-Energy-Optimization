import pyomo.environ as pyo
import numpy as np
import os
from time import sleep
from pyomo.environ import *
from matplotlib import pyplot as plt
import matplotlib.pyplot as plt
os.system("clear")
minutes=np.arange(24) + 1
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
# print(model.J.pprint())

#print("First element of J is: \n",model.J[1] )



# Defining temperature a Variable
init_dict = {(1):95}
model.T = pyo.Var(model.J, domain=pyo.NonNegativeReals, bounds = (50, 60), initialize=init_dict)
# print(model.T.pprint())

# Defining the decision variable as Variable
model.x = pyo.Var(model.J, domain=pyo.NonNegativeIntegers, bounds=(0, 1), initialize = 0)
# print(model.x.pprint())
# Defining cost function as summation of power times price of power
def obj_expression(model):
    return sum(model.c[j] * model.x[j] for j in model.J) 
model.OBJ = pyo.Objective(expr=obj_expression)

# print(model.OBJ.pprint())

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
print("Printing x results:\n")
print(model.x.pprint())
xresults=np.arange(24)
Tresults=np.arange(24)
for j in model.J:
    if j!=24:
        xresults[j] = model.x[j].value

for j in model.J:
    if j!=24:
        Tresults[j] = model.T[j].value
print(Tresults)


plt.subplot(311)
plt.title("ON/OFF Status") 
plt.xlabel("time step") 
plt.ylabel("ON/OFF") 
xt = np.arange(24)+1
#print(xt)
plt.bar(xt,xresults)

plt.subplot(312)
plt.title("Price data") 
plt.xlabel("time step") 
plt.ylabel("Price") 
xt = np.arange(24)+1
#print(xt)
plt.bar(xt,f)


plt.subplot(313)
plt.title("Temperature data") 
plt.xlabel("time step") 
plt.ylabel("Temperature") 
xt = np.arange(24)+1
#print(xt)
plt.plot(xt,Tresults)
plt.grid()
plt.show()
