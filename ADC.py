import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import math
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
import pandas as pd
from datetime import datetime

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
ads.gain = 2/3

# Create single-ended input
chan = [AnalogIn(ads, ADS.P0), AnalogIn(ads, ADS.P1), AnalogIn(ads, ADS.P2), AnalogIn(ads, ADS.P3)]

threshold = 10
diameter = 0.013

time_data = []
voltage_data_chan0,voltage_data_chan1,voltage_data_chan2,voltage_data_chan3 = [],[],[],[]
weight_data_chan0,weight_data_chan1,weight_data_chan2,weight_data_chan3 = [],[],[],[]
pressure_data_chan0,pressure_data_chan1,pressure_data_chan2,pressure_data_chan3 = [],[],[],[]

weight_buffer = [[0.0,0.0],[0.0,0.0],[0.0,0.0],[0.0,0.0]]
weight_drift = [0,0,0,0]

def cal_resistance(voltage):
    ans = []
    for vol in voltage:
        result = (10000)*((5.030/vol)-1)
        ans.append(result)
    return ans

def cal_voltage(chan):
    ans = []
    for terminal in chan:
        result = terminal.voltage
        if(result <= 0):
            result = 0.1
        ans.append(result)
    return ans

def cal_weight(resistance):
    ans = []
    for res in resistance:
        # ~ result_1 = math.exp(-(math.log((resistance+16.8104)/155170)/0.7013))
        # ~ result_2 = (6.7132e7)*(resistance**(-1.6009))+77.7879
        # ~ result_3 = (1.0686e8)*(resistance**(-1.6811))+32.6381
        # ~ result_4 = (-3.4230e6)*np.exp(1.7714e4*(1/resistance)) + (3.4229e6)*np.exp(1.7749e4*(1/resistance))
        result = (1.0686e8)*(res**(-1.6811))+32.6381
        ans.append(result)
    return ans
    
def account_drift(weight):
    global weight_buffer
    global weight_drift
    slope = []
    for i in range(len(weight_buffer)):
        weight_buffer[i][0] = weight[i]
        slope.append((weight_buffer[i][0] - weight_buffer[i][1])/1)
        if(abs(slope[i]) >= threshold):
            weight_drift[i] = weight[i]
        weight_buffer[i][1] = weight_buffer[i][0]

def cal_pressure(weight_drift, diameter):
    ans = []
    radius = diameter/2
    for wd in weight_drift:
        result = ((wd/1000)*9.81)/((np.pi)*(radius**2))/1000
        ans.append(result)
    return ans

try:
    while True:
        timestamp = datetime.now()
        voltage = cal_voltage(chan)
        resistance = cal_resistance(voltage)
        weight = cal_weight(resistance)
        account_drift(weight)
        pressure = cal_pressure(weight_drift,diameter)
        
        print(f"weights: {weight_drift}")
        #print(f"voltage {voltage:.3f} and weight_1 {weight_1:.2f} and weight_2 {weight_2:.2f} weight_3 {weight_3:.2f}")
        #print(f"output = {output_weight:.3f}g and pressure {output_pressure:.2f}Kpa\n")
        
        time_data.append(timestamp)
        voltage_data_chan0.append(round(voltage[0],3))
        voltage_data_chan1.append(round(voltage[1],3))
        voltage_data_chan2.append(round(voltage[2],3))
        voltage_data_chan3.append(round(voltage[3],3))
        
        # ~ resistance_data.append(resistance)
        weight_data_chan0.append(round(weight_drift[0],3))
        weight_data_chan1.append(round(weight_drift[1],3))
        weight_data_chan2.append(round(weight_drift[2],3))
        weight_data_chan3.append(round(weight_drift[3],3))
        # weight_data_drift.append(weight_drift)
        
        pressure_data_chan0.append(round(pressure[0],3))
        pressure_data_chan1.append(round(pressure[1],3))
        pressure_data_chan2.append(round(pressure[2],3))
        pressure_data_chan3.append(round(pressure[3],3))
        
        time.sleep(1)
        
except KeyboardInterrupt:
    data = {'Timestamp': time_data, 'Volt_0': voltage_data_chan0, 
            'Volt_1': voltage_data_chan1, 'Volt_2': voltage_data_chan2,
            'Volt_3': voltage_data_chan3, 'Weight_0': weight_data_chan0,
            'Weight_1': weight_data_chan1,'Weight_2': weight_data_chan2,
            'Weight_3': weight_data_chan3, 'Pressure_0': pressure_data_chan0,
            'Pressure_1': pressure_data_chan1, 'Pressure_2': pressure_data_chan2,
            'Pressure_3': pressure_data_chan3}
    df = pd.DataFrame(data)
    df.to_csv('FSR_data_debug.csv', index = False)
    print("Data saved to file!")








# ~ def volt_avg(resolution: int):
    # ~ buffer_size = np.array([])
    # ~ for i in range(0,resolution-1):
        # ~ buffer_size = np.append(buffer_size, chan.voltage)
    # ~ moving_avg: float = np.average(buffer_size)
    # ~ return moving_avg

# ~ while True:
    # ~ #voltage: float = volt_avg(50)
    # ~ voltage = chan.voltage
    # ~ #resistance: float = (voltage*10000/(5.250 - voltage))
    # ~ resistance: float = (10000)*((5.030/voltage)-1)
    # ~ weight: float = math.exp(-(math.log(((resistance/1000)+0.0168)/155.1748)
                                                                    # ~ /0.7013))
    # ~ print("{:>5.3f}\t{:>5.3f}\t\t{:>5.3f}".format(  voltage,
                                                    # ~ resistance,
                                                    # ~ weight))
    # ~ time.sleep(1)

