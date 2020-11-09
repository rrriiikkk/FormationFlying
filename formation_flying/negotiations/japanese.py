'''
# =============================================================================
# This file contains the function to do a Japanese auction. 
# =============================================================================
'''

def do_Japanese(flight):
    if not flight.departure_time:
        raise Exception(
            "The object passed to the greedy protocol has no departure time, therefore it seems that it is not a flight.")

    if flight.formation_state == 0 or flight.formation_state == 2:

        if flight.negotiation_state == 0:
            if flight.manager == 1 and flight.auctioneer == 0:
                flight.auctionvalue = 50

            flight.negotiation_state += 1



        elif flight.negotiation_state == 1:
            if flight.manager == 0 and flight.auctioneer == 1:
                formation_targets = flight.find_greedy_candidate()  # function works also for Japanese protocol

                if not formation_targets == []:


                    potential_winning_manager = []
                    alliancemember = []

                    for manager in formation_targets:
                        if manager.accepting_bids == True and not manager.auctionvalue == None:
                            potential_winning_manager.append(flight.calculate_potential_fuelsavings(manager))
                            alliancemember.append(manager.Alliance)
                    # print(potential_winning_manager)

                    if not potential_winning_manager == [] and max(potential_winning_manager) > 0:
                        if flight.Alliance == 1:
                            for i in range(len(alliancemember)):
                                if alliancemember[i] == 1:
                                    potential_winning_manager[i] = 1.25 * potential_winning_manager[i]

                        flight.potential_managers = formation_targets[potential_winning_manager.index(max(potential_winning_manager))]

                        flight.maxbid = max(potential_winning_manager)

                        bidexp = 0 #dummy value

                        flight.negotiation_state += 1
                        if not flight.potential_managers.auctionvalue == None and flight.maxbid >= flight.potential_managers.auctionvalue:
                            flight.make_bid(flight.potential_managers, flight.potential_managers.auctionvalue, bidexp)

                        else:
                            flight.regenerate_manager_auctioneer()



                    else:
                        flight.regenerate_manager_auctioneer()


                else:
                    flight.regenerate_manager_auctioneer()
            elif flight.manager == 1 and flight.auctioneer == 0:
                flight.negotiation_state += 1



        elif flight.negotiation_state % 2 == 0:
            if flight.manager == 1 and flight.auctioneer == 0:

                if len(flight.received_bids) > 1:
                    # Open auction, so each bidder should know how many other bidders there are
                    for bid in flight.received_bids:
                        flight.other_bids(bid.get("bidding_agent"), flight.auctionvalue)

                    flight.received_bids = [] #this list will be filled again in next step
                    flight.auctionvalue += 10

                    flight.negotiation_state += 1
                elif len(flight.received_bids) == 1:
                    winning_agent = flight.received_bids[0].get("bidding_agent")
                    flight.numberformation += 1
                    winning_agent.numberformation += 1

                    if flight.numberformation == 2 or winning_agent.numberformation == 2:
                        flight.regenerate_manager_auctioneer()
                        winning_agent.regenerate_manager_auctioneer()

                    bid_value = flight.auctionvalue
                    if len(flight.agents_in_my_formation) > 0 and not winning_agent.formation_state == 1 and not winning_agent.auctioneer == 1:
                        flight.add_to_formation(winning_agent, bid_value, discard_received_bids=True)
                        print('large formation!!!')
                    elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
                        flight.start_formation(winning_agent, bid_value, discard_received_bids=True)


                    flight.regenerate_manager_auctioneer()

                elif len(flight.received_bids) == 0:
                    flight.regenerate_manager_auctioneer()
            else:
                flight.negotiation_state += 1



        elif flight.negotiation_state % 2 == 1:

            if flight.manager == 0 and flight.auctioneer == 1:
                if flight.maxbid >= flight.potential_managers.auctionvalue:
                    bidexp = 2 #dummy
                    flight.make_bid(flight.potential_managers, flight.potential_managers.auctionvalue, bidexp)

                    flight.negotiation_state += 1

                else:
                    flight.regenerate_manager_auctioneer()
            else:
                flight.negotiation_state += 1




