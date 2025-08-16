"""
Define and train machine learning models that predict max interval parameters.

Input
----------
    - "data/trainset.hdf5" : file containing 5-seconds slices with (signal, spikes, bursts)
    - "data/training_indices.hdf5" : file contraining indices separating full training_dataset into training/validation/test set
    - "data/spikes/spikes30_train.hdf5" : training set of spikes30 model
    - "data/spikes/spikes30_val.hdf5" : validation set of spikes30 model
    - "data/spikes/signal30_train.hdf5" : training set of signal30 model
    - "data/spikes/signal30_val.hdf5" : validation set of signal30 model
    - "data/spikes/signal100_train.hdf5" : training set of signal100 model
    - "data/spikes/signal100_val.hdf5" : validation set of signal100 model

Output
----------
    - "models/signal100_train{train_instance}.h5" : trained model for 'training instance' in range(number_of_training_instance)
    - "data/custom_accuracy/{model}_train{train_instance}.csv" : file containing (training, validation) custom accuracy and loss for 'model' and 'train_instance'
""" 


#Loading the packages

import numpy as np
import h5py
import tensorflow as tf
import csv

from tqdm import trange
import time
import os

from helper import *



##################################################################################################################
# functions required to load the data for each model
#################################################################################################################

def data_spikes30():

    data_train = h5py.File('data/spikes/spikes30_train.hdf5', 'r')
    data_val = h5py.File('data/spikes/spikes30_val.hdf5', 'r')
    
    X_train = np.array(data_train['X']) # reduced spikes, lists of 0,1
    y_train = np.array(data_train['y']) # parameters (the good ones!)

    X_val = np.array(data_val['X']) # spikes, lists of 0,1
    y_val = np.array(data_val['y']) # parameters (the good ones!)


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

    indicesFile = h5py.File('data/training_indices.hdf5', 'r')
    train_indices = indicesFile['train']
    val_indices = indicesFile['val']
    test_indices = indicesFile['test']


    Z_train = burstsBinary[train_indices]
    X_spikes_train = spikesBinary[train_indices]

    Z_val = burstsBinary[val_indices]
    X_spikes_val = spikesBinary[val_indices]

    n_features = 1
    inputDim = X_train[0].shape[0]
    n_steps = X_train.shape[1]


    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], n_features))
    y_train = y_train.reshape(((y_train.shape[0], y_train.shape[1])))

    X_val = X_val.reshape((X_val.shape[0], X_val.shape[1], n_features))
    y_val = y_val.reshape(((y_val.shape[0], y_val.shape[1])))

    return X_train, y_train, X_val, y_val, Z_train, Z_val, X_spikes_train, X_spikes_val


def data_signal30():

    data_train = h5py.File('data/signal/signal30_train.hdf5', 'r')
    data_val = h5py.File('data/signal/signal30_val.hdf5', 'r')
    
    X_train = np.array(data_train['X']) # reduced spikes, lists of 0,1
    y_train = np.array(data_train['y']) # parameters (the good ones!)

    X_val = np.array(data_val['X']) # spikes, lists of 0,1
    y_val = np.array(data_val['y']) # parameters (the good ones!)


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

    indicesFile = h5py.File('data/training_indices.hdf5', 'r')
    train_indices = indicesFile['train']
    val_indices = indicesFile['val']
    test_indices = indicesFile['test']


    Z_train = burstsBinary[train_indices]
    X_spikes_train = spikesBinary[train_indices]

    Z_val = burstsBinary[val_indices]
    X_spikes_val = spikesBinary[val_indices]

    n_features = 1
    inputDim = X_train[0].shape[0]
    n_steps = X_train.shape[1]


    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], n_features))
    y_train = y_train.reshape(((y_train.shape[0], y_train.shape[1])))

    X_val = X_val.reshape((X_val.shape[0], X_val.shape[1], n_features))
    y_val = y_val.reshape(((y_val.shape[0], y_val.shape[1])))


    return X_train, y_train, X_val, y_val, Z_train, Z_val, X_spikes_train, X_spikes_val


