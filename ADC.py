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

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P3)

threshold = 15

voltage_data = []
resistance_data = []
weight_data_1 = []
weight_data_2 = []
weight_data_3 = []
time_data = []
weight_buffer = [0.0,0.0]
output_weight = 0

def account_drift(new_sample):
    global weight_buffer
    global output_weight
    weight_buffer[0] = new_sample
    slope = (weight_buffer[0] - weight_buffer[1])/1
    if(abs(slope) >= threshold):
        output_weight = new_sample
    weight_buffer[1] = weight_buffer[0]

try:
    while True:
        timestamp = datetime.now()
        voltage = chan.voltage
        resistance = (10000)*((5.030/voltage)-1)
        #weight_1 = math.exp(-(math.log(((resistance/1000)+0.0168)/155.1748)/0.7013))
        weight_1 = math.exp(-(math.log((resistance+16.8104)/155170)/0.7013))
        weight_2 = (6.7132e7)*(resistance**(-1.6009))+77.7879
        weight_3 = (1.0686e8)*(resistance**(-1.6811))+32.6381
        #weight_4 = (-3.4230e6)*np.exp(1.7714e4*(1/resistance)) + (3.4229e6)*np.exp(1.7749e4*(1/resistance))
        #account_drift(weight)
        #output_pressure = ((output_weight/1000)*9.81)/((np.pi)*(0.013**2))/1000
        print(f"voltage {voltage:.3f} and weight_1 {weight_1:.2f} and weight_2 {weight_2:.2f} weight_3 {weight_3:.2f}")
        #print(f"output = {output_weight:.3f}g and pressure {output_pressure:.2f}Kpa\n")
        time_data.append(timestamp)
        voltage_data.append(voltage)
        resistance_data.append(resistance)
        weight_data_1.append(weight_1)
        weight_data_2.append(weight_2)
        weight_data_3.append(weight_3)
        
        time.sleep(1)
        
except KeyboardInterrupt:
    data = {'Timestamp': time_data, 'Voltage': voltage_data, 
            'Resistance': resistance_data, 'Weight_1': weight_data_1, 'Weight_2': weight_data_2,'Weight_3': weight_data_3}
    df = pd.DataFrame(data)
    df.to_csv('FSR_data_acc.csv', index = False)
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

