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
    tolerance_val = 1.00
    if (current_P < tolerance_val*target): # change tolerance_val if you need more tolerance close to the target pressure
        start_harvard()
    else:
        stop_harvard()
        
        return None
    
def submit_callback(input_entry):  # Function used to push commands via GUI to the system
    input(input_entry)
    return None

def pressurize():
   labsmith.actuate_valve("2way1_red", 3) # pressurize control channel

def vent():
    labsmith.actuate_valve("2way1_red", 1) # depressurize control channel

def sample_to_chip():
    labsmith.actuate_valve("sample_valve", 1) # valve connects sample pump (harvard 11) to device
    
def reagents_to_chip():
    labsmith.actuate_valve("sample_valve", 3) # valve connects reagent pumps (custom syringe pumps) to device    
    
    
def arduino_port():
    
    ports = list(serial.tools.list_ports.comports())
    port_list = []
    for p in ports:
        print (p[1])
        if "Arduino Uno" in p.description:
            port_list.append(p[0])
            
    return port_list

def calc_delay(rate):
    if (rate == 0):
        delay = 100
    else:
        
        delay = dV*60 / 2/1.433/ rate # rate in microlitres per min
    
    return delay

def calc_steps(Vdesired):
    Vdesired = np.abs(Vdesired)
    no_steps = int(np.trunc(Vdesired/dV))
    
    return no_steps


def pump1(volume,rate):
    global board
    
    pump1_en.write(1)
    

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense

    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin1.write(1) # Direction is 1 for injection
    else:
        dir_pin1.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin1.write(1)
        time.sleep(delay)
        step_pin1.write(0)
        time.sleep(delay)
        print('pump1 step performed')
        
    pump1_en.write(0)
    return None
        
def pump2(volume,rate):
    global board

    pump2_en.write(1)

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin2.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin2.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin2.write(1)
        time.sleep(delay)
        step_pin2.write(0)
        time.sleep(delay)
        print('pump2 step performed')
        
    pump2_en.write(0)
    return None
        
def pump3(volume,rate):
    global board

 
    pump2_en.write(1)
    

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin3.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin3.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin3.write(1)
        time.sleep(delay)
        step_pin3.write(0)
        time.sleep(delay)
        print('pump2 step performed')
        
    pump3_en.write(0)
    return None
        
def pump4(volume,rate):
    global board
    
    #step_pin = board.get_pin('d:2:o')
    #dir_pin = board.get_pin('d:5:o')

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin4.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin4.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin4.write(1)
        time.sleep(delay)
        step_pin4.write(0)
        time.sleep(delay)
        print('pump4 step performed')
        
 
    return None

def pump5(volume,rate):
    global board
    
   
    #step_pin = board.get_pin('d:2:o')
    #dir_pin = board.get_pin('d:5:o')
 
    pump5_en.write(1)
    

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin5.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin5.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin5.write(1)
        time.sleep(delay)
        step_pin5.write(0)
        time.sleep(delay)
        print('pump5 step performed')
        
    pump5_en.write(0)
    return None

def pump6(volume,rate):
    global board
    
   
    #step_pin = board.get_pin('d:2:o')
    #dir_pin = board.get_pin('d:5:o')
 
    pump6_en.write(1)
    

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin6.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin6.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin6.write(1)
        time.sleep(delay)
        step_pin6.write(0)
        time.sleep(delay)
        print('pump6 step performed')
        
    pump6_en.write(0)
    return None


def pump7(volume,rate):
    global board
    
   

    pump7_en.write(1)
    

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin7.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin7.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin7.write(1)
        time.sleep(delay)
        step_pin7.write(0)
        time.sleep(delay)
        print('pump7 step performed')
        
    pump7_en.write(0)
    return None


def pump8(volume,rate):
    global board
    global stopswitch


    pump8_en.write(1)
    

    if volume ==0:
        no_steps =0
    else:
        no_steps = calc_steps(volume) # Calculated based on syringe diameter, pitch of thread and volume desired dispense
        
    if rate ==0:
        no_steps = 0
    
    delay = calc_delay(rate) # calculated by converting the uL/min input to s time delay between steps
    
    if (volume >=0):
        dir_pin8.write(1) # Injecton direction is HIGH for injection
    else:
        dir_pin8.write(0) # If negative volume given consider this as a withdrawal
    
    for i in range (0,no_steps):
        step_pin8.write(1)
        time.sleep(delay)
        step_pin8.write(0)
        time.sleep(delay)
        
        if stopswitch:
            
            break
        
        print('pump8 step performed')
        
    #pump8_en.write(0)
    return None
    
