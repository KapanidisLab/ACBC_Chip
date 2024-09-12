# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-
"""
Perform ACBC experiments using LabSmith

@author: Dr. Stelios Chatzimichail, PDRA
         Kapanidis Group, Oxford, 2022.
"""


#-------- LabSmith Imports ----------#
import serial.tools.list_ports
import serial
from uProcess import uProcess # Import LabSmith Commands
import matplotlib.pyplot as plt
import time as time # Loads system time library
import serial # Accesses USB terminals.
import os.path # File path manager
import numpy as np # arrays and math
from simple_pid import PID
import pandas as pd
from PyLabSmith import PyLabsSmith

#--------- Functions ---------#

def find_port():
    
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print (p[1])
        if "Silicon Labs CP210x" in p.description:
            test = p[0]
            print('The labsmith USB port is',test)
    return test

def find_harvard_pump():
    
    ports = list(serial.tools.list_ports.comports())
    for p in ports:
        print (p[1])
        if "USB Serial Device" in p.description:
            test = p[0]
            print('The pump11 port is',test)
    return test

def withdraw_from_port(port_number):
    stop_harvard()
    if port_number !=1:    
        labsmith.actuate_valve("8way1_green", port_number)
    
    reverse_target()
    start_harvard()
    return None

def infuse_reagent(port_number):
    withdraw_from_port(port_number)
    time.sleep(10) # Withdraw from vial sample for 10 seconds, this value will need to be adjusted depending on flow-rate set on harvard pump
    inject_to_chip()

def inject_to_chip():
    stop_harvard()
    labsmith.actuate_valve("8way1_green", 8) # 1 is the number of the chip port
    time.sleep(2)
    labsmith.actuate_valve("8way1_green", 1) # 1 is the number of the chip port
    infuse_target()
    
    start_harvard()
    time.sleep(60) # Inject to chip for 60 seconds, this value will need to be adjusted depending on flow-rate set on harvard pump
    stop_harvard()

def p_quake():
    pquake = labsmith.get_pquake()
    return pquake

def p_chip():
    pchip = labsmith.get_pchip()
    return pchip

def start_harvard():
    global reverse

    if (reverse == False):
        ser.write(str.encode('irun' + '\r\n'))
    else:
        ser.write(str.encode('wrun' + '\r\n'))

def stop_harvard():
    ser.write(str.encode('stop' + '\r\n'))
    

def reverse_target():
    global reverse 
    reverse = True
    return reverse    

def infuse_target():
    global reverse
    reverse = False
    return reverse
  

def targetPressure():
    global check_target
    check_target = True
    return check_target


def remove_targets():
    global remove_target
    remove_target = True
    
    return remove_target

def stop_targets():
    global stop_target
    stop_target = True
    return stop_target


def constPflow(target):
    current_P = p_chip()
    
    if (current_P < 1.00*target): # 99% for tolerance
        start_harvard()
    else:
        stop_harvard()
        
        return None
    

def submit_callback(input_entry):  # Function used to push commands via GUI to the system
    input(input_entry)
    return None

#--------- End of Functions ---------#
#################################
#################################
PATH = r"C:\Users\ONI\Desktop\fluidics\fluidics_gui"
os.chdir(PATH) # Change PATH variable to directory containing the pylabsmith.py file

#-------- Define Solutions and Wetware ----------#

dead_volume = 50 # input system dead volume in microlitres
chip_volume = 5 # input chip volume in microlitres

solution_ports = pd.read_csv('solutions.csv', index_col=0, squeeze=True).to_dict() # Modify solutions.csv file with name of reagents in each port
solutions =  {v: k for k, v in solution_ports.items()}



global const_P
const_P = True


labsmith = PyLabsSmith()
labsmith.initialise_valve(valve_type = "AV801", valve_name = "8way1_green",
                          valve_manifold = 1, device_index = 0)

labsmith.add_sensors()
labsmith.actuate_valve("8way1_green", 1)



#--------- Global Variables ---------#
line_length = 600         # Define the size of the plot visuals. 0 if not needed. Value is in seconds
runtime = 2
inter = 1               # interval for animation


##################################
##################################


pump11_port = find_harvard_pump()

# Configure serial connection
ser = serial.Serial(
    port=pump11_port,
    baudrate=9600,
    parity=serial.PARITY_ODD,
    stopbits=serial.STOPBITS_TWO,
    bytesize=serial.SEVENBITS
)

ser.isOpen()

input = 'stop'
out = ''

# Send the input to the device
# Note the carriage return and line feed characters \r\n will depend on the device
ser.write(str.encode(input + '\r\n'))

# Wait 1 sec before reading output
time.sleep(1)
while ser.inWaiting() > 0:
    out += ser.read(1).decode("utf-8") 

# Print the response
if out != '':
    print(out)



    
#--------- GUI Imports ---------#

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import tkinter as Tk
import matplotlib.pyplot as plt
import matplotlib.animation as animation
#--------- End of GUI Imports ---------#

#--------- Numerical Imports ---------#

start = time.time()     # Document program start-time
np.set_printoptions(threshold=np.inf) # If needed to handle large arrays