def data_signal100():

    data_train = h5py.File('data/signal/signal100_train.hdf5', 'r')
    data_val = h5py.File('data/signal/signal100_val.hdf5', 'r')
    
    X_train = np.array(data_train['X']) # reduced spikes, lists of 0,1
    y_train = np.array(data_train['y']) # parameters (the good ones!)

    X_val = np.array(data_val['X']) # spikes, lists of 0,1
    y_val = np.array(data_val['y']) # parameters (the good ones!)


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

    indicesFile = h5py.File('data/training_indices.hdf5', 'r')
    train_indices = indicesFile['train']
    val_indices = indicesFile['val']
    test_indices = indicesFile['test']


    Z_train = burstsBinary[train_indices]
    X_spikes_train = spikesBinary[train_indices]

    Z_val = burstsBinary[val_indices]
    X_spikes_val = spikesBinary[val_indices]

    n_features = 1
    inputDim = X_train[0].shape[0]
    n_steps = X_train.shape[1]


    X_train = X_train.reshape((X_train.shape[0], X_train.shape[1], n_features))
    y_train = y_train.reshape(((y_train.shape[0], y_train.shape[1])))

    X_val = X_val.reshape((X_val.shape[0], X_val.shape[1], n_features))
    y_val = y_val.reshape(((y_val.shape[0], y_val.shape[1])))


    return X_train, y_train, X_val, y_val, Z_train, Z_val, X_spikes_train, X_spikes_val


##################################################################################################################
# define custom accuracy function 
#################################################################################################################

def custom_accuracy(model, X_val, y_val, z_val, X_spikes_val): # NB: X_val and y_val are reshaped for conv
    
    error = []

    for i in trange(len(X_val)):
        #print(i)
        X_input = X_val[i, :]  
        y_ideal = y_val[i, :] #ideal par
        spike_train = X_spikes_val[i, :]
        burst_ideal = z_val[i, :]

        if len(np.where(burst_ideal == 1)[0] != 0):
            
            y_pred = model.predict(X_input.reshape((1, X_val.shape[1], 1)), verbose = 0) # reshape
            #print(y_pred)
            pred_burst_ts = get_bursts_from_spikes(convert_binary_spikes_to_timestamps(spike_train), y_pred[0][0], y_pred[0][1], y_pred[0][2], 20, 5) #returns timestamps
            pred_burst = convert_burst_timestamps_to_binary(pred_burst_ts)

            list_bursts = [burst_ideal, pred_burst]
            error.append(binary_error_function(list_bursts))
    avg = sum(error)/len(error)
    print(avg, 1-avg)

    return 1-avg



##################################################################################################################
# define fit function 
#################################################################################################################
def fit_model(model, X_train, y_train, X_val, y_val, Z_val, Z_train, X_spikes_val, X_spikes_train, n_epochs, bs):
    val_accuracy = []
    train_accuracy= []

    val_loss = []
    train_loss= []

    custom_accuracy_val = []
    custom_accuracy_train= []
    
    for epoch in range(n_epochs):
        print('\nEpoch: ', epoch, '\n')

        history = model.fit(X_train, y_train, 
            batch_size = bs, 
            epochs = 1,
            validation_data = (X_val, y_val), verbose = 0)

      
        val_accuracy.append(history.history['val_accuracy'][0])
        train_accuracy.append(history.history['accuracy'][0])

        val_loss.append(history.history['val_loss'][0])
        train_loss.append(history.history['loss'][0])
        
        val_new_metric = custom_accuracy(model, X_val, y_val, np.array(Z_val), X_spikes_val)
        custom_accuracy_val.append(val_new_metric)

        train_new_metric = custom_accuracy(model, X_train, y_train, np.array(Z_train), X_spikes_train)
        custom_accuracy_train.append(train_new_metric)

    analysis = [ val_accuracy, train_accuracy, val_loss, train_loss, custom_accuracy_val, custom_accuracy_train]

    return model, analysis



##################################################################################################################
# define models
#################################################################################################################



def model_spikes30(): 
              
    model = tf.keras.Sequential()    
    d1, d2 = 128, 64
    
    k1, k2 = 3, 5
              
    model.add(tf.keras.layers.Conv1D(d1, kernel_size= k1, activation='relu',padding='same', input_shape=(X_train.shape[1],1)))

    model.add(tf.keras.layers.Conv1D(d2, kernel_size= k2, activation='relu',padding='same'))
              
    model.add(tf.keras.layers.MaxPooling1D(pool_size=2,strides=1)) 
              
    dr1 = 0.33
    model.add(tf.keras.layers.Dropout(dr1))

    # dr2 = 0.94
    # model.add(tf.keras.layers.Dropout(dr2))
                            
    model.add(tf.keras.layers.Flatten())
    d4 = 64
    model.add(tf.keras.layers.Dense(d4, activation='relu'))
              
    dr3 = 0.12
    model.add(tf.keras.layers.Dropout(dr3))

              
    model.add(tf.keras.layers.Dense(3, activation='relu'))
    
    lrate = 10**-6
              
    rmsprop = tf.keras.optimizers.RMSprop(lr= lrate)
              
    bs = 2

    return model, rmsprop, bs



