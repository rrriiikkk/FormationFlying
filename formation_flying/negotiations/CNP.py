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
            #search for auctioneers
                
            if flight.formation_state == 0:
                formation_targets = flight.find_CNP_auctioneers()

         
        elif flight.manager == 0 and flight.auctioneer == 1:
            #search for managers is not needed as they will reach out to auctioneers
            pass
        
        else:
            raise Exception("The flight is neither a manager nor a auctioneer")
    else:
        pass


    
                   

        


       