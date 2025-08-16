"""
Generates a 5 second window with signal, spikes, and bursts detected using both the machine learning approach,
and by using default Max Interval parameters. The bursts are layered one above each other, with different colors:
blue and red. Which burst is at the top (colored in blue) or at the bottom (colored in red) is chosen randomly.

Input
----------
    - "models/spikes30.h5" : trained machine learning model spikes30
    - "data/spikes/spikes30_test.hdf5" : file with test data for the spikes30 model
    - "data/training_indices.hdf5" : file contraining indices separating full training_dataset into training/validation/test set
    - "data/data_channel.hdf5" : file contraining signal of channels used in trainset
    - "data/trainset.hdf5" : file containing 5-seconds slices with (signal, spikes, bursts)
    - "data/trainset_info.dat" : file containing information about training data (points to h5 dataset files with recorded signal)
    - "models/signal30.h5" : trained machine learning model signal30
    - "data/signal/signal30_test.hdf5" : file with test data for the signal30 model
    - "models/signal100.h5" : trained machine learning model signal100
    - "data/signal/signal100_test.hdf5" : file with test data for the signal100 model

Output
----------
    - "data/burst_quality/images/spikes30_index{i}_blue{blue}.png" : images with 5-seconds slices with signal, spikes, 
      and bursts detected using machine learning model, and default max interval parameters.
      'i' is in range(number_of_test_samples_spikes30 + number_of_test_samples_signal30 + number_of_test_samples_signal100)
      'blue' = 'Default' or 'Predicted' defines if the blue bursts in the image is the one detected using default max interval parameters
      or the machine learning model
"""



import pandas as pd 
import numpy as np
import h5py
import matplotlib.pyplot as plt 
import tensorflow as tf
from helper import *
import glob
import os



###################################################################
# spikes30
###################################################################

# load model
model = 'models/spikes30.h5'
model = tf.keras.models.load_model(model)
# load data
data = h5py.File('data/spikes/spikes30_test.hdf5', 'r')
# load indices to get test data
indices = h5py.File('data/training_indices.hdf5', 'r')
# load channel data
signals_file = h5py.File('data/data_channel.hdf5', 'r')
# select test indices 
indices_of_test_data = np.array(indices['test'])
# load training_set data
inout = h5py.File('data/trainset.hdf5', 'r')
generated_data_indices = pd.read_csv('data/trainset_info.dat', sep = '\s+')

if os.path.exists('data/burst_quality') is False:
    os.mkdir('data/burst_quality')
if os.path.exists('data/burst_quality/images') is False:
    os.mkdir('data/burst_quality/images')

### generate images and save in folder
for i, index in enumerate(indices_of_test_data):
    signal = np.array(inout['signal'][str(index)])
    signal_cp = np.copy(signal)
    risingEdge = generated_data_indices['risingEdge'][i]
    for j in range(np.array(signals_file['indices'], dtype = int).max()+1):
        indices_j = np.array(signals_file['indices'][str(j)])
        if i in indices_j:
            fullSignal = np.array(signals_file['signal'][str(j)])
            break
    thresh = get_threshold(fullSignal, rising = risingEdge)
    signal = signal - signal.min()
    signal /= signal.max() - signal.min()
    thresh = thresh - signal_cp.min()
    thresh /= signal_cp.max() - signal_cp.min()
    diff_thresh = thresh - np.average(signal)                  
    binary_input = data['X'][i]
    # predict maxinterval params using machine learning model
    params = model.predict(binary_input.reshape(1,len(binary_input)), verbose = 0)[0] 
    binary_spikes = np.array(inout['spikesBinary'][str(index)])
    timestamp_spikes = convert_binary_spikes_to_timestamps(binary_spikes)
    # detect bursts using default parameters
    default_bursts = get_bursts_from_spikes(timestamp_spikes, 15, 20, 25, 20, 5) 
    bursts_optimal = np.array(inout['burstsBinary'][str(index)])
    # detect bursts using predicted parameters
    bursts = get_bursts_from_spikes(timestamp_spikes, params[0], params[1], params[2], 20, 5)
    bursts_binary = convert_burst_timestamps_to_binary(bursts)
    default_bursts_binary = convert_burst_timestamps_to_binary(default_bursts)

    # randomly define if default or predicted bursts are going to be blue (at the top)
    blue = np.random.choice(['Default', 'Predicted'])

    # plot and save image
    fig, ax = plt.subplots(figsize = (12,8))
    ax.plot(signal, c = 'k', alpha = 0.9)
    ax.hlines(np.average(signal)+diff_thresh, 0, 50_000, color = '#2b75cf')
    ax.hlines(np.average(signal)-diff_thresh, 0, 50_000, color = '#d12721')

    if blue == 'Default':
        ax.vlines(np.where(default_bursts_binary == 1)[0], -0.1,-0.05, color = '#2b75cf')
        ax.vlines(np.where(bursts_binary == 1)[0], -0.17,-0.12,color = '#d12721')
    else:
        ax.vlines(np.where(bursts_binary == 1)[0], -0.1,-0.05, color = '#2b75cf')
        ax.vlines(np.where(default_bursts_binary == 1)[0], -0.17,-0.12,color = '#d12721')

    ax.vlines(np.where(binary_spikes == 1)[0], -0.24,-0.19, color = '#5d2f8f')
    ax.set_xticks([])
    ax.set_yticks([])
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig(f'data/burst_quality/images/spikes30_index{i}_blue{blue}.png')
    plt.close()
    

    
###################################################################
# signal30
###################################################################

# load model
model = 'models/signal30.h5'
model = tf.keras.models.load_model(model)
# load data
data = h5py.File('data/signal/signal30_test.hdf5', 'r')