def stopswitch_ON():
    global stopswitch 
    global maintain_P
    maintain_P = False
    stopswitch = True
    
    return None

def stopswitch_OFF():
    global stopswitch
    stopswitch = False
    return None

def infuse_reagent(port_no):
    
    pump_functions = {
    1: pump1,
    2: pump2,
    3: pump3,
    4: pump4,
    5: pump5,
    6: pump6,
    7: pump7,
    8: pump8
    }
    
    global stopswitch
    stopswitch = False
    labsmith.actuate_valve("8way1", port_no) # switch to eppendorf in position port 2    
    reagents_to_chip()
    
    
    if port_no in pump_functions:
        pump_func = pump_functions[port_no]
        pump_func(100, 100)  # Inject 100 μL to chip with pump corresponding to the port that was called
    else:
        print(f"Error: No pump found for port {port_no}")



#--------- End of Functions ---------#
#################################
#################################
file_path = r"C:\Users\ONI\Desktop\fluidics\fluidics_gui"
os.chdir(file_path) # Change file_path variable to directory containing the pylabsmith.py file

#-------- Define Solutions reagents ----------#

solution_ports = pd.read_csv('solutions.csv', index_col=0, squeeze=True).to_dict() # Modify solutions.csv file with name of reagents in each port
solutions =  {v: k for k, v in solution_ports.items()}

#Setup labsmith


labsmith = PyLabsSmith()
labsmith.initialise_valve(valve_type = "AV801", valve_name = "8way1_green",
                          valve_manifold = 1, device_index = 0)

labsmith.initialise_valve(valve_type = "AV201", valve_name = "2way1_red",
                          valve_manifold = 1, device_index = 2) 

labsmith.initialise_valve(valve_type = "AV201", valve_name = "sample_valve",
                          valve_manifold = 1, device_index = 3)

labsmith.add_sensors()
labsmith.actuate_valve("8way1_green", 1) # initialize 8way valve to position port 1
labsmith.actuate_valve("2way1_red", 1) # Initialize pneumatic valve to position port 1
labsmith.actuate_valve("sample_valve", 1) # valve connects sample pump (harvard 11) to device

#Setup arduinos

#Find ports
ports = arduino_port() # Find Arduino Port
baud = 9600 # Define Baud Rate
syringe_type = '1 mL' # Syringe you use, will need to modify dV accordingly

#start pyfirmata and find define arduino boards
global board
board = pyfirmata.Arduino(ports[1])
it = pyfirmata.util.Iterator(board)
it.start()
time.sleep(1)

global board2
board2 = pyfirmata.Arduino(ports[0])
it = pyfirmata.util.Iterator(board2)
it.start()
time.sleep(1)

#Define all pins
global step_pin1, dir_pin1,step_pin2,dir_pin2,step_pin3,dir_pin3,step_pin4,dir_pin4

step_pin1 = board.get_pin('d:2:o')
dir_pin1 = board.get_pin('d:5:o')
step_pin2 = board.get_pin('d:3:o')
dir_pin2 = board.get_pin('d:6:o')
step_pin3 = board.get_pin('d:4:o')
dir_pin3 = board.get_pin('d:7:o')
step_pin4 = board.get_pin('d:12:o')
dir_pin4 = board.get_pin('d:13:o')

global step_pin5, dir_pin5,step_pin6,dir_pin6,step_pin7,dir_pin7,step_pin8,dir_pin8

step_pin5 = board2.get_pin('d:2:o')
dir_pin5 = board2.get_pin('d:5:o')
step_pin6 = board2.get_pin('d:3:o')
dir_pin6 = board2.get_pin('d:6:o')
step_pin7 = board2.get_pin('d:4:o')
dir_pin7 = board2.get_pin('d:7:o')
step_pin8 = board2.get_pin('d:12:o')
dir_pin8 = board2.get_pin('d:13:o')

#Disable motors for the time being
global pump1_en, pump2_en, pump3_en, pump4_en
pump1_en = board.get_pin('d:9:o')
pump2_en = board.get_pin('d:10:o')
pump3_en = board.get_pin('d:11:o')
pump4_en = board.get_pin('d:12:o')

pump5_en = board2.get_pin('d:9:o')
pump6_en = board2.get_pin('d:10:o')
pump7_en = board2.get_pin('d:11:o')
pump8_en = boar2.get_pin('d:12:o')

pump1_en.write(0)
pump2_en.write(0)
pump3_en.write(0)
pump4_en.write(0)



