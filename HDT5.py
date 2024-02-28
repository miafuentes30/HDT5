import simpy
import random
import numpy as np
import matplotlib.pyplot as plt

RANDOM_SEED = 42
MEMORY_CAPACITY = 100
INSTRUCTIONS_PER_CYCLE = 3
CPU_SPEED = 1 
NUM_PROCESSES = [25, 50, 100, 150, 200]

# Variables para las gráficas
avg_times = []
std_dev_times = []

random.seed(RANDOM_SEED)
np.random.seed(RANDOM_SEED)
env = simpy.Environment()
RAM = simpy.Container(env, init=MEMORY_CAPACITY, capacity=MEMORY_CAPACITY)
cpu = simpy.Resource(env, capacity=1)

def new_process(env, interval):
    while True:
        yield env.timeout(random.expovariate(1.0 / interval))
        
        process = {
            'id': len(env.processes) + 1,
            'memory': random.randint(1, 10),
            'instructions': random.randint(1, 10),
            'arrival_time': env.now
        }
        env.processes.append(process)
        print(f"New process {process['id']} with {process['memory']} memory and {process['instructions']} instructions at time {env.now}")

        with RAM.get(process['memory']) as req:
            yield req

        with cpu.request() as req:
            yield req
            env.process(run_process(env, process))

def run_process(env, process):
    print(f"Process {process['id']} starts running at time {env.now}")

    while process['instructions'] > 0:
        instructions_to_execute = min(INSTRUCTIONS_PER_CYCLE, process['instructions'])
        yield env.timeout(1 / CPU_SPEED) 

        process['instructions'] -= instructions_to_execute

        if process['instructions'] <= 0:
            print(f"Process {process['id']} is terminated at time {env.now}")
            RAM.put(process['memory'])
        else:
            random_choice = random.randint(1, 21)

            if random_choice == 1:
                print(f"Process {process['id']} goes to waiting at time {env.now}")
                env.process(waiting_process(env, process))
            elif random_choice == 2:
                print(f"Process {process['id']} goes back to ready at time {env.now}")
                env.process(run_process(env, process))

def waiting_process(env, process):
    yield env.timeout(random.randint(1, 5))
    print(f"Process {process['id']} is back to ready from waiting at time {env.now}")
    env.process(run_process(env, process))

# Función para ejecutar la simulación con diferentes cantidades de procesos
def run_simulation(interval):
    env.processes = [] 
    env.process(new_process(env, interval))
    env.run(until=100) 

    # Calcular estadísticas
    times = [process['arrival_time'] - process['arrival_time'] for process in env.processes]
    avg_time = np.mean(times)
    std_dev_time = np.std(times)
    
    return avg_time, std_dev_time

# Parte a: Ejecutar simulación con diferentes cantidades de procesos e intervalos de llegada
for num_processes in NUM_PROCESSES:
    avg_time, std_dev_time = run_simulation(10)
    avg_times.append(avg_time)
    std_dev_times.append(std_dev_time)

# Graficar resultados
plt.plot(NUM_PROCESSES, avg_times, label='Average Time')
plt.plot(NUM_PROCESSES, std_dev_times, label='Standard Deviation')
plt.xlabel('Number of Processes')
plt.ylabel('Time')
plt.legend()
plt.title('Simulation Results')
plt.show()
