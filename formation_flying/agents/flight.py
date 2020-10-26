'''
# =============================================================================
#    In this file the Flight-styleagent is defined.
#
#    Flights have a communication_range that defines the radius in which they 
#    look for their neighbors to negotiate with. They negotiate who to form a 
#    formation with in order to save fuel.  
#    
#    Different negotiation methods can be applied. In the parameter files one 
#    can set 'negototiation_method' which defines which method will be used. 
#    The base model only includes the greedy algorithm.
#
# =============================================================================
'''

import numpy as np

from mesa import Agent
from .airports import Airport
from ..negotiations.greedy import do_greedy
from ..negotiations.CNP import do_CNP
from ..negotiations.english import do_English
import math


def calc_distance(p1, p2):
    # p1 = tuple(p1)
    # p2 = tuple(p2)
    dist = (((p1[0] - p2[0])**2 + (p1[1] - p2[1])**2) ** 0.5)
    return dist


class Flight(Agent):


    # =========================================================================
    # Create a new Flight agent.
    #
    # Args:
    #     unique_id: Unique agent identifier.
    #     pos: Starting position
    #     destination: the position of the destination
    #     destination_agent: the agent of the destination airport
    #     speed: Distance to move per step.
    #     departure_time: step of the model at which the flight should depart its origin
    #
    #     heading: numpy vector for the Flight's direction of movement.
    #     communication_range: Radius to look around for Flights to negotiate with.
    # =========================================================================

    def __init__(
            self,
            unique_id,
            model,
            pos,
            destination_agent,
            destination_pos,
            departure_time,
            speed,
            communication_range,
            
    ):

        super().__init__(unique_id, model)
        self.pos = np.array(pos)
        self.destination = np.array(destination_pos)
        self.destination_agent = destination_agent
        self.speed = speed
        self.departure_time = departure_time
        self.heading = [self.destination[0] - self.pos[0], self.destination[1] - self.pos[1]]
        self.communication_range = communication_range
        

        # =====================================================================
        #   Initialize parameters, the values will not be used later on.
        # =====================================================================
        self.agents_in_my_formation = []

        self.leaving_point = [-10, -10]
        self.joining_point = [-10, -10]

        self.planned_fuel = calc_distance(self.pos, self.destination)
        self.model.total_planned_fuel += self.planned_fuel

        self.fuel_consumption = 0   # A counter which counts the fuel consumed
        self.deal_value = 0         # All the fuel lost or won during bidding

        self.formation_state = 0    # 0 = no formation, 
                                    #1 = committed, 
                                    #2 = in formation, 
                                    #3 = unavailable, 
                                    #4 = adding to formation

        self.state = "scheduled"    # Can be scheduled, flying, or arrived

        self.last_bid_expiration_time = 0

        # =============================================================================
        #   Agents decide during initialization whether they are manager or auctioneer
        #   However, this can also be changed during the flight.
        #
        #   !!! TODO Exc. 1.3: implement when a manager can become an auctioneer and vice versa.!!!
        # =============================================================================
        self.accepting_bids = 0
        self.received_bids = []
        self.received_bids_old = []

        self.manager = self.model.random.choice([0, 1])
        if self.manager:
            self.accepting_bids = 1
        self.auctioneer = abs(1 - self.manager)
        
        
        #in only 'PercentageAlliance' amount of time the flight should be part of the alliance
        zeros = np.zeros(100-self.model.PercentageAlliance, dtype=int)
        ones = np.ones(self.model.PercentageAlliance, dtype=int)
        keuze = np.append(zeros, ones)        
        
        self.Alliance               = self.model.random.choice(keuze)
        self.potential_auctioneers  = []            # this list will contain all the potential auctioneers for a manager
        self.potential_managers     = []            # this list will contain all the potential managers that sent a request to the respective auctioneer
        self.negotiation_state      = 0             # 0 = no negotiation is initialised, managers will send requests to auctioneers
                                                    # 1 = Auctioneers send their biddings if they are interested,
                                                    # 2 = Manager decides who to give the contract
        self.ownbid = 0
        self.maxbid = 0
        self.own_exp_date = 0
        self.bids_of_other_bidders = []             #shows agent the current bids

        self.test = 'helaas'

        
        

    # =============================================================================
    #   In advance, the agent moves (physically) to the next step (after having negotiated)
    # =============================================================================
    def advance(self):
        self.do_move()

    # =============================================================================
    #   In the "step", the negotiations are performed.
    #   Check if the agent is flying, because negotiations are only allowed in the air.
    #
    #   !!! TODO Exc. 2: implement other negotiation methods.!!!
    # =============================================================================
    def step(self):
        if self.state == "flying":
            if self.model.negotiation_method == 0:
                do_greedy(self)

            if len(self.agents_in_my_formation) > 0 and self.formation_state == 0:
                raise Exception("Agent status is no-formation, but it has agents registered as being in its formation...")

            if self.model.negotiation_method == 1:
                do_CNP(self)
            if self.model.negotiation_method == 2:
                do_English(self)
            if self.model.negotiation_method == 3:
                do_Vickrey(self)
            # if self.model.negotiation_method == 4:
            #     do_Japanese(self)

    # =============================================================================
    #   This formula assumes that the route of both agents are of same length, 
    #   because joining- and leaving-points are taken to be as the middle-point 
    #   between their current positions / destinations.
    #
    #   !!! TODO Exc. 1.3: improve calculation joining/leaving point.!!!
    # =============================================================================
    def calculate_joining_point(self, target_agent):

        rotation = np.array([[0, -1], [1, 0]])

        if len(self.agents_in_my_formation) == 0 and len(target_agent.agents_in_my_formation) == 0:
            destination1 = self.destination
            destination2 = target_agent.destination

        else:
            if len(self.agents_in_my_formation) > 0 and len(target_agent.agents_in_my_formation) > 0:
                raise Exception("This function is not advanced enough to handle two formations joining")

            if len(self.agents_in_my_formation) > 0 and len(target_agent.agents_in_my_formation) == 0:
                destination1 = self.leaving_point
                destination2 = target_agent.destination

            elif len(self.agents_in_my_formation) == 0 and len(target_agent.agents_in_my_formation) > 0:
                destination1 = self.destination
                destination2 = target_agent.leaving_point

        origin_midpoint = np.array(self.calc_middle_point(self.pos, target_agent.pos))
        dest_midpoint = np.array(self.calc_middle_point(destination1, destination2))

        trajectory_line = dest_midpoint - origin_midpoint
        trajectory_slope = (dest_midpoint[1] - origin_midpoint[1]) / (dest_midpoint[0] - origin_midpoint[0])

        potential_joinpath_agent1 = origin_midpoint - self.pos
        potential_joinpath_agent2 = origin_midpoint - target_agent.pos

        alpha_agent1 = np.dot(trajectory_line, potential_joinpath_agent1)
        alpha_agent2 = np.dot(trajectory_line, potential_joinpath_agent2)

        # We can multiply by 2 as the joining- and leaving-points are in the middle!
        # WARNING: If you change the way the leaving- and joining-points are calculated, you should change this formula accordingly!

        # Determine the joining point

        if alpha_agent1 < 0 and alpha_agent2 > 0:  # agent 1 is limiting factor
            distance = abs((np.cross(trajectory_line, potential_joinpath_agent1)) / np.linalg.norm(trajectory_line))
            direction = (np.dot(rotation, trajectory_line)) / np.linalg.norm(trajectory_line)
            if self.pos[1] > origin_midpoint[1] + trajectory_slope * (self.pos[0] - origin_midpoint[0]):
                joining_point = self.pos - direction * distance
            elif self.pos[1] < origin_midpoint[1] + trajectory_slope * (self.pos[0] - origin_midpoint[0]):
                joining_point = self.pos + direction * distance
            else:
                joining_point = self.pos

        elif alpha_agent1 > 0 and alpha_agent2 < 0:  # agent 2 is limiting factor
            distance = abs((np.cross(trajectory_line, potential_joinpath_agent2)) / np.linalg.norm(trajectory_line))
            direction = (np.dot(rotation, trajectory_line)) / np.linalg.norm(trajectory_line)
            if target_agent.pos[1] > origin_midpoint[1] + trajectory_slope * (
                    target_agent.pos[0] - origin_midpoint[0]):
                joining_point = target_agent.pos - direction * distance
            elif target_agent.pos[1] < origin_midpoint[1] + trajectory_slope * (
                    target_agent.pos[0] - origin_midpoint[0]):
                joining_point = target_agent.pos + direction * distance
            else:
                joining_point = target_agent.pos

        elif alpha_agent1 == 0 and alpha_agent2 == 0:
            joining_point = origin_midpoint

        else:
            raise Exception("the origin midpoint cannot lay in front or behind both agents")

        return joining_point

    def calculate_leaving_point(self,target_agent):

        rotation = np.array([[0, -1], [1, 0]])

        if len(self.agents_in_my_formation) == 0 and len(target_agent.agents_in_my_formation) == 0:
            destination1 = self.destination
            destination2 = target_agent.destination

        else:
            if len(self.agents_in_my_formation) > 0 and len(target_agent.agents_in_my_formation) > 0:
                raise Exception("This function is not advanced enough to handle two formations joining")

            if len(self.agents_in_my_formation) > 0 and len(target_agent.agents_in_my_formation) == 0:
                destination1 = self.leaving_point
                destination2 = target_agent.destination

            elif len(self.agents_in_my_formation) == 0 and len(target_agent.agents_in_my_formation) > 0:
                destination1 = self.destination
                destination2 = target_agent.leaving_point


        origin_midpoint = np.array(self.calc_middle_point(self.pos, target_agent.pos))
        dest_midpoint = np.array(self.calc_middle_point(destination1, destination2))

        potential_leavepath_agent1 = destination1 - dest_midpoint
        potential_leavepath_agent2 = destination2 - dest_midpoint

        trajectory_line = dest_midpoint - origin_midpoint
        trajectory_slope = (dest_midpoint[1] - origin_midpoint[1]) / (dest_midpoint[0] - origin_midpoint[0])

        beta_agent1 = np.dot(trajectory_line, potential_leavepath_agent1)
        beta_agent2 = np.dot(trajectory_line, potential_leavepath_agent2)

        if beta_agent1 < 0 and beta_agent2 > 0:  # agent 1 is limiting factor
            distance = abs(
                (np.cross(trajectory_line, potential_leavepath_agent1)) / np.linalg.norm(trajectory_line))
            direction = (np.dot(rotation, trajectory_line)) / np.linalg.norm(trajectory_line)
            if self.destination[1] > dest_midpoint[1] + trajectory_slope * (self.destination[0] - dest_midpoint[0]):
                leaving_point = self.destination - direction * distance
            elif self.destination[1] < dest_midpoint[1] + trajectory_slope * (self.destination[0] - dest_midpoint[0]):
                leaving_point = self.destination + direction * distance
            else:
                leaving_point = self.destination

        elif beta_agent1 > 0 and beta_agent2 < 0:  # agent 2 is limiting factor
            distance = abs(
                (np.cross(trajectory_line, potential_leavepath_agent2)) / np.linalg.norm(trajectory_line))
            direction = (np.dot(rotation, trajectory_line)) / np.linalg.norm(trajectory_line)
            if target_agent.destination[1] > dest_midpoint[1] + trajectory_slope * (
                    target_agent.destination[0] - dest_midpoint[0]):
                leaving_point = target_agent.destination - direction * distance
            elif target_agent.destination[1] < dest_midpoint[1] + trajectory_slope * (
                    target_agent.destination[0] - dest_midpoint[0]):
                leaving_point = target_agent.destination + direction * distance
            else:
                leaving_point = target_agent.destination

        elif beta_agent1 == 0 and beta_agent2 == 0:
            leaving_point = dest_midpoint
        else:
            raise Exception("the destination midpoint cannot lay in front or behind both agents")

        return leaving_point

    def calculate_potential_fuelsavings(self, target_agent):

        joining_point = self.calculate_joining_point(target_agent)
        leaving_point = self.calculate_leaving_point(target_agent)

        if len(self.agents_in_my_formation) == 0 and len(target_agent.agents_in_my_formation) == 0:

            original_distance = calc_distance(self.destination,self.pos) + calc_distance(target_agent.destination,target_agent.pos)

            agent1_new_distance = calc_distance(self.pos, joining_point)+self.model.fuel_reduction*calc_distance(
                joining_point, leaving_point) + calc_distance(leaving_point,self.destination)
            agent2_new_distance = calc_distance(target_agent.pos, joining_point) + self.model.fuel_reduction * calc_distance(
                joining_point, leaving_point) + calc_distance(leaving_point, target_agent.destination)

            fuel_savings = original_distance - agent1_new_distance - agent2_new_distance

        else:
            if len(self.agents_in_my_formation) > 0 and len(target_agent.agents_in_my_formation) > 0:
                raise Exception("This function is not advanced enough to handle two formations joining")

            if len(self.agents_in_my_formation) > 0 and len(target_agent.agents_in_my_formation) == 0:
                formation_leader = self
                formation_joiner = target_agent

            elif len(self.agents_in_my_formation) == 0 and len(target_agent.agents_in_my_formation) > 0:
                formation_leader = target_agent
                formation_joiner = self

            # Fuel for formation

            old_distance_formation = 0
            new_distance_formation = 0

            for agent in formation_leader.agents_in_my_formation:
                old_agent_distance = self.model.fuel_reduction * calc_distance(agent.pos, formation_leader.leaving_point) + calc_distance(formation_leader.leaving_point, agent.destination)
                new_agent_distance = calc_distance(agent.pos, joining_point) + self.model.fuel_reduction*calc_distance(joining_point, leaving_point) + calc_distance(leaving_point, agent.destination)
                old_distance_formation += old_agent_distance
                new_distance_formation += new_agent_distance

            # Fuel for joiner

            old_distance_joiner = calc_distance(formation_joiner.pos, formation_joiner.destination)
            new_distance_joiner = calc_distance(formation_joiner.pos, joining_point) + self.model.fuel_reduction * calc_distance(
                joining_point, leaving_point) + calc_distance(leaving_point, formation_joiner.destination)

            # Total fuel

            fuel_savings_formation = old_distance_formation - new_distance_formation
            fuel_savings_joiner = old_distance_joiner - new_distance_joiner

            fuel_savings = fuel_savings_formation + fuel_savings_joiner

        return fuel_savings


    # =========================================================================
    #   Add the chosen flight to the formation. While flying to the joining point 
    #   of a new formation, managers temporarily don't accept any new bids.
    #
    #   Calculate how the "bid_value" is divided.
    #   The agents already in the formation, share the profit from the bid equally.
    #
    #   !!! TODO Exc. 1.1: improve calculation joining/leaving point.!!!
    # =========================================================================
    def add_to_formation(self, target_agent, bid_value, discard_received_bids=True):
        self.model.fuel_savings_closed_deals += self.calculate_potential_fuelsavings(target_agent)

        if len(target_agent.agents_in_my_formation) > 0 and len(self.agents_in_my_formation) >0:
            raise Exception("Warning, you are trying to combine multiple formations - some functions aren't ready for this ("
                  "such as potential fuel-savings)")

        if len(target_agent.agents_in_my_formation) > 0 and len(self.agents_in_my_formation) == 0:
            raise Exception("Model isn't designed for this scenario.")

        self.model.add_to_formation_counter += 1
        self.accepting_bids = False

        if discard_received_bids:
            # Discard all bids that have been received
            self.received_bids = []

        self.joining_point = self.calculate_joining_point(target_agent)
        self.leaving_point = self.calculate_leaving_point(target_agent)
        self.speed_to_joining = self.calc_speed_to_joining_point(target_agent)

        involved_agents = [self]
        for agent in self.agents_in_my_formation:
            involved_agents.append(agent) # These are the current formation agents

        for agent in involved_agents:
            agent.agents_in_my_formation.append(target_agent)
            agent.formation_state = 4

        if target_agent in involved_agents:
            raise Exception("This is not correct")

        bid_receivers = bid_value / (len(
            self.agents_in_my_formation) + 1)

        self.deal_value += bid_receivers
        for agent in self.agents_in_my_formation:
            agent.deal_value += bid_receivers

        target_agent.deal_value -= bid_value

        target_agent.formation_state = 1

        target_agent.joining_point = self.joining_point
        target_agent.leaving_point = self.leaving_point
        target_agent.speed_to_joining = target_agent.calc_speed_to_joining_point(self)

        for agent in involved_agents:
            agent.joining_point = self.joining_point
            agent.leaving_point = self.leaving_point
            agent.speed_to_joining = self.calc_speed_to_joining_point(target_agent)

        target_agent.agents_in_my_formation = involved_agents
        involved_agents.append(target_agent)

    # =========================================================================
    #   The value of the bid is added to the "deal value" of the manager, 
    #   and removed from the auctioneer. A manager leads the formation, the rest
    #   are 'slaves' to the manager.
    #
    #   !!! TODO Exc. 1.3: improve calculation joining/leaving point.!!!
    # =========================================================================
    def start_formation(self, target_agent, bid_value, discard_received_bids=True):
        if self == target_agent:
            raise Exception("ERROR: Trying to start a formation with itself")
        if len(self.agents_in_my_formation) > 0 or len(target_agent.agents_in_my_formation) > 0:
            raise Exception("Starting a formation with an agent that is already in a formation!")

        self.model.new_formation_counter += 1
        self.model.fuel_savings_closed_deals += self.calculate_potential_fuelsavings(target_agent)
        self.deal_value += bid_value
        target_agent.deal_value -= bid_value

        self.accepting_bids = False
        self.formation_role = "manager"
        target_agent.formation_role = "slave"

        # You can use the following error message if you want to ensure that managers can only start formations with
        # auctioneers. The code itself has no functionality, but is a "check"

        if not self.manager and target_agent.auctioneer:
          raise Exception("Manager tries to form a formation with another manager")

        if discard_received_bids:
            self.received_bids = []

        if self.distance_to_destination(target_agent.pos) < 0.001:
            # Edge case where agents are at the same spot.
            self.formation_state = 2
            target_agent.formation_state = 2
            self.accepting_bids = True

        else:
            self.joining_point = self.calculate_joining_point(target_agent)
            target_agent.joining_point = self.joining_point

            self.speed_to_joining = self.calc_speed_to_joining_point(target_agent)
            target_agent.speed_to_joining = target_agent.calc_speed_to_joining_point(self)

            target_agent.formation_state = 1
            self.formation_state = 1


        self.leaving_point = self.calculate_leaving_point(target_agent)
        self.agents_in_my_formation.append(target_agent)
        target_agent.agents_in_my_formation.append(self)
        target_agent.leaving_point = self.leaving_point


    # =============================================================================
    #   This function finds the agents to make a bid to, and returns a list of these agents.
    #   In the current implementation, it randomly returns an agent, 
    #   instead of deciding which manager it wants to make a bid to.
    # =============================================================================

    def find_greedy_candidate(self):
        neighbors = self.model.space.get_neighbors(pos=self.pos, radius=self.communication_range, include_center=True)
        candidates = []
        for agent in neighbors:
            if type(agent) is Flight and agent.negotiation_state == 0 and agent.formation_state == 0:
                if agent.accepting_bids == 1:
              # if agent.formation_state == 0 or agent.formation_state == 2:
                    if not self == agent:
                        # Pass if it is the current agent
                        candidates.append(agent)
        return candidates
    
    # =============================================================================
    #   This function finds the agents to reach out to, and returns a list of these agents.
    # =============================================================================   
    def find_CNP_auctioneers(self):
        neighbors = self.model.space.get_neighbors(pos=self.pos, radius=self.communication_range, include_center=True)
        auctioneers = []
        for agent in neighbors:
            if type(agent) is Flight and agent.negotiation_state == 0 and agent.formation_state == 0:
                if agent.accepting_bids == 0:
                    if not self == agent:
                        # Pass if it is the current agent
                        auctioneers.append(agent)
        return auctioneers

    # =============================================================================
    #   append to manager potential auctioneers and append to potential auctioneers potential managers
    # =============================================================================   

        
    def which_manager_for_which_auctioneer(self, auctioneer):
        self.potential_auctioneers.append(auctioneer)
        auctioneer.potential_managers.append(self)

    def which_manager_for_which_auctioneerENGLISH(self, manager):
        self.potential_managers.append(manager)
        manager.potential_auctioneers.append(self)
        
        

    # =========================================================================
    #   Making the bid.
    # =========================================================================
    def make_bid(self, bidding_target, bid_value, bid_expiration_date):
        bid = {"bidding_agent": self, "value": bid_value, "exp_date": bid_expiration_date, "Alliance": self.Alliance}
        bidding_target.received_bids.append(bid)



    # =========================================================================
    #   Existing flights that havn't formed a formation yet will be re-assigned to become manager/auctioneer
    # =========================================================================
    def regenerate_manager_auctioneer(self):
        self.negotiation_state = 0
        self.potential_auctioneers = []
        self.potential_managers = []
        self.received_bids = []
        self.ownbid = 0
        self.maxbid = 0
        self.own_exp_date = 0
        self.bids_of_other_bidders = []
        if self.formation_state == 0:
            self.manager = self.model.random.choice([0, 1])
            if self.manager:
                self.accepting_bids = 1
            else: 
                self.accepting_bids = 0
            self.auctioneer = abs(1 - self.manager)

    # =========================================================================
    #   Let bidders know what other bids have been done
    # =========================================================================
    def other_bids(self,bidder,otherbids):
        bidder.bids_of_other_bidders = otherbids


    # =========================================================================
    #   This function randomly chooses a new destination airport. 
    #
    #   !!! This can be used if you decide to close airports on the fly while 
    #   implementing de-commitment (bonus-assignment).!!!
    # =========================================================================
    def find_new_destination(self):


        open_destinations = []
        for agent in self.model.schedule.agents:
            if type(agent) is Airport:
                if agent.airport_type == "Destination":
                    open_destinations.append(agent)

        self.destination_agent = self.model.random.choice(open_destinations)
        self.destination = self.destination_agent.pos

        # You could add code here to decommit from the current bid.


    # =========================================================================
    #   'calc_middle_point'
    #   Calculates the middle point between two geometric points a & b. 
    #   Is used to calculate the joining- and leaving-points of a formation.
    #
    #   'distance_to_destination' 
    #   Calculates the distance to one point (destination) from an agents' current point.
    #
    #   !!! TODO Exc. 1.3: improve calculation joining/leaving point.!!!
    # =========================================================================
    def calc_middle_point(self, a, b):
        return [0.5 * (a[0] + b[0]), 0.5 * (a[1] + b[1])]

    def distance_to_destination(self, destination):
        # 
        return ((destination[0] - self.pos[0]) ** 2 + (destination[1] - self.pos[1]) ** 2) ** 0.5

    # =========================================================================
    #   This function actually moves the agent. It considers many different 
    #   scenarios in the if's and elif's, which are explained step-by-step.
    # =========================================================================
    def do_move(self):

        if self.distance_to_destination(self.destination) <= self.speed / 2:
            # If the agent is within reach of its destination, the state is changed to "arrived"
            self.state = "arrived"

        elif self.model.schedule.steps >= self.departure_time:
            # The agent only starts flying if it is at or past its departure time.
            self.state = "flying"

            if self.formation_state == 2 and self.distance_to_destination(self.leaving_point) <= self.speed / 2:
                # If agent is in formation & close to leaving-point, leave the formation
                self.state = "flying"
                self.formation_state = 0
                self.agents_in_my_formation = []

            if (self.formation_state == 1 or self.formation_state == 4) and \
                    self.distance_to_destination(self.joining_point) <= self.speed_to_joining / 2:
                # If the agent reached the joining point of a new formation, 
                # change status to "in formation" and start accepting new bids again.
                self.formation_state = 2
                self.accepting_bids = True

        if self.state == "flying":
            self.model.total_flight_time += 1
            if self.formation_state == 2:
                # If in formation, fuel consumption is 75% of normal fuel consumption.
                f_c = self.model.fuel_reduction * self.speed
                self.heading = [self.leaving_point[0] - self.pos[0], self.leaving_point[1] - self.pos[1]]
                self.heading /= np.linalg.norm(self.heading)
                new_pos = self.pos + self.heading * self.speed



            elif self.formation_state == 1 or self.formation_state == 4:
                # While on its way to join a new formation
                if self.formation_state == 4 and len(self.agents_in_my_formation) > 0:
                    f_c = self.speed_to_joining * self.model.fuel_reduction
                else:
                    f_c = self.speed_to_joining

                self.heading = [self.joining_point[0] - self.pos[0], self.joining_point[1] - self.pos[1]]
                self.heading /= np.linalg.norm(self.heading)
                new_pos = self.pos + self.heading * self.speed_to_joining

            else:
                self.heading = [self.destination[0] - self.pos[0], self.destination[1] - self.pos[1]]
                f_c = self.speed
                self.heading /= np.linalg.norm(self.heading)
                new_pos = self.pos + self.heading * self.speed

            if f_c < 0:
                raise Exception("Fuel cost lower than 0")

            self.model.total_fuel_consumption += f_c
            self.fuel_consumption += f_c

            self.model.space.move_agent(self, new_pos)



    def is_destination_open(self):
        if self.destination_agent.airport_type == "Closed":
            return False
        else:
            return True


    # ========================================================================= 
    #   Calculates the speed to joining point.
    #
    #   !!! TODO Exc. 1.3: improve calculation joining/leaving point.!!!
    # =========================================================================
    def calc_speed_to_joining_point(self, neighbor):

        joining_point = self.calculate_joining_point(neighbor)
        dist_self = ((joining_point[0] - self.pos[0]) ** 2 + (joining_point[1] - self.pos[1]) ** 2) ** 0.5
        dist_neighbor = ((joining_point[0] - neighbor.pos[0]) ** 2 + (joining_point[1] - neighbor.pos[1]) ** 2) ** 0.5

        if dist_self >= dist_neighbor:
            speed = self.speed
        else:
            speed = self.speed*(dist_self/dist_neighbor)

        rest = float(dist_self % speed)
        regular_time = math.floor(float(dist_self / speed))
        if rest > 0:
            time = regular_time + 1
        elif rest == 0:
            time = regular_time
        return float(dist_self / time)
