"""
Generates plot with histogram showing burst_quality metric.
The histogram has three bars containing how many "Default", "Predict", or "Equal" bursts are classified as optimal, 
using the the output from 'GUI.py', stored in "GUI/".
"""


import pandas as pd 
import numpy as np
import matplotlib.pyplot as plt 


def find_model_type_indices(files, model_type):
    indices = []
    for i, file in enumerate(files):
        if file.find(model_type) != -1:
            indices.append(i)
    return np.array(indices)

model_types = ['spikes30', 'signal30', 'signal100']

classif_data = pd.read_csv('GUI/burst_quality.txt', sep = '\s+', header = None)

def swapPositions(list, pos1, pos2):
     
    list[pos1], list[pos2] = list[pos2], list[pos1]
    return list




number_of_differentBursts_per_modelType = []
files = classif_data.iloc[:,0].values
classif = classif_data.iloc[:,1].values


fig_size_dim    = 4*8
golden_ratio    = (1+np.sqrt(5))/2 + 3
fig_size        = (fig_size_dim, fig_size_dim/golden_ratio)

def plot_style():
    font_size       = fig_size_dim
    dpi             =  500

    params = {'figure.figsize': fig_size,
              'figure.dpi': dpi,
              'savefig.dpi': dpi,
              'font.size': font_size,
              'font.family': "Tahoma",
              'figure.titlesize': font_size,
              'legend.fontsize': font_size,
              'axes.labelsize': font_size,
              'axes.titlesize': font_size,
              'xtick.labelsize': font_size,
              'ytick.labelsize': font_size,
                }

    plt.rcParams.update(params)

plot_style()



fig, axs = plt.subplots(ncols=3, nrows=1)



for model_index, model_type in enumerate(model_types):
        
    indices_of_model_type = find_model_type_indices(files, model_type)    
    files_of_model_type = files[indices_of_model_type]
    classif_of_model_type = classif[indices_of_model_type]
    default_points = 0
    predicted_points = 0
    number_of_differentBursts_per_modelType.append([model_type, len(indices_of_model_type)])
    burst_class_list = []
    equal_points = 0
    for i in range(equal_points):
        burst_class_list.append('Equal')
    for i, file in enumerate(files_of_model_type):
        blueBurst = file[file.find('blue')+len('blue'):file.find('.png')]
        if classif_of_model_type[i] == 'Equal':
            burst_class_list.append('Equal')
            equal_points += 1
            default_points += 1
            predicted_points += 1
        elif classif_of_model_type[i] == 'Blue':
            if blueBurst == 'Default':
                burst_class_list.append('Default')
                default_points += 1
            else: 
                burst_class_list.append('Predicted')
                predicted_points += 1
        else:
            if blueBurst == 'Default':
                burst_class_list.append('Predicted')
                predicted_points += 1
            else:
                burst_class_list.append('Default')
                default_points += 1
    
    burst_class_list = np.sort(burst_class_list)
    burst_class_arr = np.array(burst_class_list)
    burst_class_list = swapPositions(burst_class_list, 1, -1)


    axs[model_index].hist(burst_class_list, bins = [0,1,2,3], align = 'left', rwidth = 0.8, color = '#2c69bf', edgecolor='black', lw = 1.2)
    #plt.title(model_type)
    axs[model_index].set_ylim(0,120)
    #axs[model_index].tick_params(axis='both', which='major', labelsize=14)


    for axx in axs:
        for axis in ['top','bottom','left','right']:
            axx.spines[axis].set_linewidth(fig_size_dim/16)
            axx.tick_params(width=fig_size_dim/16, which='both')
            axx.tick_params(length=fig_size_dim/3.2, which='major')
            axx.tick_params(length=fig_size_dim/5.33, which='minor')

      
    if np.where(burst_class_arr == 'Default')[0].shape[0] > np.where(burst_class_arr == 'Predicted')[0].shape[0]:
        axs[model_index].arrow(-0.4,np.where(burst_class_arr == 'Default')[0].shape[0],1.8,0, ls = '--', color = 'red')
        axs[model_index].fill_between([0.59,1.4], np.where(burst_class_arr == 'Default')[0].shape[0], np.where(burst_class_arr == 'Predicted')[0].shape[0], color = 'red', alpha = 0.1)



    else:
        axs[model_index].arrow(-0.4,np.where(burst_class_arr == 'Predicted')[0].shape[0],1.8,0, ls = '--', color = 'red')
        axs[model_index].fill_between([-0.41,0.4], np.where(burst_class_arr == 'Predicted')[0].shape[0], np.where(burst_class_arr == 'Default')[0].shape[0], color = 'red', alpha = 0.1)

axs[0].set_ylabel('Occurrences')
axs[0].set_title('Spike30P')
axs[1].set_title('Signal30P')
axs[2].set_title('Signal100P')

plt.show()