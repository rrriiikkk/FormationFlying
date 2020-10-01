# -*- coding: utf-8 -*-
"""
Created on Thu Oct  1 15:11:02 2020

@author: HJ Hoogendoorn
"""

import numpy as np
import random as rd



test = ([1,2,3])

PercentageAlliance = 40


zeros = np.zeros(100-PercentageAlliance, dtype=int)

ones = np.ones(PercentageAlliance, dtype=int)
keuze = np.append(zeros, ones)
print(rd.choice(keuze))