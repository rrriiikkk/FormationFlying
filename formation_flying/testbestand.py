# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 15:11:02 2020

@author: HJ Hoogendoorn
"""

import numpy as np






a = [1,2,3,4,5]
b = [6,7,8,9,10]
for i in range(len(a)):
    if a[i] == 1:
        b[i] = 1.25 * b[i]













#selfalliance = 0
#
#received_bids = []
#
#bid1 = {"bidding_agent": 1111, "value": 125, "exp_date": 3, "Alliance": 0}
#bid2 = {"bidding_agent": 1112, "value": 100, "exp_date": 3, "Alliance": 0}
#bid3 = {"bidding_agent": 1113, "value": 100, "exp_date": 3, "Alliance": 1}
#
#received_bids.append(bid1)
#received_bids.append(bid2)
#received_bids.append(bid3)
#
#
#
#if received_bids != []:
# 
#    
#    
#    valueA = [] #bidding values of alliance members
#    valueB = [] #bidding values of non-alliance members
#    bidding_agentA = []
#    bidding_agentB = []
#    
#    
#    for bid in received_bids:
#        if bid.get("Alliance") == 1:
#            valueA.append(bid.get("value"))
#            bidding_agentA.append(bid.get("bidding_agent"))
#        elif bid.get("Alliance") == 0:
#            valueB.append(bid.get("value"))
#            bidding_agentB.append(bid.get("bidding_agent"))       
#     
#    #a deal is only considered with a non-alliance member if the bidding_value is >=25% larger    
#    if selfalliance == 1 and (max(valueA) >= max(valueB) or 1.25*max(valueA) >= max(valueB)):
#        winning_agent = bidding_agentA[valueA.index(max(valueA))]
#        
#    elif selfalliance == 1 and (max(valueA) < max(valueB)):
#        winning_agent = bidding_agentB[valueB.index(max(valueB))]   
# 
#    elif selfalliance == 0:
#        valueA.extend(valueB)
#        bidding_agentA.extend(bidding_agentB)
#        winning_agent = bidding_agentA[valueA.index(max(valueA))]
#    
#    else:
#        raise Exception("something went wrong in diciding the winning auctioneer")
#
#elif received_bids == []:
#    print("gelukt")
#    
    

    