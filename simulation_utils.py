import heapq
import numpy as np
from abc import ABC, abstractmethod


class Event(ABC):
    def __init__(self, time, simulator, server):
        self.time = time
        self.simulator = simulator
        self.server = server

    def __lt__(self, other):
        return self.time < other.time

    @abstractmethod
    def process(self):
        pass


class ArrivalEvent(Event):
    def __init__(self, time, simulator, server):
        super().__init__(time, simulator, server)

    def process(self):
        if self.simulator.servers[self.server].is_busy():
            if self.simulator.servers[self.server].is_full():
                self.simulator.tossed_event_count += 1
            else:
                self.simulator.servers[self.server].enqueue(self)
        else:
            self.simulator.servers[self.server].set_busy()
            service_time = np.random.exponential(1/self.simulator.server_service_rate[self.server])
            exit_time = self.time + service_time
            self.simulator.schedule(ServiceEvent(self.time, exit_time, service_time, self.simulator, self.server))


class ServiceEvent(Event):
    def __init__(self, arrival_time, time, service_time, simulator, server):
        super().__init__(time, simulator, server)
        self.arrival_time = arrival_time
        self.service_time = service_time

    def process(self):
        self.simulator.processed_event_count += 1
        # update wait_time and service_time
        self.simulator.wait_time += self.time - self.service_time - self.arrival_time
        self.simulator.service_time += self.service_time
        # if there are unprocessed Arrival events, process the first one
        if self.simulator.servers[self.server].queue:
            service_time = np.random.exponential(1/self.simulator.server_service_rate[self.server])
            event = self.simulator.servers[self.server].dequeue()
            self.simulator.schedule(ServiceEvent(event.time, self.time + service_time, service_time, self.simulator, self.server))
        else:
            self.simulator.servers[self.server].set_idle()


class Server:
    def __init__(self, simulator, queue_size):
        self.simulator = simulator
        self.queue_size = queue_size
        self.queue = []
        self.busy = False

    def enqueue(self, event):
        self.queue.append(event)

    def dequeue(self):
        return self.queue.pop(0)

    def is_full(self):
        return len(self.queue) >= self.queue_size

    def is_busy(self):
        return self.busy

    def set_busy(self):
        self.busy = True

    def set_idle(self):
        self.busy = False


class Simulator:
    def __init__(self, T, N, server_probability, arrival_rate, server_queue_size, server_service_rate):
        # input parameters
        self.final_time = T
        self.N = N
        self.server_probability = server_probability
        self.arrival_rate = arrival_rate
        self.server_queue_size = server_queue_size
        self.server_service_rate = server_service_rate

        # output parameters
        self.processed_event_count = 0
        self.tossed_event_count = 0
        self.wait_time = 0
        self.service_time = 0

        # simulation objects
        self.current_time = 1
        self.servers = []
        self.event_list = []
        self.unprocessed_service_events = []

    def initialize_simulation(self):
        self.servers = [Server(self, self.server_queue_size[i]) for i in range(self.N)]
        heapq.heapify(self.event_list)
        time = 0
        self.schedule(ArrivalEvent(time, self, np.random.choice(self.N, p=self.server_probability)))
        while time < self.final_time:
            time += np.random.exponential(1/self.arrival_rate)
            self.schedule(ArrivalEvent(time, self, np.random.choice(self.N, p=self.server_probability)))

    def run(self):
        self.initialize_simulation()
        while self.event_list and self.current_time < self.final_time:
            event = heapq.heappop(self.event_list)
            self.current_time = event.time
            event.process()

    def schedule(self, event):
        heapq.heappush(self.event_list, event)

    def get_total_time(self):
        return (self.wait_time + self.service_time) / self.processed_event_count

    def print_results(self):
        print(f"{self.processed_event_count} {self.tossed_event_count} {self.current_time} {self.wait_time / self.processed_event_count} {self.service_time / self.processed_event_count}")
        