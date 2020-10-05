'''
# =============================================================================
# This file contains the function to do a CNP. In the CNP
# agents form a formation with the agent in the neighborhood that makes 
# their potential fuel savings the biggest!
# =============================================================================
'''


def do_CNP(flight):
    if not flight.departure_time:
        raise Exception("The object passed to the greedy protocol has no departure time, therefore it seems that it is not a flight.")


    if flight.formation_state == 0:

        if flight.negotiation_state == 0:
            if flight.manager == 1 and flight.auctioneer == 0:
                
                #search for auctioneers if the manager hasn't looked yet
                if flight.potential_auctioneers == []:
                    formation_targets = flight.find_CNP_auctioneers()
                    
                    if formation_targets != []:
                        for auctioneer in formation_targets:
                            
                            #will append potential auctioneers to the manager and append all the managers that sent a request to the respective auctioneers
                            flight.which_manager_for_which_auctioneer(auctioneer)
                            
                        
                flight.negotiation_state = 1
            
            #If the flight is an auctioneer, the only thing is to increase the negotiation_state to 1
            elif flight.manager == 0 and flight.auctioneer == 1:
                flight.negotiation_state = 1
            
            else:
                raise Exception("The flight is neither a manager nor an auctioneer")                
                    
                    
                    
                    
 
               
        elif flight.negotiation_state == 1:
            
            if flight.manager == 1 and flight.auctioneer == 0:
                flight.negotiation_state = 2
            
            elif flight.manager == 0 and flight.auctioneer == 1:
                
                for manager in flight.potential_managers:
                    
                    #the auctioneer will only make a bid if it will gain fuel savings
                    if flight.calculate_potential_fuelsavings(manager) > 0:
                        bid_value = flight.calculate_potential_fuelsavings(manager)
                        bid_exp_date = 3 #when the negotiation_state has passed 2, the bid will vanish
                                         #this is a fixed value for CNP
                        flight.make_bid(manager, bid_value, bid_exp_date)
                        
                flight.negotiation_state = 2

            else:
                raise Exception("The flight is neither a manager nor an auctioneer")                         
                    
     


               

        elif flight.negotiation_state == 2: #managers will decide upon winning auctioneer
            if flight.manager == 1 and flight.auctioneer == 0:
            #here the manager will decide upon the winning bid
                valueA = [] #bidding values of alliance members
                valueB = [] #bidding values of non-alliance members
                bidding_agentA = []
                bidding_agentB = []
            
                for bid in flight.received_bids:
                    if bid.get("Alliance") == 1:
                        valueA.append(bid.get("value"))
                        bidding_agentA.append(bid.get("bidding_agent"))
                    elif bid.get("Alliance") == 0:
                        valueB.append(bid.get("value"))
                        bidding_agentB.append(bid.get("bidding_agent"))                           

                if max(valueA) >= max(valueB) or 1.25*max(valueA) >= max(valueB):
                    winning_agent = bidding_agentA[valueA.index(max(valueA))]
                    bid_value = max(valueA)
                    
                elif max(valueA) <= max(valueB):
                    winning_agent = bidding_agentB[valueB.index(max(valueB))]   
                    bid_value = max(valueB)
                    
                else:
                    raise Exception("something went wrong in diciding the winning auctioneer")                            





            
                #as there have passed 2 steps a new fuel saving calculation needs to be performed...
                formation_savings = flight.calculate_potential_fuelsavings(winning_agent)
                
                if len(flight.agents_in_my_formation) > 0:
                    flight.add_to_formation(winning_agent, formation_savings, discard_received_bids=True)
                    
                elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
                    flight.start_formation(winning_agent, formation_savings, discard_received_bids=True)
                    
                flight.negotiation_state = 0
                flight.potential_auctioneers = []
                    
            
        
            elif flight.manager == 0 and flight.auctioneer == 1:
                flight.negotiation_state = 0
                flight.potential_managers = []
            else:
                raise Exception("The flight is neither a manager nor an auctioneer") 
        


       