# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 17:11:40 2022

@author: HouseFishBalloon
"""
import random

strat=[[]]*10
strat[0]=[1,1,5,5,0,0,2,6,6,10,10,11,12] #One Die Spread
strat[1]=[5,5,5,16,6,6,6,6,6,6] #Convenience Store
strat[2]=[0,0,0,0,0,0,15,9,9,9,9,9,9] #Fruit and Veg
strat[3]=[2,2,2,3,3,3,15,8,8,18] #Furniture Factory
strat[4]=[0,1,2,3,3,3,15,3,4] #Mine Spread
strat[5]=[5,5,5,5,5,5,16,18] #Bakery
strat[6]=[] #Buy Nothing
strat[7]=[1,1,1,1,1,1,15,7,7,18] #Cheese Factory
strat[9]=[1,1,5,5,0,0,2,6,6,10,10,11,12] #One Die Spread


strat=[[]]*4
strat[0]=[5,5,1,1,0,0,2,6,6,10,10,11,12] #One Die Spread
strat[1]=[5,5,5,16,6,6,6,6,6,6] #Convenience Store
strat[2]=[5,5,5,5,5,5,16,18] #Bakery
strat[3]=[1,1,1,1,1,1,15,7,7,18] #Cheese Factory


genetic_iterations = 10000
monte_carlo_iterations = 10000
test_iterations=10000
turns = 80
Players = 2
Population=25
iterations=400

Genetic_Algorithm = False
Monte_Carlo = False
Strategy_Tester = False

Monte_Carlo_Table = False
Monte_Carlo_Table_2 = True