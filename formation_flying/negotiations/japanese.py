'''
# =============================================================================
# This file contains the function to do a Japanese auction. 
# =============================================================================
'''

def do_Japanese(flight):
    if not flight.departure_time:
        raise Exception(
            "The object passed to the japanese protocol has no departure time, therefore it seems that it is not a flight.")

    if flight.formation_state == 0 or flight.formation_state == 2:

        if flight.negotiation_state == 0:
            if flight.manager == 1 and flight.auctioneer == 0:
                #each auction is opened with a bidding value of 50. This is done to speed up the auction
                flight.auctionvalue = 50

            flight.negotiation_state += 1


        #auctioneers wil search for the best potential auction and take part of that bidding if the starting value of 50 is below their private maximum bidding value
        elif flight.negotiation_state == 1:

            if flight.manager == 0 and flight.auctioneer == 1:
                formation_targets = flight.find_greedy_candidate()  # function works also for Japanese protocol

                if not formation_targets == []:


                    potential_winning_manager = []
                    alliancemember = []

                    for manager in formation_targets:

                        #check if auction is open and calculate own max private bidding value
                        if manager.accepting_bids == True and not manager.auctionvalue == None:
                            potential_winning_manager.append(flight.calculate_potential_fuelsavings(manager))
                            alliancemember.append(manager.Alliance)


                    if not potential_winning_manager == [] and max(potential_winning_manager) > 0:
                        #increase own private max bidding value by 25% if auctioneer AND mananager are part of the alliance
                        if flight.Alliance == 1:
                            for i in range(len(alliancemember)):
                                if alliancemember[i] == 1:
                                    potential_winning_manager[i] = 1.25 * potential_winning_manager[i]

                        flight.potential_managers = formation_targets[potential_winning_manager.index(max(potential_winning_manager))]

                        flight.maxbid = max(potential_winning_manager)

                        bidexp = 0 #dummy value, only used as it is requested by the make_bid function

                        flight.negotiation_state += 1
                        if not flight.potential_managers.auctionvalue == None and flight.maxbid >= flight.potential_managers.auctionvalue:
                            flight.make_bid(flight.potential_managers, flight.potential_managers.auctionvalue, bidexp)

                        else:
                            flight.regenerate_manager_auctioneer()


                    #if there is no auction that is benefitial fot the auctioneer:
                    else:
                        flight.regenerate_manager_auctioneer()


                else:
                    flight.regenerate_manager_auctioneer()
            elif flight.manager == 1 and flight.auctioneer == 0:
                flight.negotiation_state += 1



        elif flight.negotiation_state % 2 == 0:
            #manager will make sure all auctioneers know how many auctioneers are taking part of the auction
            #if one auctioneer is left a formation is started
            if flight.manager == 1 and flight.auctioneer == 0:

                if len(flight.received_bids) > 1:
                    # Open auction, so each bidder should know how many other bidders there are
                    for bid in flight.received_bids:
                        flight.other_bids(bid.get("bidding_agent"), flight.auctionvalue)

                    flight.received_bids = [] #this list will be filled again in next step
                    flight.auctionvalue += 10 #each bidding round the bid value will be increased by 10, seemed reasonable

                    flight.negotiation_state += 1
                elif len(flight.received_bids) == 1:
                    winning_agent = flight.received_bids[0].get("bidding_agent")

                    #this is a ducttape fix that will only allow a manager or auctioneer to take part in 1 formation
                    #without this, at the destination a loop will be created at which formations leave each other but in the next step will rejoin each other...
                    flight.numberformation += 1
                    winning_agent.numberformation += 1

                    if flight.numberformation == 2 or winning_agent.numberformation == 2:
                        flight.regenerate_manager_auctioneer()
                        winning_agent.regenerate_manager_auctioneer()

                    # if winning_agent == flight.unique_id: #duckttape fix
                    #     flight.regenerate_manager_auctioneer()


                    bid_value = flight.auctionvalue
                    #very long if statement, somehow it is otherwise possible to let 2 formations join each other...
                    if len(flight.agents_in_my_formation) > 0 and not winning_agent.formation_state == 1 and not winning_agent.formation_state == 2 and len(winning_agent.agents_in_my_formation) == 0 and not winning_agent in flight.agents_in_my_formation:
                        flight.add_to_formation(winning_agent, bid_value, discard_received_bids=True)
                        print('large formation!!!')
                    elif len(flight.agents_in_my_formation) == 0 and len(winning_agent.agents_in_my_formation) == 0 and flight.manager == 1:

                        flight.start_formation(winning_agent, bid_value, discard_received_bids=True)


                    flight.regenerate_manager_auctioneer()

                elif len(flight.received_bids) == 0:
                    flight.regenerate_manager_auctioneer()
            else:
                flight.negotiation_state += 1



        elif flight.negotiation_state % 2 == 1:
        #in the previous step all auctioneers that are still in the bidding have been sent to all auctioneers, so they
        #'know' with how many they are still in the auction.
        #as in the previous step (that also is the next step) is looked at the amount of auctioneers in the auction,
        #and that a formation is started when only 1 auctioneer is left, it was decided to do nothing with that info in this step
            if flight.manager == 0 and flight.auctioneer == 1:
                if flight.maxbid >= flight.potential_managers.auctionvalue:
                    bidexp = 2 #dummy
                    flight.make_bid(flight.potential_managers, flight.potential_managers.auctionvalue, bidexp)

                    flight.negotiation_state += 1

                else:
                    flight.regenerate_manager_auctioneer()
            else:
                flight.negotiation_state += 1




