"""
helper functions used to manipulate and analyze MEA data.

"""


import h5py
import numpy as np



def load_signal(filename, well, channel):
    # create an object h5 with the file structure from filename
    h5 = h5py.File(filename, 'r')        # 'r' = read

    infoChannel = h5['Data']['Recording_0']['AnalogStream']['Stream_0']['InfoChannel'] 
    channelData = h5['Data']['Recording_0']['AnalogStream']['Stream_0']['ChannelData']

    for i in range(len(infoChannel)):
        groupID = infoChannel[i][2]
        rowIndex = infoChannel[i][1]
        if well == groupID and well*12+channel == rowIndex:
            #signalRaw = channelData[rowIndex]     # get raw signal from specific well and channel
            signalRaw = np.array(channelData[rowIndex])
            break

    adZero = infoChannel[i][8]
    conversionFactor = infoChannel[i][10]
    exponent = infoChannel[i][7]

    # convert the signal to V and multiple by 1e6 to get it in microV
    signal = 1e6*(signalRaw-adZero)*conversionFactor*10.0**exponent

    return signal

def get_threshold(signal, rising = 8):
    global risingEdge
    risingEdge = rising
    ## in order to set the thresholds, the standard deviation
    ## for the first 1000 points is calculated
    stdDeviationConsidered_in_s = 0.250
    #risingEdge = 8  ## falling edge = to rising edge
    signalStdList = []
    startAnalysisTime = 0
    signalStdList = signal[startAnalysisTime*10000:startAnalysisTime*10000+int(stdDeviationConsidered_in_s*10000)]
    threshold = risingEdge * np.std(abs(np.array(signalStdList)))

    return threshold



def get_spikes_and_bursts(signal, threshold, maxIntervalStartBurst, maxIntervalEndBurst, minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst):
    
    deadtime = 30
    spikes = []
    for i in range(len(signal)):
        if(not len(spikes)):    
            if(abs(signal[i])>threshold):
                spikes.append(i)
        else:
            if(abs(signal[i])>threshold and (abs(i - spikes[-1]) > deadtime)):
                spikes.append(i)   
    

    
    # multiply by *10 factor to get values in "index units"
    maxIntervalStartBurst, maxIntervalEndBurst = maxIntervalStartBurst*10, maxIntervalEndBurst*10 
    minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst = minIntervalBetweenBursts*10, minDurationOfBurst*10, minSpikeCountInBurst

    #spikes = convert_binary_spikes_to_timestamps(spikes)
    bursts = []
    i = 0
    k = 0
    #print('first spike', spikes[0])
        
    while (i < len(spikes)-2):
        if(abs(spikes[i] - spikes[i+1]) <= maxIntervalStartBurst):
            bursts.append([spikes[i],spikes[i+1]])
            j = i+1
            while(abs(spikes[j] - spikes[j+1]) < maxIntervalEndBurst):
                bursts[k].append(spikes[j+1])
                j += 1
                if(j >= len(spikes) - 1): break #j+1, -2 ## -1
            i = j+1
            k += 1
        else:
            i += 1      


    valid_bursts = []
    
    for burst in bursts:
        if len(burst) > minSpikeCountInBurst and abs(burst[0] - burst[-1]) > minDurationOfBurst:
            valid_bursts.append([burst[0], burst[-1]])
            
    final_bursts = []

    if len(valid_bursts) > 1:
        i = 0
        initial_time = valid_bursts[i][0]
        final_time = valid_bursts[i][-1]
        
        
        while(i < len(valid_bursts) - 1):

            if abs(valid_bursts[i][-1] - valid_bursts[i+1][0]) < minIntervalBetweenBursts:
                #initial_time = valid_bursts[i][0]
                final_time = valid_bursts[i+1][-1]
                #merged_burst.append([vinitial_time, final_time ])
                #valid_bursts[i] = valid_bursts[i] + valid_bursts[i+1]
                #valid_bursts.remove(valid_bursts[i+1])
                if i+1 == len(valid_bursts) -1:
                    final_bursts.append([initial_time, final_time ])

                    
            else:
                final_bursts.append([initial_time, final_time ])
                if i < len(valid_bursts)-2:
                    initial_time = valid_bursts[i+1][0]
                    final_time = valid_bursts[i+1][-1]
                else:
                    final_bursts.append([valid_bursts[i+1][0], valid_bursts[i+1][-1] ])
                    
            i+= 1
        
    elif len(valid_bursts) == 1:
        final_bursts = valid_bursts
    
    else:
        print('We don\'t get valid bursts from this set of parameters')
    return np.array(spikes), np.array(final_bursts, dtype=object) # I have modified it in np.array





