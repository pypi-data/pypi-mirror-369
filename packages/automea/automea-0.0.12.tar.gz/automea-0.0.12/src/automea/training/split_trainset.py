##################################################################################################
# Prepare the spikes30, signal30 and signal100 datasets, divided by train, test and validation files
##################################################################################################


#load the packages

import pandas as pd 
import numpy as np
import h5py

import os
from sklearn.model_selection import train_test_split
import random
from sklearn import preprocessing


# load the data
df = pd.read_csv('data/trainset_info.dat', sep = '\s+')
params = df[['param1', 'param2', 'param3']].iloc[:,:].values

data = h5py.File('data/trainset.hdf5', 'r')


namesInt = []
for name, value in data['burstsBinary'].items():
    namesInt.append(int(name))

namesInt = np.sort(namesInt)

burstsBinary = []
signal = []
spikesBinary = []


for index in range(namesInt[-1] + 1):
    burstsBinary.append(np.asarray(data['burstsBinary'][str(namesInt[index])]))
    signal.append(np.asarray(data['signal'][str(namesInt[index])]))
    spikesBinary.append(np.asarray(data['spikesBinary'][str(namesInt[index])]))


burstsBinary = np.array(burstsBinary)
signal = np.array(signal)
spikesBinary = np.array(spikesBinary)

#shuffle the data
shuffledIndices = np.copy(namesInt)
np.random.shuffle(shuffledIndices)


#divide in train, val, test
train_indices, test_indices = train_test_split(shuffledIndices,test_size = 0.15, shuffle = False)
train_indices, val_indices = train_test_split(train_indices,test_size = 0.15, shuffle = False)


# save the indices data division

indicesFile = h5py.File('data/training_indices.hdf5', 'w')
indicesFile['train'] = train_indices
indicesFile['val'] = val_indices
indicesFile['test'] = test_indices
indicesFile.close()



# Prepare the SPIKES DATA for 3 files: train, test and validation

X_train = spikesBinary[train_indices] # spikes, arrays of 0,1
X_test = spikesBinary[test_indices] # spikes, arrays of 0,1
X_val = spikesBinary[val_indices] # spikes, arrays of 0,1

y_train = params[train_indices] # parameters, arrays with 3 elements
y_test = params[test_indices] # parameters, arrays with 3 elements
y_val = params[val_indices] # parameters, arrays with 3 elements


z_train = burstsBinary[train_indices] # bursts, arrays of 0,1
z_test = burstsBinary[test_indices] # bursts, arrays of 0,1
z_val = burstsBinary[val_indices] # bursts, arrays of 0,1


#define function to reduce the dimension
def reduce_dimension(X): 
    X2 = np.zeros((len(X), len(X[0][::30])))
    for i, x in enumerate(X):
        X2[i] = np.array([1 if len(np.where(x[30*j:30*j+30] == 1)[0]) else 0 for j in range(len(x[::30]))])
    return X2


X_train_r = reduce_dimension(X_train)
X_test_r = reduce_dimension(X_test)
X_val_r = reduce_dimension(X_val)

z_train_r = reduce_dimension(z_train)
z_test_r = reduce_dimension(z_test)
z_val_r = reduce_dimension(z_val)



X = [X_train_r, X_test_r, X_val_r]
y = [y_train, y_test, y_val]
X_spikes = [X_train, X_test, X_val]
z = [z_train, z_test, z_val]


# save the new datafiles
if not os.path.exists('data/spikes'):
    os.mkdir('data/spikes/')


data_division = h5py.File('data/spikes/spikes30_train.hdf5', 'w')
data_division['X'] = X_train_r
data_division['y'] = y_train
data_division['z'] = z_train_r
data_division.close()

data_division = h5py.File('data/spikes/spikes30_test.hdf5', 'w')
data_division['X'] = X_test_r
data_division['y'] = y_test
data_division['z'] = z_test_r
data_division.close()

data_division = h5py.File('data/spikes/spikes30_val.hdf5', 'w')
data_division['X'] = X_val_r
data_division['y'] = y_val
data_division['z'] = z_val_r
data_division.close()

# End for spikes data preparation




# Start signal data preparation

#define the averages functions
def averages (X_scaled, window_size):
    
    all_train_moving_avg = []
    
    for j in range(len(X_scaled)):
        numbers = X_scaled[j]
        i = 0
        moving_averages = []
        
        while (i+1)*window_size < len(numbers):
            this_window = numbers[i*window_size : (i+1)*window_size]
            window_average = sum(this_window) / window_size
            moving_averages.append(window_average)
            i += 1
            
        if (i-1)*window_size < len(numbers):
            this_window = numbers[(i-1)*window_size :]
            window_average = sum(this_window) / len(this_window)
            moving_averages.append(window_average)
        
        all_train_moving_avg.append(moving_averages)
    
    return pd.DataFrame(all_train_moving_avg)




#load the dataset and process the data
if not os.path.exists('data/signal'):
    os.mkdir('data/signal')
for dataset, indices in (('train', train_indices), ('test', test_indices), ('val', val_indices)):

    X = signal[indices] # signal elements
    X_spikes = spikesBinary[indices] # spikes elements

    y = params[indices] # parameters (the good ones!)
    z = burstsBinary[indices] # bursts (the good ones!)



    # we need to normalize/modify the data: [0,1] -> we do it in steps: first we take away the bias/average, then we 
    # take the abs value, following we do the average (30 point windows, so it is like we are performing 30ms time 
    # averages, like we did in binary), then we mon-max in [0,1]


    X_norm = np.copy(X)
    X_scaled = X_norm - np.average(X_norm)
    X_scaled = abs(X_scaled)



    #print('avg') # consider either 30 or other value

    X_scaled30 = averages(X_scaled, 30)
    X_scaled100= averages(X_scaled, 100)

    #print('o-1 rescale')
    minmax_scale = preprocessing.MinMaxScaler(feature_range=(0,1)).fit(X_scaled30.T)
    X_minmax=minmax_scale.transform(X_scaled30.T).T
    X_scaled30 = X_minmax



    minmax_scale = preprocessing.MinMaxScaler(feature_range=(0,1)).fit(X_scaled100.T)
    X_minmax=minmax_scale.transform(X_scaled100.T).T
    X_scaled100 = X_minmax



    #save the prepared datasets
    result = h5py.File('data/signal/signal30_{}.hdf5'.format(dataset), 'w')
    result['X'] = X_scaled30
    result['X_spikes'] = reduce_dimension(X_spikes)
    result['y'] = y
    result['z'] = reduce_dimension(z)
    result.close()

    result = h5py.File('data/signal/signal100_{}.hdf5'.format(dataset), 'w')
    result['X'] = X_scaled100
    result['X_spikes'] = reduce_dimension(X_spikes)
    result['y'] = y
    result['z'] = reduce_dimension(z)
    result.close()