import numpy as np
from core.device import Device

def calculate_weighted_std(device: Device,field)-> float:
    val = np.arange(len(device.analytics[field]))
    wt = device.analytics[field]
    mean = np.average(val, weights=wt)
    variance = np.average((val - mean)**2, weights=wt)
    return np.sqrt(variance)

def calculate_weighted_mean(device: Device,field)-> float:
    val = np.arange(len(device.analytics[field]))
    wt = device.analytics[field]
    return np.average(val, weights=wt) # type: ignore

def mins_to_hours_str(mins)-> str:
    '''Function to convert minutes to a string of hours and minutes'''
    return f"{mins//60:.0f}h {int(mins%60)}mins"