# -*- coding: utf-8 -*-
"""
Created on Wed Aug  3 17:03:47 2022

@author: turnerp
"""

import serial.tools.list_ports
import serial
from uProcess import uProcess # Import LabSmith Commands
import matplotlib.pyplot as plt
import time as time # Loads system time library
import serial # Accesses USB terminals.
import os.path # File path manager
import numpy as np # arrays and math
import re
import time




class PyLabsSmith:
    
    """Finds USB port, initialises connections to labsmith"""

    def __init__(self, device = "Silicon Labs CP210x", address = 14):
        
        self.device_dict = {}
        
        self.find_port(device)
        self.initialise_connection()
        

    def find_port(self, device):
        
        """finds USB port of labSmith"""
        
        ports = list(serial.tools.list_ports.comports())
        
        ports = [port for port in ports if device in port.description]
        
        if len(ports) > 0:
            
            self.port = int(str(ports[0]).split("(COM")[-1].replace(")",""))
            
        else:
            print("no device found")
            self.port = None

     
    def initialise_connection(self, verbose = True):
        
        """finds devices, reports active devices + device addresses, adds device info to a dictionary"""
        
        if self.port != None:
        
            self.EIB = uProcess.CEIB()
            self.EIBopen = self.EIB.InitConnection(self.port) # USB Port
            self.port = self.EIB.GetComPort()
            
            device_list = self.EIB.CmdCreateDeviceList()
            
            if len(device_list) != 0:
            
                self.device_dict = {}
                
                for i in range(len(device_list)):
                    
                    device_object = device_list[i]
    
                    device_name = type(device_object).__name__
                    device_address = device_object.GetAddress()
                    
                    device_type = "unkown"
                    
                    if device_name == "C4VM":
                        device_type = "valve_manifold"
                    elif device_name == "CSyringe":
                        device_type == "syringe"
                    elif device_name == "C4AM":
                        device_type = 'sensor_manifold'

                    
                    self.device_dict[i] = dict(device_object = device_object,
                                                device_address = device_address,
                                                device_name = device_name,
                                                device_type = device_type)
                    
                    if verbose:
                        print(f"Found device {i}: {device_name} at address {device_address}")
                        
                time.sleep(1)
                
            else:
                raise RuntimeError("No devices found, unplug/plug the device?")
                
                

    def initialise_valve(self,
                          valve_type = "AV801",
                          valve_name = "valve1",
                          valve_manifold = 1,
                          device_index = 0):
        
        valve_dict = self.device_dict[device_index]
        device_name = valve_dict["device_name"]
        
        if device_name == "C4VM":
    
            valve_address = valve_dict["device_address"]
            
           
            self.device_dict[valve_name] = dict(valve_type = valve_type,
                                                valve_manifold = valve_manifold,
                                                valve_address = valve_address,
                                                valve_position = None,
                                                valve_status = None)
    
            self.actuate_valve(valve_name, valve_position = 1, verbose = False)
            
            valve_status = self.device_dict[valve_name]["valve_status"]
            
            if valve_status == "Stuck!":
                
                print(f"Cannot connect to the valve on manifold {valve_manifold}")
                
                self.device_dict.pop(valve_name)
                
            elif valve_status == "Indeterminate position":
                
                raise RuntimeError("Could not actuate valve, restart python interpreter?")
                
                self.device_dict.pop(valve_name)
                 
            else:
        
                print(f"Initialised {valve_type} '{valve_name}' on manifold {valve_manifold} at address {valve_address}")
        
        else:
            
            raise RuntimeError("Device is not a known valve manifold, chnage the device index?")
        
        
    def initialise_syringe(self, syringe_name = "Syringe1", device_index = 1, calibrate = False):
        
        syringe_dict = self.device_dict[device_index]
        device_name = syringe_dict["device_name"]
        
        if device_name == "CSyringe":
    
            syringe_address = syringe_dict["device_address"]
            
            syringe = uProcess.CSyringe(self.EIB,syringe_address)
            
            syringe_status = syringe.CmdGetStatus()
            
            if syringe_status == True:
            
                max_volume = syringe.GetMaxVolume()
                flow_rate_max = syringe.GetMaxFlowrate()
                flow_rate_min = syringe.GetMinFlowrate()
                
                syringe.CmdShowDevice(True)
                time.sleep(1)
                syringe.CmdShowDevice(False)
                
                self.device_dict[syringe_name] = dict(syringe_name = syringe_name,
                                                      syringe_address = syringe_address,
                                                      valve_position = None,
                                                      valve_status = None,
                                                      max_volume = max_volume,
                                                      flow_rate_max = flow_rate_max,
                                                      flow_rate_min = flow_rate_min)
                
                
                print(f"Initialised Syringe '{syringe_name}' at address {syringe_address}")
    
                if calibrate:
                    
                    self.calibrate_syringe(syringe_name)
    
            else:
                
                print("Syringe not available?")
                
        else:
            
            raise RuntimeError("Device is not a known syringe, change the device index?")
            
        
    def initialise_sensors(self,
                          valve_type = "psensor",
                          valve_name = "psensor1",
                          sensor_manifold = 1,
                          device_index = 0):
        
        valve_dict = self.device_dict[device_index]
        device_name = valve_dict["device_name"]
        
        if device_name == "C4AM":
    
            valve_address = valve_dict["device_address"]
            
           
            self.device_dict[valve_name] = dict(valve_type = valve_type,
                                                valve_manifold = valve_manifold,
                                                valve_address = valve_address,
                                                valve_position = None,
                                                valve_status = None)
    
            
            
            
            valve_status = self.device_dict[valve_name]["valve_status"]
            
            if valve_status == "Stuck!":
                
                print(f"Cannot connect to the valve on manifold {valve_manifold}")
                
                self.device_dict.pop(valve_name)
                
            elif valve_status == "Indeterminate position":
                
                raise RuntimeError("Could not actuate valve, restart python interpreter?")
                
                self.device_dict.pop(valve_name)
                 
            else:
        
                print(f"Initialised {valve_type} '{valve_name}' on manifold {valve_manifold} at address {valve_address}")
        
        else:
            
            raise RuntimeError("Device is not a known valve manifold, chnage the device index?")    
        
        
    def open_syringe(self, syringe_name, volume = 10, max_volume = True):
        
        syringe_dict = self.device_dict[syringe_name]
        syringe_address = syringe_dict["syringe_address"]
        
        max_volume = syringe_dict["max_volume"]
        
        syringe = uProcess.CSyringe(self.EIB,syringe_address)
        syringe.CmdSetFlowrate(80)
        syringe.CmdMoveToVolume(max_volume)
        
        # print(syringe.CmdGetVolume())
    
        
    
    
    def close_syringe(self, syringe_name):
        
        syringe_dict = self.device_dict[syringe_name]
        syringe_address = syringe_dict["syringe_address"]
        
        max_volume = syringe_dict["max_volume"]
        
        syringe = uProcess.CSyringe(self.EIB,syringe_address)
        
        syringe.CmdMoveToVolume(0)
        
        # print(syringe.CmdGetVolume())
        
        
        
    def inject_volume(self, syringe_name, Vinject, Flowrate):
        """Push syringe.

        Keyword arguments:
        syringe_name -- name given to the syringe look at initialise syringe
        Vinject -- Volume to be pushed (uL)
        Flowrate -- Rate at which syringe pushes (uL/min)
        """
        
        syringe_dict = self.device_dict[syringe_name]
        syringe_address = syringe_dict["syringe_address"]
        
        max_volume = syringe_dict["max_volume"]
        
        syringe = uProcess.CSyringe(self.EIB,syringe_address)
        V = syringe.CmdGetVolume()
        
        Vtarget = V-Vinject
        if Vtarget <0:
            Vtarget = 0
            print('Not enough volume left in syringe')
        
        syringe.CmdSetFlowrate(Flowrate)
        syringe.CmdMoveToVolume(Vtarget)
        
        
    
    def withdraw_volume(self, syringe_name, Vinject, Flowrate):
        """Aspirate syringe.

        Keyword arguments:
        syringe_name -- name given to the syringe look at initialise syringe
        Vinject -- Volume to be aspirated (uL)
        Flowrate -- Rate at which syringe aspirates (uL/min)
        """
        
        syringe_dict = self.device_dict[syringe_name]
        syringe_address = syringe_dict["syringe_address"]
        
        max_volume = syringe_dict["max_volume"]
        
        syringe = uProcess.CSyringe(self.EIB,syringe_address)
        V = syringe.CmdGetVolume()

        Vtarget = V+Vinject
        if Vtarget > max_volume:
            Vtarget = max_volume
            print('Already filled up')
        
        syringe.CmdSetFlowrate(Flowrate)
        syringe.CmdMoveToVolume(Vtarget)
        
        # print(syringe.CmdGetVolume())
        
    
    def current_position_syringe(self, syringe_name):
        """Get position of syringe.

        Keyword arguments:
        syringe_name -- name given to the syringe look at initialise syringe
        """
        syringe_dict = self.device_dict[syringe_name]
        syringe_address = syringe_dict["syringe_address"]
        syringe = uProcess.CSyringe(self.EIB,syringe_address)
        V = syringe.CmdGetVolume()
        
        print({V})
            
            
            
    def calibrate_syringe(self, syringe_name):
        
        syringe_dict = self.device_dict[syringe_name]
        
        syringe_address = syringe_dict["syringe_address"]
        
        syringe = uProcess.CSyringe(self.EIB,syringe_address)
        
        syringe.CmdAutoCal()
        

    
    def actuate_valve(self,
                      valve_name,
                      valve_position,
                      verbose = True):
        
        valve_dict = self.device_dict[valve_name]
        
        valve_type = valve_dict["valve_type"]
        valve_manifold = valve_dict["valve_manifold"]
        valve_address = valve_dict["valve_address"]
        
        if verbose == True:
            print(f"Setting valve '{valve_name}' to port {valve_position}")
        
        valve_object = uProcess.C4VM(self.EIB,valve_address)
        
        V1 = valve_object.GetValve(valve_manifold)
        valve_status = V1.GetStatus()
        
        moving = True
        
        while moving == True:

            if valve_type == "AV801":
                
                valve_object.CmdSelect(valve_manifold,valve_position)
            
                valve = valve_object.GetValve(valve_manifold)
                valve_status = valve.GetSelectorStatusText()
            
            if valve_type == "AV201":
                
                valve_object.CmdSetValves(0,0,0,valve_position)
                
                valve = valve_object.GetValve(valve_manifold)
                valve_status = valve.GetStatusText()
                
            if 'Moving' not in valve_status:
            
                moving = False
                
                valve_dict["valve_status"] = valve_status
                valve_dict["valve_position"] = valve_position


    def get_valve_status(self, valve_name):
    
        valve_dict = self.device_dict[valve_name]
        
        valve_type = valve_dict["valve_type"]
        valve_manifold = valve_dict["valve_manifold"]
        
        if valve_type == "AV801":
            
            valve = self.valve_manifold.GetValve(valve_manifold)
            valve_status = valve.GetSelectorStatusText()
            
        if valve_type == "AV201":
                    
            valve = self.valve_manifold.GetValve(valve_manifold)
            valve_status = valve.GetStatusText()
            
        
    def close_connection(self):
            self.EIB.CloseConnection()
            
            
            
    def get_sensor_status(self, valve_name):
    
        sensor_dict = self.device_dict[valve_name]
        
        valve_type = valve_dict["valve_type"]
        valve_manifold = valve_dict["valve_manifold"]
        
        if valve_type == "AV801":
            
            valve = self.valve_manifold.GetValve(valve_manifold)
            valve_status = valve.GetSelectorStatusText()
    
    
    def add_sensors(self):
        global psensors
        psensors = uProcess.C4AM(self.EIB,81)
        add_pressure_sensor = self.EIB.New4AM(81)
    
    
    def get_pchip(self):
        global psensors
        psensors.CmdGetStatus()
        read_sensor = str(psensors.GetSensor(2))
        
        pchip = float(read_sensor.split(' ')[-2])
        pchip = pchip/100 # Conversion from kPa to Bar
        return pchip
    
    def get_pquake(self):
        global psensors
        psensors.CmdGetStatus()
        read_sensor = str(psensors.GetSensor(3))
        
        pquake = float(read_sensor.split(' ')[-2])
        pquake = pquake/100 # Conversion from kPa to Bar
        return pquake
    
# reader.close_connection()





