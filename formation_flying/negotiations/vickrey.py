'''
# =============================================================================
# This file contains the function to do a Vickrey auction. 
# =============================================================================
'''

def do_Vickrey(flight):
    if not flight.departure_time:
        raise Exception(
            "The object passed to the greedy protocol has no departure time, therefore it seems that it is not a flight.")

    if flight.formation_state == 0 or flight.formation_state == 2:

        # auctioneers will find potential managers
        if flight.negotiation_state == 0 and flight.formation_state == 0:

            if flight.manager == 1 and flight.auctioneer == 0:
                pass

            elif flight.manager == 0 and flight.auctioneer == 1:

                formation_targets = flight.find_greedy_candidate()  # function works also for Vickrey protocol

                if not formation_targets == []:

                    potential_winning_manager = []
                    alliancemember = []

                    for manager in formation_targets:
                        if manager.accepting_bids == True:
                            potential_winning_manager.append(flight.calculate_potential_fuelsavings(manager))
                            alliancemember.append(manager.Alliance)


                    if max(potential_winning_manager) > 0:
                        if flight.Alliance == 1:
                            for i in range(len(alliancemember)):
                                if alliancemember[i] == 1:
                                    potential_winning_manager[i] = 1.25 * potential_winning_manager[i]

                        winning_manager = formation_targets[potential_winning_manager.index(max(potential_winning_manager))]
                        bid_value = max(potential_winning_manager)
                        bid_exp_date = 2 #fixed value
                        flight.make_bid(winning_manager, bid_value, bid_exp_date)

                        if flight.formation_state == 2:
                            raise Exception("auctioneer in formation tries to form other formation...")
                    else:
                        flight.regenerate_manager_auctioneer()


                else:
                    flight.regenerate_manager_auctioneer()






        elif flight.negotiation_state == 1:  # managers will decide upon winning auctioneer
            if flight.manager == 1 and flight.auctioneer == 0:

                if flight.received_bids != []:
                    # here the manager will decide upon the winning bid
                    bidvalues = []
                    for bid in flight.received_bids:

                        bidvalues.append(bid.get("value"))
                    winning_agent = flight.received_bids[bidvalues.index(max(bidvalues))].get("bidding_agent")
                    bidvalues[bidvalues.index(max(bidvalues))] = -100 #dummy value, makes sure, the winning agent has not to pay the max price
                    bid_value = max(bidvalues)

                    if bid_value > 0:

                        if len(flight.agents_in_my_formation) > 0:
                            flight.add_to_formation(winning_agent, bid_value, discard_received_bids=True)
                            print('large formation!!!')
                        elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
                            flight.start_formation(winning_agent, bid_value, discard_received_bids=True)

                    else:
                        flight.regenerate_manager_auctioneer()
                        
            elif flight.manager == 0 and flight.auctioneer == 1:
                pass


            else:
                raise Exception("The flight is neither a manager nor an auctioneer")


    flight.negotiation_state += 1
    if flight.negotiation_state >= 2:
        flight.regenerate_manager_auctioneer()



