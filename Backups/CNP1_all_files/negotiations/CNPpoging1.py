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

        
        if flight.manager == 1 and flight.auctioneer == 0:
            
            
            #The manager will search for potential auctioneers that are within his vision
            formation_targets = flight.find_CNP_candidate()
    
            #If there are candidates, start a formation with the one that results in the most fuel savings
            if formation_targets != None:
                
                #these two lists will be used to find the winning bid
                candidate_list, savings = [], []
                for agent in formation_targets:
                    
                    if flight.calculate_potential_fuelsavings(agent) > 0:
                        candidate_list.append(agent)
                        savings.append(flight.calculate_potential_fuelsavings(agent))
         
        elif flight.manager == 0 and flight.auctioneer == 1:
            pass
        
        else:
            raise Exception("The flight is neither a manager nor a auctioneer")
    else:
        pass

    
    #look for index in list with max fuel savings, then look up the respective agent
    winning_agent = candidate_list.index(savings.index(max(savings)))                    
                        
   
    
    
    if len(flight.agents_in_my_formation) > 0:
        flight.add_to_formation(winning_agent, max(savings), discard_received_bids=True)
        
    
    elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
        flight.start_formation(winning_agent, max(savings), discard_received_bids=True)
        


       