################### Define filename structure #################
cwd = os.getcwd() # Get present directory location
save_path = time.strftime('%m-%d-%Y_%H_%M_%S') # Timestamp run date and time of experiment; use underscore instead of spaces

# Create datapath for saved files

os.mkdir(save_path)
os.mkdir(save_path + '\\images')
spectra_path = save_path + '\\images'


# Create file to which flow data will be read and store initial value
filename_flow = os.path.join(save_path,'Flow.txt')
#filename_flow = "{0}_{1}.txt".format("Flow",timeStr)
ffile=open(filename_flow,"a+")
ffile.write('0'+'  '+'0' + "\n")
ffile.close()

# Create figure structure with chromatogram and pressure plots
fig = plt.figure()
ax_S = fig.add_subplot(2, 2, 1)
ax_P = fig.add_subplot(2, 2, 2)

ax_flow = fig.add_subplot(2, 2, 4)

# Format plot
plt.xticks(rotation=45, ha='right')
plt.subplots_adjust(bottom=0.30)
ax_P.set_xlabel('Time (s)')
ax_P.set_ylabel('Pressure (bar)')
ax_S.set_xlabel('Time (s)')
ax_S.set_ylabel('Pressure (bar)')
ax_S.title.set_text('Quake Valve Pressure Plot')
ax_P.title.set_text('Chip Backpressure plot')

ax_flow.set_xlabel('Time (s)')
ax_flow.set_ylabel('Flow (uL / min)')
ax_flow.title.set_text('Flow Graph')

# Define arrays used to store sensor values
xs_S = [] # time for sensor 1
ys_S = [] # sensor 1 vals
xs_P = [] # time for sensor 2
ys_P = [] # sensor 2 vals
xs_flow = [] # Flow Sensor Xs 
ys_flow = [] # Flow Sensor Ys

# parameter initializations

pchip = p_chip()
pquake = p_quake()
global target
target = -100

global reverse
reverse = False

global remove_target
remove_target = False

global stop_target
stop_target = False

global check_target
check_target = False
###############################3


filename_S = os.path.join(save_path,'PQuake.txt')         
s=open(filename_S,"a+")
s.write('0'+'  '+str(pquake) + "\n")
s.close()

# Create file to which pressure data will be read and store initial value
filename_P = os.path.join(save_path,'PChip.txt')
#filename_P = "{0}{1}.txt".format("Pressure",timeStr)
f=open(filename_P,"a+")
f.write('0'+'  '+ str(pchip))
f.write("\n")
f.close()

# Adjust appearance of subplots to specifications of user
plt.subplots_adjust(left=None, bottom=0.15, right=None, top=None, wspace=0.65, hspace=0.65)

## Define Line Objects for each subplot
line_S, = ax_S.plot ([],[])
line_P,= ax_P.plot ([],[])
line_flow, = ax_flow.plot ([],[])

#--------- Define Initialization Function for the Animation ---------#

def init():
    
    
    return line_S, line_P, line_flow

#--------- Animation Part Begins ---------#
# This function is called periodically from FuncAnimation
def animate(i, xs_P, ys_P, xs_S, ys_S):
    
    global check_target
    global target 
    global remove_target
    global stop_target
    global reverse
    
    if remove_target:
        remove_target = False
        stop_target = False
        target = 100
          
    if const_P:
        constPflow(target)
        if check_target:
            check_target = False
            stop_target = False
            target = p_chip()
    
    if stop_target:
        target = 0

    end = time.time() # Current time
    exp_time = end-start # Experiment time
    pquake = p_quake() # Retrieve pressure from pneumatic valve channel
    ys_S.append(pquake) # Store pressure in pneumatic valve channel
    xs_S.append(exp_time) # Store exp time
    pchip = p_chip() # Retrieve pressure from flow channel
    xs_P.append(exp_time) # Store exp time
    ys_P.append(pchip) # Store pressure in flow channel

   
    # GUI visualization of plots
    
    if (line_length > 0):
        xs_S_short = xs_S[-line_length:]
        ys_S_short = ys_S[-line_length:]
        xs_P_short = xs_P[-line_length:]
        ys_P_short = ys_P[-line_length:]
        xs_flow_short = xs_flow[-line_length:]
        ys_flow_short = ys_flow[-line_length:]
    else:
        xs_S_short = xs_S
        ys_S_short = ys_S
        xs_P_short = xs_P
        ys_P_short = ys_P
        xs_flow_short = xs_flow
        ys_flow_short = ys_flow

    # Update Line Object
    line_S.set_data(xs_S_short,ys_S_short)
    line_P.set_data(xs_P_short,ys_P_short)

    line_flow.set_data(xs_flow_short,ys_flow_short)
    # Update Axis Limits
    ax_S.relim()
    ax_S.autoscale_view()
    ax_P.relim()
    ax_P.autoscale_view()

    ax_flow.relim()
    ax_flow.autoscale_view()

    f=open(filename_S,"a+")
    f.write(str(end-start)+'  '+ str(pquake))
    f.write("\n")
    f.close()
    s=open(filename_P,"a+")
    s.write(str(end-start)+'  '+ str(pchip)+"\n")
    s.close()

