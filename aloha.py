


#Slotted ALOHA Network

import random
import simpy
import math

RANDOM_SEED = 34
SIM_TIME = 100000



MU = 1

""" Queue system  """      
class server_queue:
   def __init__(self, env, arrival_rate):
      self.server = simpy.Resource(env, capacity = 1)
      self.env = env
      self.queue_len = 0
      self.flag_processing = 0
      self.packet_number = 0
      self.sum_time_length = 0
      self.start_idle_time = 0
      self.arrival_rate = arrival_rate

   def process_packet(self, env, packet):
      with self.server.request() as req:
         start = env.now
         yield req
         yield env.timeout(random.expovariate(MU))
         latency = env.now - packet.arrival_time
         ###self.Packet_Delay.addNumber(latency)
         #print("Packet number {0} with arrival time {1} latency {2}".format(packet.identifier, packet.arrival_time, latency))
         self.queue_len -= 1
         if self.queue_len == 0:
            self.flag_processing = 0
            self.start_idle_time = env.now

   def packets_arrival(self, env):
      # packet arrivals 

      while True:
         # Infinite loop for generating packets
         yield env.timeout(random.expovariate(self.arrival_rate))
         # arrival time of one packet

         self.packet_number += 1
         # packet id
         print(self.packet_number)
         arrival_time = env.now  
         #print(self.num_pkt_total, "packet arrival")
         new_packet = Packet(self.packet_number,arrival_time)
         if self.flag_processing == 0:
            self.flag_processing = 1
            #idle_period = env.now - self.start_idle_time
            #self.Server_Idle_Periods.addNumber(idle_period)
            #print("Idle period of length {0} ended".format(idle_period))
         self.queue_len += 1
         env.process(self.process_packet(env, new_packet))


""" Packet class """       
class Packet:
   def __init__(self, identifier, arrival_time):
      self.identifier = identifier
      self.arrival_time = arrival_time



def main():
   random.seed(RANDOM_SEED)
   for arrival_rate in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
      env = simpy.Environment()
      router = server_queue(env, arrival_rate)
      env.process(router.packets_arrival(env))
      env.run(until=SIM_TIME)


if __name__ == '__main__': main()
part2.pyOpen
Displaying part2.py.
