'''
# =============================================================================
# This file contains the function to do a CNP. In the CNP
# agents form a formation with the agent in the neighborhood that makes
# their potential fuel savings the biggest!
# =============================================================================
'''


def do_CNP(flight):
    if not flight.departure_time:
        raise Exception(
            "The object passed to the greedy protocol has no departure time, therefore it seems that it is not a flight.")

    if flight.formation_state == 0 or flight.formation_state == 2:

        if flight.negotiation_state == 0:
            if flight.manager == 1 and flight.auctioneer == 0:

                # search for auctioneers if the manager hasn't looked yet
                if flight.potential_auctioneers == []:
                    formation_targets = flight.find_CNP_auctioneers()

                    if formation_targets != []:
                        for auctioneer in formation_targets:
                            # will append potential auctioneers to the manager and append all the managers that sent a request to the respective auctioneers
                            flight.which_manager_for_which_auctioneer(auctioneer)




            # If the flight is an auctioneer, the only thing is to increase the negotiation_state to 1
            elif flight.manager == 0 and flight.auctioneer == 1:
                pass

            else:
                raise Exception("The flight is neither a manager nor an auctioneer")


        elif flight.negotiation_state == 1:

            if flight.manager == 1 and flight.auctioneer == 0:
                pass

            elif flight.manager == 0 and flight.auctioneer == 1:
                potential_winning_manager = []

                if flight.potential_managers != []:
                    for manager in flight.potential_managers:
                        potential_winning_manager.append(flight.calculate_potential_fuelsavings(manager))

                    if max(potential_winning_manager) > 0:
                        winning_manager = flight.potential_managers[potential_winning_manager.index(max(potential_winning_manager))]
                        bid_value = max(potential_winning_manager)
                        bid_exp_date = 3 #fixed value
                        flight.make_bid(winning_manager, bid_value, bid_exp_date)

                        if flight.formation_state == 2:
                            raise Exception("auctioneer in formation tries to form other formation...")
                    else:
                        pass

            else:
                raise Exception("The flight is neither a manager nor an auctioneer")



        elif flight.negotiation_state == 2:  # managers will decide upon winning auctioneer
            if flight.manager == 1 and flight.auctioneer == 0:

                if flight.received_bids != []:
                    # here the manager will decide upon the winning bid
                    valueA = []  # bidding values of alliance members
                    valueB = []  # bidding values of non-alliance members
                    bidding_agentA = []
                    bidding_agentB = []

                    for bid in flight.received_bids:
                        if bid.get("Alliance") == 1:
                            valueA.append(bid.get("value"))
                            bidding_agentA.append(bid.get("bidding_agent"))
                        elif bid.get("Alliance") == 0:
                            valueB.append(bid.get("value"))
                            bidding_agentB.append(bid.get("bidding_agent"))
                    if valueA != [] and valueB != []:
                        if flight.Alliance == 1 and (1.25 * max(valueA) >= max(valueB)):
                            winning_agent = bidding_agentA[valueA.index(max(valueA))]
                            bid_value = max(valueA)

                        elif flight.Alliance == 1 and (1.25 * max(valueA) < max(valueB)):
                            winning_agent = bidding_agentB[valueB.index(max(valueB))]
                            bid_value = max(valueB)

                        # if manager is not alliance member --> doesn't care if auctioneer is member
                        elif flight.Alliance == 0:
                            valueA.extend(valueB)
                            bidding_agentA.extend(bidding_agentB)
                            winning_agent = bidding_agentA[valueA.index(max(valueA))]
                            bid_value = max(valueA)
                    elif valueA != [] and valueB == []:
                        winning_agent = bidding_agentA[valueA.index(max(valueA))]
                        bid_value = max(valueA)

                    elif valueA == [] and valueB != []:
                        winning_agent = bidding_agentB[valueB.index(max(valueB))]
                        bid_value = max(valueB)


                    else:
                        winning_agent = 0
                        bid_value = 0

                    if winning_agent != 0:

                        if len(flight.agents_in_my_formation) > 0:
                            flight.add_to_formation(winning_agent, bid_value, discard_received_bids=True)
                            print('large formation!!!')
                        elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
                            flight.start_formation(winning_agent, bid_value, discard_received_bids=True)


            elif flight.manager == 0 and flight.auctioneer == 1:
                pass


            else:
                raise Exception("The flight is neither a manager nor an auctioneer")


    flight.negotiation_state += 1
    if flight.negotiation_state >= 3:
        flight.regenerate_manager_auctioneer()