def convert_binary_spikes_to_timestamps(binary_list):
    spikes = []
    for i in range(len(binary_list)):
        if binary_list[i]==1:
            spikes.append(i) #not +1
    return spikes


# it is the same get_burst function from 00_Dataset_Formatting_step0... just renamed
def get_bursts_from_spikes(spikes, maxIntervalStartBurst, maxIntervalEndBurst, minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst):
    

    maxIntervalStartBurst, maxIntervalEndBurst = maxIntervalStartBurst*10, maxIntervalEndBurst*10 
    minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst = minIntervalBetweenBursts*10, minDurationOfBurst*10, minSpikeCountInBurst

    bursts = []
    i = 0
    k = 0
    while (i < len(spikes)-2):
        if(abs(spikes[i] - spikes[i+1]) <= maxIntervalStartBurst):
            bursts.append([spikes[i]])
            j = i+1
            while(abs(spikes[j] - spikes[j+1]) < maxIntervalEndBurst):
                bursts[k].append(spikes[j])
                j += 1
                if(j >= len(spikes) - 1): break
            i = j
            k += 1
        else:
            i += 1      


    valid_bursts = []
    
        
    for burst in bursts:
        if len(burst) > minSpikeCountInBurst and abs(burst[0] - burst[-1]) > minDurationOfBurst:
            valid_bursts.append(np.array([burst[0], burst[-1]]))

    merged_bursts = []

    if len(valid_bursts) > 1:
        i = 0
        initial_time = valid_bursts[i][0]
        final_time = valid_bursts[i][-1]
        
        while(i < len(valid_bursts) - 1):

            if abs(valid_bursts[i][-1] - valid_bursts[i+1][0]) < minIntervalBetweenBursts:
                final_time = valid_bursts[i+1][-1]
                if i+1 == len(valid_bursts) -1:
                    merged_bursts.append([initial_time, final_time ])

                    
            else:
                merged_bursts.append([initial_time, final_time ])
                if i < len(valid_bursts)-2:
                    initial_time = valid_bursts[i+1][0]
                    final_time = valid_bursts[i+1][-1]
                else:
                    merged_bursts.append([valid_bursts[i+1][0], valid_bursts[i+1][-1] ])
                    
            i+= 1
        
    elif len(valid_bursts) == 1:
        merged_bursts = valid_bursts
    
    else:
        #print('We don\'t get valid bursts from this set of parameters')
        merged_bursts = []
    return np.array(merged_bursts, dtype=object) # I have modified it in np.array


    return valid_bursts


def convert_burst_timestamps_to_binary(valid_bursts):

    binary_bursts = np.zeros(50_000)
    for item in valid_bursts:
        binary_bursts[item[0]:item[1]] = 1
    return binary_bursts



def binary_error_function(binary_lists): #comparison ideal- and 1 PREDICTED, for a single datapoint
    error = (sum(pow(binary_lists[0]-binary_lists[1],2))/np.count_nonzero(binary_lists[0])) # ideal - predicted
    return error

    

def merge_bursts(bursts, intervalBetweenTrains_in_s = 1):
    merged_bursts = []
    start_merging = False
    for i in range(len(bursts)-1):
        dist = abs(bursts[i][-1] - bursts[i+1][0])
        if(dist < intervalBetweenTrains_in_s*10_000):
            if start_merging == False:
                merged_bursts.append([bursts[i][0], bursts[i+1][-1]])
                start_merging = True     
            else:
                merged_bursts[-1][-1] = bursts[i+1][-1]
        elif start_merging:
            start_merging = False
        else:
            merged_bursts.append([bursts[i][0], bursts[i][-1]])

    return merged_bursts


