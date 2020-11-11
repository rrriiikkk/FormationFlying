'''
# =============================================================================
# Data functions are saved here (instead of Model.py) for a better overview. 
# These functions can be called upon by the DataCollector. 
# You can add more advanced metric here!
# =============================================================================
'''

from .agents.flight import Flight
from .agents.airports import Airport

def compute_total_fuel_used(model):
    return model.total_fuel_consumption

def compute_planned_fuel(model):
    return model.total_planned_fuel

def fuel_savings_closed_deals(model):
    return model.fuel_savings_closed_deals

def real_fuel_saved(model):
    return model.total_planned_fuel - model.total_fuel_consumption

def total_deal_value(model):
    deal_values = [agent.deal_value for agent in model.schedule.agents]
    return sum(deal_values)

def compute_total_flight_time(model):
    return model.total_flight_time

def total_planned_time(model):
    return model.total_planned_time

def compute_time_delay(model):
    return model.total_flight_time-model.total_planned_time

def compute_model_steps(model):
    return model.schedule.steps

def new_formation_counter(model):
    return model.new_formation_counter

def add_to_formation_counter(model):
    return model.add_to_formation_counter

def number_not_in_formation(model):
    return model.flights_not_in_formation

def compute_average_time_for_formation(model):
    if model.flights_not_in_formation < 50:
        return model.total_steps_till_formations/(50-model.flights_not_in_formation)

def alliance_fuel_counter(model):
    #alliance_planned_fuel = 0
    alliance_real_fuel = 0
    for agent in model.schedule.agents:
        if type(agent) is Flight:
            if agent.Alliance == 1:
                #alliance_planned_fuel += agent.planned_fuel
                alliance_real_fuel += agent.fuel_consumption
    return alliance_real_fuel

