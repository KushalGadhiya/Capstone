import time
import board
import busio
import adafruit_ads1x15.ads1115 as ADS
import math
from adafruit_ads1x15.analog_in import AnalogIn
import numpy as np
# ~ import pandas as pd
from datetime import datetime

# Create the I2C bus
i2c = busio.I2C(board.SCL, board.SDA)

# Create the ADC object using the I2C bus
ads = ADS.ADS1115(i2c)
ads.gain = 2/3

# Create single-ended input on channel 0
chan = AnalogIn(ads, ADS.P3)

voltage_data = []
resistance_data = []
weight_data = []
time_data = []

try:
    while True:
        timestamp = datetime.now()
        voltage = chan.voltage
        resistance = (10000)*((5.030/voltage)-1)
        weight = math.exp(-(math.log(((resistance/1000)+0.0168)/155.1748)
                                                                /0.7013))
        print(f"voltage {voltage} and weight {weight}")
        time_data.append(timestamp)
        voltage_data.append(voltage)
        resistance_data.append(resistance)
        weight_data.append(weight)
        
        time.sleep(1)
        
except KeyboardInterrupt:
    data = {'Timestamp': time_data, 'Voltage': voltage_data, 
            'Resistance': resistance_data, 'Weight': weight_data}
    df = pd.DataFrame(data)
    df.to_csv('FSR_data.csv', index = False)
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

