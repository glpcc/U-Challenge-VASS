import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

class knowledge_base():
    def __init__(self) -> None:
        pass

    def distance_to_kpoints(self,point_distribution,k,starting_point):
        total_points = point_distribution[starting_point]
        distance = 1
        # While there are points to collect
        while total_points < k :
            if starting_point+distance < len(point_distribution):
                total_points += point_distribution[starting_point+distance]

            if starting_point-distance > 0:
                total_points += point_distribution[starting_point-distance]
            
            if starting_point+distance > len(point_distribution) and starting_point-distance < 0:
                distance = 0
                break
            else:
                distance += 1
        return distance - 1
            