def plot_burst_config(merged_bursts, burst_train_to_analyze, signal, threshold, maxIntervalStartBurst, maxIntervalEndBurst,
                         minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst, timestamp):
    global time_i, time_f

    merged = merged_bursts[burst_train_to_analyze]

    spikes, valid_bursts = get_spikes_and_bursts(signal, threshold, maxIntervalStartBurst, maxIntervalEndBurst, minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst)
    timeWindowInSeconds = 5
    time_window = int(timeWindowInSeconds*10_000)
    #startTimeInSeconds = merged[0] + ((merged[-1] - merged[0])/2) - (timeWindowInSeconds/ 2)
    startTimestamp = merged[0] + ((merged[-1] - merged[0])//2) - (time_window//2)
    


    time_i = int(startTimestamp)
    time_f = time_i + time_window 


    ####### find spikes and busts in the plot range ########################

    spikes_to_plot = []
    for spike in spikes:
        if(spike > time_i):
            spikes_to_plot.append(spike)
            if(spike > time_f):
                break


    bursts_to_plot = []
    if(time_i > valid_bursts[0][0]):
        i = 0
        dist = time_i - valid_bursts[0][0]
        while(dist > 0):
            i += 1
            dist = time_i - valid_bursts[i][0]
    else:
        i = 1

    j = i-1
    dist = time_f - valid_bursts[j][0]
    while(dist > 0):
        j += 1
        dist = time_f - valid_bursts[j][0]

    for k in range(i-1,j):
        bursts_to_plot.append(valid_bursts[k])


    ####### plot #########################################################

    fig = plt.figure(figsize=(12,7))

    for spike in spikes_to_plot:
        plt.axvline(spike,0,0.02, c = '#660033', lw = 0.75)
            
    for burst in bursts_to_plot:
        plt.hlines(-68,burst[0],burst[-1], colors = '#FF3333', lw = 9)
        #plt.hlines(-350,burst[0],burst[-1], colors = '#FF3333', lw = 9)



    plt.plot(np.array(timestamp[time_i:time_f])*10_000, signal[time_i:time_f], c = 'k', lw = 0.6, 
        label = '{}-{}-{}-{}-{}'.format(maxIntervalStartBurst, maxIntervalEndBurst, minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst))
    plt.axhline(0, c = 'k', lw = 1)
    plt.axhline(threshold, color =  'r', lw = 2)
    plt.axhline(-threshold, color = 'b', lw = 2)
    plt.xlabel('Time [s]', fontsize = 20)
    plt.ylabel('Voltage [\u03BCV]', fontsize = 20)
    plt.ylim(-75,75)

    #plt.ylim(-380, 380)
    plt.xlim(time_i, time_f)
    plt.yticks(np.arange(-75,76,25), fontsize = 20)

    #plt.yticks(np.arange(-380,380, 100), fontsize = 20)
    xticks = np.linspace(time_i, time_f,8)
    xticks_labels = [str(np.round(tick/10_000,2)) for tick in xticks]
    plt.xticks(xticks, labels = xticks_labels, fontsize = 20)
    plt.grid(ls = 'dotted')
    plt.legend(loc=0, fontsize = 18)
    plt.tight_layout()
    plt.show()
    plt.close()


def save_burst_and_params(filename_output, filename_output, filename, signal, threshold, well, channel, burst_train_to_analyze, merged_bursts, timestamp, 
                      maxIntervalStartBurst, maxIntervalEndBurst, minIntervalBetweenBursts, minDurationOfBurst, minSpikeCountInBurst):
    f = open(filename_output, 'a+')    
    string_to_append = f'{filename}\t{well}\t{channel}\t{risingEdge}\t{burst_train_to_analyze}\t{timestamp[time_i]}\t{timestamp[time_f]}\t'
    string_to_append += f'{maxIntervalStartBurst}\t{maxIntervalEndBurst}\t{minIntervalBetweenBursts}\t{minDurationOfBurst}\t{minSpikeCountInBurst}\n'
    f.write(string_to_append)
    f.close()    