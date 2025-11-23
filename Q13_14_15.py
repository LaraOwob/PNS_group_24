

import matplotlib.pyplot as plt
import numpy as np


def traffic_policing(jobs, leak_rate,burst_rate,dt):
    conforming_intervals = []
    all_jobs_bit_data = []
    for j in jobs:
        job_bit_data = {}        
        excess = max(0, j["rate"]- leak_rate )
        end_conform = j["end"]
        for t in np.arange(j["start"], j["end"]+dt, dt):
            water_volume = excess * abs(j["start"] - t)
            if water_volume >= burst_rate:
                job_bit_data[t] = burst_rate
                end_conform = t
                
            else:
                job_bit_data[t] = water_volume
        conforming_intervals.append((j["start"],end_conform))
        all_jobs_bit_data.append(job_bit_data)
    return conforming_intervals, all_jobs_bit_data
        
        
    
def traffic_shaping(jobs, shaping_rate,dt):
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
        
        

def policing_graph(data, intervals):
    fig, ax = plt.subplots()
    set_line_objects   = []
    for job_data in data:
        times = list(job_data.keys())
        values = list(job_data.values())
        line_obj, = ax.plot(times, values, label='Job Bitrate')
        set_line_objects.append(line_obj)
    
    # Fill conforming intervals
    
    for start, end in intervals:
        k = 0 
        for job_data in data:
            times = np.array(list(job_data.keys()))
            values = np.array(list(job_data.values()))
            mask = (times >= start) & (times <= end)
            ax.fill_between(times[mask], 0, values[mask], alpha=0.3,  color=set_line_objects[k].get_color())
            k += 1
    
    ax.set_xlabel("Time")
    ax.set_ylabel("Bitrate")
    ax.set_title("Traffic Policing Timeline")
    ax.legend([f'Job {i+1}' for i in range(len(data))])    
    plt.show()
    plt.savefig("Policing_Graph.png")
    
    
    
def main():
    jobs = [
    {"start": 0, "end": 10, "rate": 5.0},    # burst 1: 5 Mbit/s for 10 s
    {"start": 15, "end": 20, "rate": 7.5},   # burst 2: 7.5 Mbit/s for 5 s
    {"start": 25, "end": 50, "rate": 2.5},   # burst 3: 2.5 Mbit/s for 25 s
]
    shaping_rate = 4
    dt = 0.01
    delay_data,bit_data = traffic_shaping(jobs, shaping_rate,dt)
    burst_tolerance =8
    leak_rate = 4
    #Question 13
    #makeGraph(delay_data,"Delay ","Delay (Mbit/s)")
    #Question 14
    #makeGraph(bit_data,"Bitrate ","Bitrate (Mbit/s)")
    #Question 15
    conforming_intervals, policing_bit_data = traffic_policing(jobs, leak_rate,burst_tolerance,dt)
    print("Conforming Intervals:",conforming_intervals)
    policing_graph(policing_bit_data,conforming_intervals)
    
if __name__ == "__main__":
    main()
    