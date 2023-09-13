from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import PySimpleGUI as sg
import matplotlib, time, threading
matplotlib.use('TkAgg')
import matplotlib.pyplot as plt
import numpy as np
import random
import pandas as pd

def fig_maker(window,x): # this should be called as a thread, then time.sleep() here would not freeze the GUI
    plt.plot(x)
    window.write_event_value('-THREAD-', 'done.')
    time.sleep(0.01)
    return plt.gcf()


def draw_figure(canvas, figure, loc=(0, 0)):
    figure_canvas_agg = FigureCanvasTkAgg(figure, canvas)
    figure_canvas_agg.draw()
    figure_canvas_agg.get_tk_widget().pack(side='top', fill='both', expand=1)
    return figure_canvas_agg


def delete_fig_agg(fig_agg):
    fig_agg.get_tk_widget().forget()
    plt.close('all')

# Establish the different example devices on the house (power, (min_usage_time,max_usage_time (mins) ))
electronic_devices = {
    "Light" : [10,(1,300)],
    "oven" : [1500,(5,120)],
    "AC" : [1000,(60,300)],
    "Computer": [800,(5,300)],
    "Freezer": [300,(300,600)],
    "TV":[200,(5,300)],
    "MicroWave":[1100,(1,5)]
}

if __name__ == '__main__':
    # define the data array 
    power_data = np.array([0])
    current_power = 0

    # define the window layout
    layout = [[sg.Button('update'), sg.Button('Stop', key="-STOP-"), sg.Button('Exit', key="-EXIT-")],
              [sg.Radio('Keep looping', "RADIO1", default=True, size=(12,3),key="-LOOP-"),sg.Radio('Stop looping', "RADIO1", size=(12,3), key='-NOLOOP-')],
              [sg.Checkbox(i, default=False, size=(12,3),key=f"{i}") for i in electronic_devices],
              [sg.Text('Plot test', font='Any 18')],             
              [sg.Canvas(size=(500,500), key='canvas')]]

    # create the form and show it without the plot
    window = sg.Window('Demo Application - Embedding Matplotlib In PySimpleGUI',
                       layout, finalize=True)

    fig_agg = None
    while True:
        event, values = window.read()
        if event is None:  # if user closes window
            break
        
        if event == "update":
            if fig_agg is not None:
                    delete_fig_agg(fig_agg)
            fig = fig_maker(window,power_data)
            fig_agg = draw_figure(window['canvas'].TKCanvas, fig)

        if event == "-THREAD-":
            print('Acquisition: ', values[event])
            time.sleep(0.1)
            if values['-LOOP-'] == True:
                if fig_agg is not None:
                    delete_fig_agg(fig_agg)
                fig = fig_maker(window,power_data)
                current_power = sum([electronic_devices[i][0] for i in values if i in electronic_devices and values[i] == True]) + random.random()*2
                power_data = np.append(power_data,current_power)
                fig_agg = draw_figure(window['canvas'].TKCanvas, fig)
                window.Refresh()
        
        if event == "-STOP-":
            window['-NOLOOP-'].update(True)
            df = pd.DataFrame(power_data)
            df['Minute'] = df.index
            df.to_csv('data-generator/data/example_02.csv',header=['Power','Minute'],index=False)
        
        if event == "-EXIT-":
            break
            
    
    window.close()