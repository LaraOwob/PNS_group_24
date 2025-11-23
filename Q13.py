

import matplotlib.pyplot as plt
import numpy as np
def arrival_rate(jobs, t):
    for j in jobs:
        if t > j["start"] and t < j["end"]:
            return j["rate"]
    
    
def calculate_bandwidth_usage(jobs, shaping_rate,dt):
    data_points = {}
    for j in jobs:
        total_Mbits = (j["end"] - j["start"]) * j["rate"]
        
        excess = max(0, j["rate"]- shaping_rate )
        total_time = total_Mbits / shaping_rate
        delay = total_time - (j["end"] - j["start"])
        for t in np.arange(j["start"], j["end"]+dt, dt):
            data_points[t] =excess * abs(j["start"] - t)
            peak = data_points[t]
        extra_time = delay + j["end"]
        for s in np.arange(j["end"],extra_time +dt,dt):
            down_step = max(0,  peak - shaping_rate * (s - j["end"]))
            data_points[s] = down_step
        
        
    return data_points

def makeGraph(data):
    plt.plot(data.keys(), data.values())
    plt.xlabel('Time (s)')
    plt.ylabel('Bandwidth Usage (Mbit/s)')
    plt.title('Bandwidth Usage Over Time with Traffic Shaping')
    plt.grid(True)
    plt.show()
   
def main():
    jobs = [
    {"start": 0, "end": 10, "rate": 5.0},    # burst 1: 5 Mbit/s for 10 s
    {"start": 15, "end": 20, "rate": 7.5},   # burst 2: 7.5 Mbit/s for 5 s
    {"start": 25, "end": 50, "rate": 2.5},   # burst 3: 2.5 Mbit/s for 25 s
]
    shaping_rate = 4
    dt = 0.01
    bandwidth_usage = calculate_bandwidth_usage(jobs, shaping_rate,dt)
    makeGraph(bandwidth_usage)
    
if __name__ == "__main__":
    main()
    