root = Tk.Tk()

# -------------------------- GUI Commands -------------------------- #


    
def pause_animation():
    ani.event_source.stop()

def resume_animation():
    ani.event_source.start()

def set_integration_time():
    
    ani.event_source.stop()

def peakfinder():
    ani.event_source.stop()

def flow_value():
    ani.event_source.stop()
def stop_measurement():
    ani.event_source.stop()




# -------------------------- GUI Design Grid -------------------------- #

################## ROW 1 ##################
label = Tk.Label(root,text="ACBC Gui").grid(column=0, row=0)
quit_button = Tk.Button(root,text="QUIT",fg="black",width = 10,
                   height=2, command=pause_animation).grid(column=0, row=1, sticky = Tk.W)

pause_button = Tk.Button(root,text="Pause",fg="black",width = 10,
                   height=2, command=pause_animation).grid(column=0, row=1, sticky = Tk.W, padx=83)


resume_button = Tk.Button(root,text="Resume",fg="black",width = 10,
                   height=2, command=resume_animation).grid(column=0, row=1, sticky = Tk.W, padx=166)


save_button = Tk.Button(root,text="Save Session",fg="black",width = 15,
                   height=2, command=pause_animation).grid(column=0, row=1, sticky = Tk.W, padx=249)




################## ROW 3 ##################


pressurize_button = Tk.Button(root,text="pressurize chip",fg="black",
                   height=2, command=lambda: pressurize()).grid(column=0, row=3, sticky = Tk.W, padx=0)

vent_button = Tk.Button(root,text="Vent",fg="black",
                   height=2, command=lambda: vent()).grid(column=0, row=3, sticky = Tk.W, padx=255)



################## ROW 5 ##################
start_flow = Tk.Button(root,text='Start Pump',fg="black",
                   height=2, command=lambda: start_harvard()).grid(column=0, row=5, sticky = Tk.W, padx=0)

stop_flow = Tk.Button(root,text='Stop Pump',fg="black",
                   height=2, command=lambda: stop_targets()).grid(column=0, row=5, sticky = Tk.W, padx=100)

lock_target = Tk.Button(root,text='Lock Pressure',fg="black",
                   height=2, command=lambda: targetPressure()).grid(column=0, row=5, sticky = Tk.W, padx=200)

reverse_flow = Tk.Button(root,text='Withdraw Pump',fg="black",
                   height=2, command=lambda: reverse_target()).grid(column=0, row=5, sticky = Tk.W, padx=300)

reverse_flow = Tk.Button(root,text='Infuse Pump',fg="black",
                   height=2, command=lambda: infuse_target()).grid(column=0, row=5, sticky = Tk.W, padx=400)

const_flow = Tk.Button(root,text='Switch to constant flow',fg="black",
                   height=2, command=lambda: remove_targets()).grid(column=0, row=5, sticky = Tk.W, padx=650)

################################## ROW 5 ############################################
#####################################################################################

infuse_reagent2 = Tk.Button(root,text='Infuse port 2',fg="black",
                   height=2, command=lambda: infuse_reagent(2)).grid(column=0, row=6, sticky = Tk.W, padx=0)

infuse_reagent3 = Tk.Button(root,text='Infuse port 3',fg="black",
                   height=2, command=lambda: infuse_reagent(3)).grid(column=0, row=6, sticky = Tk.W, padx=100)

infuse_reagent4 = Tk.Button(root,text='Infuse port 4',fg="black",
                   height=2, command=lambda: infuse_reagent(4)).grid(column=0, row=6, sticky = Tk.W, padx=200)

infuse_reagent5 = Tk.Button(root,text='Infuse port 5',fg="black",
                   height=2, command=lambda: infuse_reagent(5)).grid(column=0, row=6, sticky = Tk.W, padx=300)

infuse_reagent6 = Tk.Button(root,text='Infuse port 6',fg="black",
                   height=2, command=lambda: infuse_reagent(6)).grid(column=0, row=6, sticky = Tk.W, padx=400)

infuse_reagent7 = Tk.Button(root,text='Infuse port 7',fg="black",
                   height=2, command=lambda: infuse_reagent(7)).grid(column=0, row=6, sticky = Tk.W, padx=500)

infuse_reagent8 = Tk.Button(root,text='Infuse port 8',fg="black",
                   height=2, command=lambda: infuse_reagent(8)).grid(column=0, row=6, sticky = Tk.W, padx=600)


################################################################################################################

# Create GUI canvas
canvas = FigureCanvasTkAgg(fig, master=root)
canvas.get_tk_widget().grid(column=0,row=7, sticky = Tk.W)

# -------------------------- Animation Command -------------------------- #
ani = animation.FuncAnimation(fig, animate, init_func=init, blit = False, fargs=(xs_P, ys_P, xs_S, ys_S), interval=inter)

Tk.mainloop()
 # Stop pump
stop_harvard()

# Close serial 
ser.close()
labsmith.close_connection()