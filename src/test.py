# -*- coding: utf-8 -*-
"""
Spyder Editor

This is a temporary script file.
"""
#from kumaraswamy import kumaraswamy

import pickle



pop = pickle.load(open(f"../data/recdata//consumers_items_utilities_predictions_popular.p", "rb"))
for i in range(5):
    print(pop[i][:5])
    print('\n')