def model_signal(): 
    
    
    model = tf.keras.Sequential()
    d1, d2 = 128, 64
    
    k1, k2 = 7, 7
              
    model.add(tf.keras.layers.Conv1D(d1, kernel_size= k1, activation='relu',padding='same', input_shape=(X_train.shape[1],1)))

    model.add(tf.keras.layers.Conv1D(d2, kernel_size= k2, activation='relu',padding='same'))
              
    
              
    dr1 = 0.18
    model.add(tf.keras.layers.Dropout(dr1))

    d3 = 16
    k3 = 9
    model.add(tf.keras.layers.Conv1D(d3, kernel_size= k3, activation='relu',padding='same'))
   

    # dr2 = 0.001
    # model.add(tf.keras.layers.Dropout(dr2))
              
              
    model.add(tf.keras.layers.Flatten())
    d4 = 32
    model.add(tf.keras.layers.Dense(d4, activation='relu'))
              
    dr3 = 0.62
    model.add(tf.keras.layers.Dropout(dr3))
              
    model.add(tf.keras.layers.Dense(3, activation='relu'))
    
    lrate = 10**-4              

    sgd = tf.keras.optimizers.SGD(lr= lrate)
   
    bs = 4

    return model, sgd, bs


#################################################################################################################################
### RUN OPTIMIZATION ############################################################################################################
#################################################################################################################################

n_epochs = 50

os.mkdir('models')
os.mkdir('data/custom_accuracy')


#################################################################################################################################
# train spikes30 model
#################################################################################################################################

# load the data
X_train, y_train, X_val, y_val, Z_train, Z_val, X_spikes_train, X_spikes_val = data_spikes30()

for train_instance in range(10):
    model, optim, bs = model_spikes30()
    model.compile(optimizer=optim, loss = tf.keras.losses.MeanSquaredError(), metrics=['accuracy'])

    model, analysis = fit_model(model, X_train, y_train, X_val, y_val, Z_val, Z_train, X_spikes_val, X_spikes_train, n_epochs, int(bs))
    model.save(f'models/spikes30_train{train_instance}.h5')
    with open(f'data/custom_accuracy/spikes30_train{train_instance}.csv', "w") as f:
        wr = csv.writer(f)
        wr.writerows(analysis)

#################################################################################################################################
# train signal30 model
#################################################################################################################################


# load the data
X_train, y_train, X_val, y_val, Z_train, Z_val, X_spikes_train, X_spikes_val = data_signal30()

for train_instance in range(10):

    model, optim, bs = model_signal()

    model.compile(optimizer=optim, loss = tf.keras.losses.MeanSquaredError(), metrics=['accuracy'])

    model, analysis = fit_model(model, X_train, y_train, X_val, y_val, Z_val, Z_train, X_spikes_val, X_spikes_train, n_epochs, int(bs))
    model.save(f'models/signal30_train{train_instance}.h5')
    with open(f'data/custom_accuracy/signal30_train{train_instance}.csv', "w") as f:
        wr = csv.writer(f)
        wr.writerows(analysis)


#################################################################################################################################
# train signal100 model
#################################################################################################################################



# load the data
X_train, y_train, X_val, y_val, Z_train, Z_val, X_spikes_train, X_spikes_val = data_signal100()

for train_instance in range(10):

    model, optim, bs = model_signal()

    model.compile(optimizer=optim, loss = tf.keras.losses.MeanSquaredError(), metrics=['accuracy'])

    model, analysis = fit_model(model, X_train, y_train, X_val, y_val, Z_val, Z_train, X_spikes_val, X_spikes_train, n_epochs, int(bs))
    model.save(f'models/signal100_train{train_instance}.h5')
    with open(f'data/custom_accuracy/signal100_train{train_instance}.csv', "w") as f:
        wr = csv.writer(f)
        wr.writerows(analysis)