#--------- Global Variables ---------#


global const_P
const_P = True
global stopswitch
stopswitch = False
global dV
dV = 0.03588 # volume expended by 1 step of the stepper motor with the given microstepping settings

line_length = 600         # Define the size of the plot visuals. 0 if not needed. Value is in seconds
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


################## ROW 2 ##################


pressurize_button = Tk.Button(root,text="pressurize chip",fg="black",
                   height=2, command=lambda: pressurize()).grid(column=0, row=2, sticky = Tk.W, padx=0)

vent_button = Tk.Button(root,text="Vent",fg="black",
                   height=2, command=lambda: vent()).grid(column=0, row=2, sticky = Tk.W, padx=255)

sample_to_chip_button = Tk.Button(root,text="S_to_chip",fg="black",
                   height=2, command=lambda: sample_to_chip()).grid(column=0, row=2, sticky = Tk.W, padx=450)

reagents_to_chip_button = Tk.Button(root,text="FISH_to_chip",fg="black",
                   height=2, command=lambda: reagents_to_chip()).grid(column=0, row=2, sticky = Tk.W, padx=550)
                   
stopswitch_on_button = Tk.Button(root,text='stopswitch ON',fg="black",
                   height=2, command=lambda: stopswitch_ON()).grid(column=0, row=2, sticky = Tk.W, padx=700)

stopswitch_off_button = Tk.Button(root,text='stopswitch OFF',fg="black",
                   height=2, command=lambda: stopswitch_OFF()).grid(column=0, row=2, sticky = Tk.W, padx=850)




################## ROW 3 ##################
start_flow = Tk.Button(root,text='Start Pump',fg="black",
                   height=2, command=lambda: start_harvard()).grid(column=0, row=3, sticky = Tk.W, padx=0)

stop_flow = Tk.Button(root,text='Stop Pump',fg="black",
                   height=2, command=lambda: stop_targets()).grid(column=0, row=3, sticky = Tk.W, padx=100)

lock_target = Tk.Button(root,text='Lock Pressure',fg="black",
                   height=2, command=lambda: targetPressure()).grid(column=0, row=3, sticky = Tk.W, padx=200)

reverse_flow = Tk.Button(root,text='Withdraw Pump',fg="black",
                   height=2, command=lambda: reverse_target()).grid(column=0, row=3, sticky = Tk.W, padx=300)

reverse_flow = Tk.Button(root,text='Infuse Pump',fg="black",
                   height=2, command=lambda: infuse_target()).grid(column=0, row=3, sticky = Tk.W, padx=400)

const_flow = Tk.Button(root,text='Switch to constant flow',fg="black",
                   height=2, command=lambda: remove_targets()).grid(column=0, row=3, sticky = Tk.W, padx=650)

################################## ROW 4 ############################################
#####################################################################################
infuse_reagent1 = Tk.Button(root,text='Infuse port 1',fg="black",
                   height=2, command=lambda: infuse_reagent(1)).grid(column=0, row=4, sticky = Tk.W, padx=0)

infuse_reagent2 = Tk.Button(root,text='Infuse port 2',fg="black",
                   height=2, command=lambda: infuse_reagent(2)).grid(column=0, row=4, sticky = Tk.W, padx=0)

infuse_reagent3 = Tk.Button(root,text='Infuse port 3',fg="black",
                   height=2, command=lambda: infuse_reagent(3)).grid(column=0, row=4, sticky = Tk.W, padx=100)

infuse_reagent4 = Tk.Button(root,text='Infuse port 4',fg="black",
                   height=2, command=lambda: infuse_reagent(4)).grid(column=0, row=4, sticky = Tk.W, padx=200)

infuse_reagent5 = Tk.Button(root,text='Infuse port 5',fg="black",
                   height=2, command=lambda: infuse_reagent(5)).grid(column=0, row=4, sticky = Tk.W, padx=300)

infuse_reagent6 = Tk.Button(root,text='Infuse port 6',fg="black",
                   height=2, command=lambda: infuse_reagent(6)).grid(column=0, row=4, sticky = Tk.W, padx=400)

infuse_reagent7 = Tk.Button(root,text='Infuse port 7',fg="black",
                   height=2, command=lambda: infuse_reagent(7)).grid(column=0, row=4, sticky = Tk.W, padx=500)

infuse_reagent8 = Tk.Button(root,text='Infuse port 8',fg="black",
                   height=2, command=lambda: infuse_reagent(8)).grid(column=0, row=4, sticky = Tk.W, padx=600)





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