for i, index in enumerate(indices_of_test_data):
    if i == 2: break
    signal = np.array(inout['signal'][str(index)])
    signal_cp = np.copy(signal)
    risingEdge = generated_data_indices['risingEdge'][i]
    for j in range(np.array(signals_file['indices'], dtype = int).max()+1):
        indices_j = np.array(signals_file['indices'][str(j)])
        if i in indices_j:
            fullSignal = np.array(signals_file['signal'][str(j)])
            break
    thresh = get_threshold(fullSignal, rising = risingEdge)
    signal = signal - signal.min()
    signal /= signal.max() - signal.min()
    thresh = thresh - signal_cp.min()
    thresh /= signal_cp.max() - signal_cp.min()
    diff_thresh = thresh - np.average(signal)                  
    binary_input = data['X'][i]
    params = model.predict(binary_input.reshape(1,len(binary_input)), verbose = 0)[0]
    binary_spikes = np.array(inout['spikesBinary'][str(index)])
    timestamp_spikes = convert_binary_spikes_to_timestamps(binary_spikes)
    default_bursts = get_bursts_from_spikes(timestamp_spikes, 15, 20, 25, 20, 5) 
    bursts = get_bursts_from_spikes(timestamp_spikes, params[0], params[1], params[2], 20, 5)
    bursts_binary = convert_burst_timestamps_to_binary(bursts)
    default_bursts_binary = convert_burst_timestamps_to_binary(default_bursts)

    fig, ax = plt.subplots(figsize = (12,8))
    ax.plot(signal, c = 'k', alpha = 0.9)
    ax.hlines(np.average(signal)+diff_thresh, 0, 50_000, color = '#2b75cf')
    ax.hlines(np.average(signal)-diff_thresh, 0, 50_000, color = '#d12721')
    
    blue = np.random.choice(['Default', 'Predicted'])
    if blue == 'Default':
        ax.vlines(np.where(default_bursts_binary == 1)[0], -0.1,-0.05, color = '#2b75cf')
        ax.vlines(np.where(bursts_binary == 1)[0], -0.17,-0.12,color = '#d12721')
    else:
        ax.vlines(np.where(bursts_binary == 1)[0], -0.1,-0.05, color = '#2b75cf')
        ax.vlines(np.where(default_bursts_binary == 1)[0], -0.17,-0.12,color = '#d12721')
        
    
    ax.vlines(np.where(binary_spikes == 1)[0], -0.24,-0.19, color = '#5d2f8f')
    ax.set_xticks([])
    ax.set_yticks([])
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig(f'data/burst_quality/images/signal30_index{i}_blue{blue}.png')
    plt.close()

    
###################################################################
# signal100
###################################################################

# load model
model = 'models/signal100.h5'
model = tf.keras.models.load_model(model)
# load data
data = h5py.File('data/signal/signal100_test.hdf5', 'r')

for i, index in enumerate(indices_of_test_data):
    if i == 2: break
    signal = np.array(inout['signal'][str(index)])
    signal_cp = np.copy(signal)
    risingEdge = generated_data_indices['risingEdge'][i]
    for j in range(np.array(signals_file['indices'], dtype = int).max()+1):
        indices_j = np.array(signals_file['indices'][str(j)])
        if i in indices_j:
            fullSignal = np.array(signals_file['signal'][str(j)])
            break
    thresh = get_threshold(fullSignal, rising = risingEdge)
    signal = signal - signal.min()
    signal /= signal.max() - signal.min()
    thresh = thresh - signal_cp.min()
    thresh /= signal_cp.max() - signal_cp.min()
    diff_thresh = thresh - np.average(signal)                  
    binary_input = data['X'][i]
    params = model.predict(binary_input.reshape(1,len(binary_input)), verbose = 0)[0]
    binary_spikes = np.array(inout['spikesBinary'][str(index)])
    timestamp_spikes = convert_binary_spikes_to_timestamps(binary_spikes)
    default_bursts = get_bursts_from_spikes(timestamp_spikes, 15, 20, 25, 20, 5) 
    bursts = get_bursts_from_spikes(timestamp_spikes, params[0], params[1], params[2], 20, 5)
    bursts_binary = convert_burst_timestamps_to_binary(bursts)
    default_bursts_binary = convert_burst_timestamps_to_binary(default_bursts)


    fig, ax = plt.subplots(figsize = (12,8))
    ax.plot(signal, c = 'k', alpha = 0.9)
    ax.hlines(np.average(signal)+diff_thresh, 0, 50_000, color = '#2b75cf')
    ax.hlines(np.average(signal)-diff_thresh, 0, 50_000, color = '#d12721')
    
    blue = np.random.choice(['Default', 'Predicted'])
    if blue == 'Default':
        ax.vlines(np.where(default_bursts_binary == 1)[0], -0.1,-0.05, color = '#2b75cf')
        ax.vlines(np.where(bursts_binary == 1)[0], -0.17,-0.12,color = '#d12721')
    else:
        ax.vlines(np.where(bursts_binary == 1)[0], -0.1,-0.05, color = '#2b75cf')
        ax.vlines(np.where(default_bursts_binary == 1)[0], -0.17,-0.12,color = '#d12721')
        
    ax.vlines(np.where(binary_spikes == 1)[0], -0.24,-0.19, color = '#5d2f8f')
    ax.set_xticks([])
    ax.set_yticks([])
    for axis in ['top','bottom','left','right']:
        ax.spines[axis].set_linewidth(1.5)
    plt.tight_layout()
    plt.savefig(f'data/burst_quality/images/signal100_index{i}_blue{blue}.png')
    plt.close()
