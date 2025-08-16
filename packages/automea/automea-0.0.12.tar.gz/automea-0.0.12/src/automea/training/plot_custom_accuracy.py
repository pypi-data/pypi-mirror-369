"""
Generates plot with custom accuracy metric.
The custom accuracy is plotted for each machine learning model trained: 'spikes30', 'signal30', and 'signal100', 
as a function of training epoch. For more than one training instance for each model, the average custom accuracy is
plotted as a solid line, accompanied by a shaded are spanning from min and max value of training accuracy for each epoch.
"""

import numpy as np
import matplotlib.pyplot as plt
import glob
import pandas as pd 

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


model_type = 'loss_accuracy_Raw100'

fig, axs = plt.subplots(ncols=3, nrows=1)
ax = axs


for model_index, model_type in enumerate(['spikes30', 'signal30', 'signal100']):
    axs[model_index].grid(True, which='both',linewidth=fig_size_dim/100)


    train_custom_acc = []
    val_custom_acc = []
    train_loss_acc = []
    val_loss_acc = []

    for i, file in enumerate(glob.glob('data/custom_accuracy/*.csv')):
        if file.find(model_type) != -1 and file.find('_train') != -1:
            loss_accuracy = pd.read_csv(file, header = None)
            val_accuracy = loss_accuracy.T[0].iloc[:].values
            train_accuracy = loss_accuracy.T[1].iloc[:].values
            val_loss = loss_accuracy.T[2].iloc[:].values
            train_loss = loss_accuracy.T[3].iloc[:].values
            val_custom = loss_accuracy.T[4].iloc[:].values
            train_custom = loss_accuracy.T[5].iloc[:].values
            val_custom_acc.append(val_custom)
            train_custom_acc.append(train_custom)
            val_loss_acc.append(val_loss)
            train_loss_acc.append(train_loss)


    val_custom = np.array(val_custom_acc)[:5]
    train_custom = np.array(train_custom_acc)[:5]
    val_loss = np.array(val_loss_acc)[:5]
    train_loss = np.array(train_loss_acc)[:5]


    best_model_overall = np.where(val_custom == val_custom.max())[0][0]

    val_custom_best = val_custom[best_model_overall]
    val_loss_best = val_loss[best_model_overall]
    train_loss_best = train_loss[best_model_overall]
    train_custom_best = train_custom[best_model_overall]

    val_custom_avg = np.zeros(val_custom.shape[1])
    train_custom_avg = np.zeros(train_custom.shape[1])
    val_loss_avg = np.zeros(val_loss.shape[1])
    train_loss_avg = np.zeros(train_loss.shape[1])


    val_custom_avg = np.median(val_custom, axis = 0)
    train_custom_avg = np.median(train_custom, axis = 0)
    val_loss_avg = np.median(val_loss, axis = 0)
    train_loss_avg = np.median(train_loss, axis = 0)

    val_custom_std = np.std(val_custom, axis = 0)
    train_custom_std = np.std(train_custom, axis = 0)
    val_loss_std = np.std(val_loss, axis = 0)
    train_loss_std = np.std(train_loss, axis = 0)
    
    epochs = np.arange(0,50)
    
    axs[model_index].fill_between(epochs, np.min(train_custom, axis = 0), np.max(train_custom, axis = 0), color = '#0d6fbf', alpha = 0.2)
    axs[model_index].plot(train_custom_avg, c = '#0d6fbf', label = 'train', lw = fig_size_dim/16)
    axs[model_index].fill_between(epochs, np.min(val_custom, axis = 0), np.max(val_custom, axis = 0), color = '#fcca3f', alpha = 0.2)
    axs[model_index].plot(val_custom_avg, c = '#fcca3f', label = 'val', lw = fig_size_dim/16)
    axs[model_index].set_xlabel('Epoch')
    axs[model_index].tick_params(labelsize = fig_size_dim)


for axx in axs:
        for axis in ['top','bottom','left','right']:
            axx.spines[axis].set_linewidth(fig_size_dim/16)
        axx.tick_params(width=fig_size_dim/16, which='both')
        axx.tick_params(length=fig_size_dim/3.2, which='major')
        axx.tick_params(length=fig_size_dim/5.33, which='minor')

axs[0].legend()
axs[0].set_ylabel('Custom Accuracy')
axs[0].set_title('Spike30P')
axs[1].set_title('Signal30P')
axs[2].set_title('Signal100P')

plt.tight_layout()
plt.show()

