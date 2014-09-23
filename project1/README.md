# LAB 1 

## Components 
- input variables
- simulator
- output variables

### Input Variables 
Uniformly distributed random variable generator
  - U(0,1) with range (0,1)

### Queue

#### Format: 
param1/param2/param3/param4

#### Requirements:
##### M/\D/\1
arrive process    : Markovian
service process   : Determinisic (constant service time)
number of servers : 1
buffer size       : infinity 

input:
- ticks
- average number of packets generated per second
- Length of packet in bits
- service time by a packet

outut:
- average number of packets in queue
- average number of queuing delay + service time spent by the packet in the
  system
- proportion of time the server


##### M/\D/\1/\K
arrive process    : Markovian
service process   : Determinisic (constant service time)
number of servers : 1
buffer size       : constant K 

input:
- ticks
- average number of packets generated per second
- Length of packet in bits
- service time by a packet
- buffer size

output:
- average number of packets in queue
- average number of queuing delay + service time spent by the packet in the
  system
- proportion of time the server
- pack loss probability

##### Notes:
- FIFO
- 3 to 5 param
- \/ seperated

|parameters        | Representation                      |
| ---------------- | ----------------------------------- |
|param1, param2    | arrival process and service process | 
|param3            | number of servers		         | 
|param4 (optional) | size of buffer                      |


Type of arrival process and service process 
- M = Memoryless / Markovian
- D = Deterministic
- G = General

When param4 is not present, the buffer size is infinity


