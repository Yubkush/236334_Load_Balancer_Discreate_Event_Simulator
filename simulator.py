from simulation_utils import Simulator
import sys

def main():
    # parse input from command line
    T = int(sys.argv[1])
    N = int(sys.argv[2])
    probabilities = [float(x) for x in sys.argv[3:3+N]]
    arrival_rate = float(sys.argv[3+N])
    queue_size = [int(x) for x in sys.argv[4+N:4+2*N]]
    service_rate = [int(x) for x in sys.argv[4+2*N:4+3*N]]
    
    # run simulation
    simulator = Simulator(T, N, probabilities, arrival_rate, queue_size, service_rate)
    simulator.run()
    simulator.print_results()
    
    
if __name__ == '__main__':
    main()
