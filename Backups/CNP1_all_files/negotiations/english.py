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

        # managers wil find potential auctioneers
        if flight.negotiation_state == 0:

            if flight.manager == 1 and flight.auctioneer == 0:
                formation_targets = flight.find_CNP_auctioneers()  # function works also for English protocol

                if not formation_targets == []:
                    for auctioneer in formation_targets:
                        flight.which_manager_for_which_auctioneer(auctioneer)

                    flight.negotiation_state += 1
                else:
                    flight.regenerate_manager_auctioneer()




            else:
                flight.negotiation_state += 1





        # potential auctioneers will decide if they want to take part of the bidding
        elif flight.negotiation_state == 1:
            if flight.manager == 0 and flight.auctioneer == 1 and not flight.formation_state == 2:
                potential_winning_manager = []
                alliancemember = []

                if flight.potential_managers != []:
                    for manager in flight.potential_managers:

                        if manager.auctioneer == 1 and manager.manager == 0 or (manager.formation_state == 2 or manager.formation_state == 1 or manager.formation_state == 4):
                            flight.potential_managers.remove(manager)
                    for manager in flight.potential_managers:
                        # print("self:",flight.formation_state,"manager:", manager.formation_state)
                        potential_winning_manager.append(flight.calculate_potential_fuelsavings(manager))
                        alliancemember.append(manager.Alliance)






                    if not potential_winning_manager == [] and max(potential_winning_manager) > 0 and flight.formation_state == 0:
                        # Alliance members increase their bids with 25%
                        for i in range(len(alliancemember)):
                            if alliancemember[i] == 1:
                                potential_winning_manager[i] = 1.25 * potential_winning_manager[i]


                        winning_manager = flight.potential_managers[
                            potential_winning_manager.index(max(potential_winning_manager))]
                        if winning_manager.auctioneer == 0:


                            # /20 is randomly chosen, seems reasonable to find a max #steps to take part in bidding
                            bid_exp_date = int(np.floor(max(potential_winning_manager) / 20))
                            if bid_exp_date == 0:
                                bid_exp_date = 1

                            # max bid is reached at bid_exp_date

                            bid_value = max(potential_winning_manager) / bid_exp_date

                            flight.maxbid = max(potential_winning_manager)
                            flight.ownbid = bid_value
                            flight.own_exp_date = bid_exp_date
                            flight.make_bid(winning_manager, bid_value, bid_exp_date)
                            flight.potential_managers = winning_manager

                            if flight.formation_state == 2:
                                raise Exception("auctioneer in formation tries to form other formation...")

                            flight.negotiation_state += 1
                        else:
                            flight.regenerate_manager_auctioneer()

                    else:
                        flight.regenerate_manager_auctioneer()
                else:
                    flight.regenerate_manager_auctioneer()

            elif flight.formation_state == 2:
                flight.regenerate_manager_auctioneer()


            else:
                flight.negotiation_state += 1


        elif flight.negotiation_state % 2 == 0:
            if flight.manager == 1 and flight.auctioneer == 0:
                # managers send list with all biddings to all bidders
                # if there is 1 bidding value left, auctioneer wins --> negotiation state of manager goes to 0!

                if len(flight.received_bids) >= 1 :
                    bidding_values = []
                    for bid in flight.received_bids:
                        bidding_values.append(bid.get("value"))

                    for bid in flight.received_bids:
                        flight.other_bids(bid.get("bidding_agent"), bidding_values)

                    flight.negotiation_state += 1

                    if len(flight.received_bids) == 1 or flight.received_bids == flight.received_bids_old:
                        winning_agent = flight.received_bids[0].get("bidding_agent")
                        bid_value = flight.received_bids[0].get("value")

                        if len(flight.agents_in_my_formation) > 0:
                            flight.add_to_formation(winning_agent, bid_value, discard_received_bids=True)
                            print('large formation!!!')
                        elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0:
                            flight.start_formation(winning_agent, bid_value, discard_received_bids=True)

                        flight.regenerate_manager_auctioneer()

                    flight.received_bids_old = flight.received_bids

                elif len(flight.received_bids) == 0:
                    flight.regenerate_manager_auctioneer()



            else:
                flight.negotiation_state += 1




        elif flight.negotiation_state % 2 == 1:
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
            else:
                flight.negotiation_state += 1





