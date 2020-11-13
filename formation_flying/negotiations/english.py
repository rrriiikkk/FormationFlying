'''
# =============================================================================
# This file contains the function to do an English auction.
# =============================================================================
'''
import numpy as np


def do_English(flight):
    if not flight.departure_time:
        raise Exception(
            "The object passed to the English protocol has no departure time, therefore it seems that it is not a flight.")

    if flight.formation_state == 0 or flight.formation_state == 2:


        if flight.negotiation_state == 0:

            if flight.manager == 1 and flight.auctioneer == 0:
                # nothing has to happen, only increase negotiation state
                flight.negotiation_state += 1

            elif flight.manager == 0 and flight.auctioneer == 1:

                # auctioneers will find potential managers
                formation_targets = flight.find_greedy_candidate()  # function works also for English protocol

                if not formation_targets == []:

                    potential_winning_manager = []
                    alliancemember = []

                    for manager in formation_targets:
                        #this is a ducttape fix to make sure only managers are in the formation target list and that they have a formation state of 0 or 2
                        if manager.auctioneer == 1 and manager.manager == 0 or (manager.formation_state == 1 or manager.formation_state == 4):
                            formation_targets.remove(manager)


                    for manager in formation_targets:
                        #make sure the autioneer itself is not already in a formation
                        #then calculate potential fuel savings
                        if manager.accepting_bids == True and not flight.formation_state == 2:

                            potential_winning_manager.append(flight.calculate_potential_fuelsavings(manager))
                            alliancemember.append(manager.Alliance)


                    if not potential_winning_manager == [] and max(potential_winning_manager) > 0 and flight.formation_state == 0:
                        # Alliance members increase their bids with 25%
                        for i in range(len(alliancemember)):
                            if alliancemember[i] == 1:
                                potential_winning_manager[i] = 1.25 * potential_winning_manager[i]

                        #look wich manager corresponds to the highest fuel savings, be it real or artificial in case of alliance with the added 25%
                        winning_manager = formation_targets[
                            potential_winning_manager.index(max(potential_winning_manager))]
                        if winning_manager.auctioneer == 0 and winning_manager.manager == 1:


                            # /20 is randomly chosen, seems reasonable to find a max # of steps to take part in bidding
                            bid_exp_date = int(np.floor(max(potential_winning_manager) / 20))
                            if bid_exp_date == 0:
                                bid_exp_date = 1

                            # max bid is reached at bid_exp_date

                            bid_value = max(potential_winning_manager) / bid_exp_date #the bidding value will be increased linearly to the max value within the bid_exp_date

                            #the auctioneer has to remember his own maximum bid and current bidding done + the bid_exp_date
                            flight.maxbid = max(potential_winning_manager)
                            flight.ownbid = bid_value
                            flight.own_exp_date = bid_exp_date
                            flight.make_bid(winning_manager, bid_value, bid_exp_date)

                            flight.potential_managers = winning_manager #make use of an old list to save storage for a new variable

                            if flight.formation_state == 2:
                                raise Exception("auctioneer in formation tries to form other formation...")

                            flight.negotiation_state += 1
                        else:
                            flight.regenerate_manager_auctioneer()

                    else:
                        flight.regenerate_manager_auctioneer()
                else:
                    flight.regenerate_manager_auctioneer()



        elif flight.negotiation_state % 2 == 1:
            if flight.manager == 1 and flight.auctioneer == 0:
                # managers send list with all biddings to all bidders
                # if there is 1 bidding value left or no new biddings are done, auctioneer wins

                if len(flight.received_bids) >= 1:
                    bidding_values = []
                    for bid in flight.received_bids:
                        bidding_values.append(bid.get("value"))

                    for bid in flight.received_bids:
                        flight.other_bids(bid.get("bidding_agent"), bidding_values)

                    flight.negotiation_state += 1

                    if len(flight.received_bids) == 1 or flight.received_bids == flight.received_bids_old:
                        potential_winning_manager = []
                        for bid in flight.received_bids:
                            potential_winning_manager.append(bid.get("value"))

                        winning_agent = flight.received_bids[potential_winning_manager.index(max(potential_winning_manager))].get("bidding_agent")
                        bid_value = flight.received_bids[potential_winning_manager.index(max(potential_winning_manager))].get("value")

                        if len(flight.agents_in_my_formation) > 0 and not winning_agent.formation_state == 1 and not winning_agent.formation_state == 2 and not winning_agent.formation_state == 4:
                            flight.add_to_formation(winning_agent, bid_value, discard_received_bids=True)
                            print('large formation!!!')
                        elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
                            flight.start_formation(winning_agent, bid_value, discard_received_bids=True)

                        flight.regenerate_manager_auctioneer()

                    flight.received_bids_old = flight.received_bids

                elif len(flight.received_bids) == 0:
                    flight.regenerate_manager_auctioneer()

            # auctioneers have nothing to do in this step, only increase negotiation state
            else:
                flight.negotiation_state += 1


        elif flight.negotiation_state % 2 == 0:
            # auctioneers look at all other bids.
            # if there are still other bids, update own bid if it's under max_fuelsavings
            # if their own bid is the only bid remaining they will be the winning bidder

            if flight.manager == 0 and flight.auctioneer == 1:

                if not flight.bids_of_other_bidders == []:

                    if max(flight.bids_of_other_bidders) > flight.maxbid:
                        flight.regenerate_manager_auctioneer()
                    elif max(flight.bids_of_other_bidders) < flight.maxbid and len(flight.bids_of_other_bidders) > 1:

                        flight.ownbid += flight.maxbid / flight.own_exp_date

                        if flight.ownbid <= flight.maxbid and flight.agents_in_my_formation == 0:
                            flight.make_bid(flight.potential_managers, flight.ownbid, flight.own_exp_date)
                            flight.negotiation_state += 1
                            print('pass')
                            if len(flight.agents_in_my_formation) > 0:

                                raise Exception('auctioneer from formation wants to form another formation')

                        else:
                            flight.regenerate_manager_auctioneer()

                    elif max(flight.bids_of_other_bidders) == flight.maxbid:
                        flight.negotiation_state += 1

                    else:
                        flight.regenerate_manager_auctioneer()
                else:
                    flight.regenerate_manager_auctioneer()

            # auctioneers have nothing to do in this step, only increase negotiation state
            else:
                flight.negotiation_state += 1