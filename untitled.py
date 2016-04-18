

from __future__ import division
import random
import simpy
import math

TS = 1
TOTALHOSTS = 10
slot_length = 1
LINEAR = 0
EXPONENTIAL = 1
SIM_TIME = 100000
   
class host:
   def __init__(self, env, name, mylambda, ethernet):
      self.server = simpy.Resource(env, capacity = 1)
      self.env = env
      self.name = name
      self.mylambda = mylambda
      self.L = 0              # Number of Packets in the queue/ Queue Length
      self.S = 0              # Slot number for next transmission attempt
      self.N = 0              # Number of reattempts to transmit packet
      self.ethernet = ethernet
      self.transmitpackets = 0#success_packets
      self.flag_processing = 0
      self.packet_number = 0
      self.start_idle = 0

#If a host has no packets in queue, it will not attempt to transmit
#If a host has a packet in the queue:
#  and the Ethernet's current slot number is the same as the host's slot number S, attempt to transmit
#     succeed and process packet if there is only 1 host attempting to transmit
#        decrease host's queue length, L, by 1 and increment it's slot number, S
#     fails if there are multiple host's attempting to transmit
#	 for each host attempting to transmit:
#	    increment their number of reattempts, N, by 1
#	    recalculate their slot numbers by given formula
#	       exponential:  take K = min(N, 10), take a random decimal R =(0, 2^R)
#		     S = S + R + 1
#	       linear: take K = min(N, 1024), take a random int from 0, K
#		     S = S + R + 1
#
   def process_packet(self, env):
      start = env.now
      if self.L == 0:
        self.flag_processing = 0
        self.start_idle_time = env.now
      self.L -= 1
      self.S += 1
      self.N = 0 
      self.transmitpackets += 1
      
   def packets_arrival(self, env, ethernet):
      while True:
         yield env.timeout(random.expovariate(self.mylambda))
         arrival_time = env.now
         if(self.L == 0):
            self.S = ethernet.slot_number + 1
         self.packet_number += 1
         if self.flag_processing == 0:
            self.flag_processing = 1
         self.L += 1

   def delay_packet(self, control):
      #exponental
      if control == 1: 
         K = min(self.N, 10)
         R = round(random.uniform(0, 2**K))
         self.S = (self.S + R + 1)
         self.N += 1
      #linear
      if control == 0: 
         K = min(self.N, 1024)
         R = random.randint(0, K)
         self.S = self.S + R + 1
         self.N += 1


class ethernet:
  def __init__(self, env, hostcount, mylambda, slot_length):
      self.hostcount = hostcount
      self.nodearray = []
      self.env = env
      self.mylambda = mylambda
      self.slot_number = 0
      self.slot_length = slot_length
      self.slot_succeeded = 0
      self.slot_collided = 0
      self.hosts_transmitting = 0
            
  def ethernetdelay(self, env, control):
      for x in range(self.hostcount):
          self.nodearray.append(host(env, x + 1, self.mylambda, self))
          self.env.process(self.nodearray[x].packets_arrival(self.env, self)) #create host array

      while True:
         yield self.env.timeout(self.slot_length)
         #reset count of number of hosts attempting to transmit
         self.hosts_transmitting = 0
         #For each host check if their current slot number matches, ethernet's currentr slot number
         for x in range(self.hostcount):
            if(self.nodearray[x].L == 0):
               continue
            if(self.nodearray[x].L >= 1 and self.nodearray[x].S == self.slot_number):
               self.hosts_transmitting += 1
               index = x
         #If there is only one host transmitting, then it is successful
         if (self.hosts_transmitting == 1):
            self.slot_succeeded += 1
            self.nodearray[index].process_packet(self.env)
         #if there are multiple hosts attempting to transmit, delay the transmission and recalculate slot numbers
         if (self.hosts_transmitting > 1):
            self.slot_collided += 1
            for x in range(self.hostcount):
               if (self.nodearray[x].S == self.slot_number):
                  self.nodearray[x].delay_packet(control) 
	 #increment to process next slot
         self.slot_number += 1						

  def throughput(self, control, linear, exponential):
    if(control == 1):
      exponential[self.mylambda] =  self.slot_succeeded/self.slot_number
    elif(control == 0):
      linear[self.mylambda] = self.slot_succeeded/self.slot_number
      
def print_table(mylambda, linear, exponential):
   print("{:<8} {: <22} {: <18}".format(mylambda, exponential[mylambda], linear[mylambda]))
   
def main():
   linear = {}
   exponential = {}
   print("Simulation Time: ", SIM_TIME)
   print("{:<8} {:<22} {:<18}".format("Lambda", "Exponential Backoff", "Linear Backoff"))
   for mylambda in [0.01, 0.02, 0.03, 0.04, 0.05, 0.06, 0.07, 0.08, 0.09]:
      #Simulate linear backoff
      env = simpy.Environment()
      myethernet = ethernet(env, TOTALHOSTS, mylambda, slot_length)
      env.process(myethernet.ethernetdelay(env, LINEAR))
      env.run(until=SIM_TIME)
      myethernet.throughput(LINEAR, linear, exponential)
      #Simulate exponential backoff
      env = simpy.Environment()
      myethernet = ethernet(env, TOTALHOSTS, mylambda, slot_length)
      env.process(myethernet.ethernetdelay(env, EXPONENTIAL))
      env.run(until=SIM_TIME)
      myethernet.throughput(EXPONENTIAL, linear, exponential)
      print_table(mylambda, linear, exponential)
    
if __name__ == '__main__': main()
