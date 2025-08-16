"""
Based on previously selected data, containing the location of a 5 seconds signal window, 
and the optimal max interval parameters, generates a trainset.h5 file with only the 
5 seconds slice of the signal (as a float array), and corresponding spikes and bursts 
(binary array) 

Input
----------
    - "data/trainset_info.dat" : file containing information about training data (points to h5 dataset files with recorded signal)

Output
----------
    - "data/data_channel.hdf5" : file containing signal of channels used in trainset
    - "data/trainset.hdf5" : file containing 5-seconds slices with (signal, spikes, bursts)
"""

import pandas as pd 
import numpy as np
import h5py
import matplotlib.pyplot as plt 
import tensorflow as tf
from sklearn.model_selection import train_test_split
from helper import *



global timestamp

# define variables to store which (dataset, well, channel) is been 
# currently analyzed
previous_filename = None
previous_well = None
previous_channel = None

# load file containing information necessary to build the trainset
goodBurstsData = pd.read_csv('data/trainset_info.dat', sep = '\s+')

# create file to store signal
fullChannelSignal = h5py.File('data/data_channel.hdf5', 'w')

fullChannelSignal.create_group('indices')
fullChannelSignal.create_group('signal')

inputOutputData = h5py.File('data/trainset.hdf5', 'w')

inputOutputData.create_group('signal')
inputOutputData.create_group('spikesBinary')
inputOutputData.create_group('burstsBinary')


previous_filename = None
previous_well = None
previous_channel = None


stopAt = -1

unique_signals = 0
                            
                            
for index in goodBurstsData.index:
    if index == stopAt: break

    filename = goodBurstsData['filename'][index]
    well = goodBurstsData['well'][index]
    channel = goodBurstsData['channel'][index]
    
    if filename != previous_filename or well != previous_well or channel != previous_channel :
        unique_signals += 1
        
indices_with_same_signal = [[-1] for i in range(unique_signals)]

sampling_freq = 10_000
unique_signals = 0

previous_filename = None
previous_well = None
previous_channel = None

for index in goodBurstsData.index:
    
    print(index)
    
    spikesBinary = np.zeros(6_000_000)
    burstsBinary = np.zeros(6_000_000)

    
    if index == stopAt: break

    filename = goodBurstsData['filename'][index]
    well = goodBurstsData['well'][index]
    channel = goodBurstsData['channel'][index]
    risingEdge = goodBurstsData['risingEdge'][index]
    startTime = goodBurstsData['startTime'][index]
    endTime = goodBurstsData['endTime'][index]
    maxIntervalStart = goodBurstsData['param1'][index]
    maxIntervalEnd = goodBurstsData['param2'][index]
    minIntervalBetween = goodBurstsData['param3'][index]
    minDuration = goodBurstsData['param4'][index]
    minSpikes = goodBurstsData['param5'][index]


    if filename != previous_filename or well != previous_well or channel != previous_channel :
        
        signal = load_signal(filename, well, channel)
        timestamp = [(i+1)/sampling_freq for i in range(len(signal))] 
        threshold = get_threshold(signal, risingEdge)
        spikes, bursts = get_spikes_and_bursts(signal, threshold, 
                         maxIntervalStart, maxIntervalEnd, minIntervalBetween, minDuration, minSpikes)
        
        fullChannelSignal['signal'][str(unique_signals)] = signal
        unique_signals += 1



    indices_with_same_signal[unique_signals-1].append(index)
    
    
    
    previous_filename = filename    
    previous_well = well
    previous_channel = channel
    

    
    signal_slice = signal[timestamp.index(startTime):timestamp.index(endTime)]
    
    spikesBinary[spikes] = 1
    spikesBinary_slice = spikesBinary[timestamp.index(startTime):timestamp.index(endTime)]
    
    for burst in bursts:    
        burstsBinary[burst[0]:burst[-1]] = 1
    burstsBinary_slice = burstsBinary[timestamp.index(startTime):timestamp.index(endTime)]



    inputOutputData['signal'][str(index)] = signal_slice
    inputOutputData['spikesBinary'][str(index)] = spikesBinary_slice
    inputOutputData['burstsBinary'][str(index)] = burstsBinary_slice
    
        
for unique in range(unique_signals):
    indices_with_same_signal[unique].pop(0)
    if len(indices_with_same_signal[unique]) != 0:
        fullChannelSignal['indices'][str(unique)] = indices_with_same_signal[unique]

fullChannelSignal.close()
inputOutputData.close()