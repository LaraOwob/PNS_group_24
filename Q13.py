

import matplotlib.pyplot as plt
import numpy as np
def arrival_rate(jobs, t):
    for j in jobs:
        if t > j["start"] and t < j["end"]:
            return j["rate"]
    
    
def calculate_bandwidth_usage(jobs, shaping_rate,dt):
    delay_data_points = []
    bitrate_data_points = []
    for j in jobs:
        job_bit_data = {}
        job_delay_data = {}
        total_Mbits = (j["end"] - j["start"]) * j["rate"]
        
        excess = max(0, j["rate"]- shaping_rate )
        total_time = total_Mbits / shaping_rate
        delay = total_time - (j["end"] - j["start"])
        for t in np.arange(j["start"], j["end"]+dt, dt):
            job_delay_data[t] =excess * abs(j["start"] - t)
            peak = job_delay_data[t]
            job_bit_data[t] = shaping_rate 
        extra_time = delay + j["end"]
        for s in np.arange(j["end"],extra_time +dt,dt):
            down_step = max(0,  peak - shaping_rate * (s - j["end"]))
            job_delay_data[s] = down_step
            job_bit_data[s] = shaping_rate 
        bitrate_data_points.append(job_bit_data)
        delay_data_points.append(job_delay_data)
        
    return delay_data_points,bitrate_data_points

   
def makeGraph(data,title,axes):
    for job in data:
        plt.plot(job.keys(), job.values())
        plt.xlabel('Time (s)')
        plt.ylabel(axes)
        plt.title(title+'Over Time with Traffic Shaping')
        plt.grid(True)
    plt.legend([f'Job {i+1}' for i in range(len(data))])
    plt.show()
    plt.savefig(title+'.png')
        
def main():
    jobs = [
    {"start": 0, "end": 10, "rate": 5.0},    # burst 1: 5 Mbit/s for 10 s
    {"start": 15, "end": 20, "rate": 7.5},   # burst 2: 7.5 Mbit/s for 5 s
    {"start": 25, "end": 50, "rate": 2.5},   # burst 3: 2.5 Mbit/s for 25 s
]
    shaping_rate = 4
    dt = 0.01
    delay_data,bit_data = calculate_bandwidth_usage(jobs, shaping_rate,dt)
    makeGraph(delay_data,"Delay ","Delay (Mbit/s)")
    
    makeGraph(bit_data,"Bitrate ","Bitrate (Mbit/s)")
    
if __name__ == "__main__":
    main()
    