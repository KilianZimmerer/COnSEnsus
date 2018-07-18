import COntent as con
import numpy as np
import networkx as nx

# initial parameters
N  = 100 # network size
iu = 51 # information uptake
dd = 1 # degree density
p = (0.1, 1) # propaganda (denisty   , opinion)
# generating model (Erdos-Renyi network)
graph = nx.erdos_renyi_graph(N, dd)
print(nx.info(graph))

adj = nx.to_numpy_array(graph)

# initializing the opinions
initial_opinions = np.random.rand(N)

model = con.Model(adjacency_matrix=adj.copy(),
                  opinion=initial_opinions.copy(),
                  information_uptake = iu,
                  propaganda = p,
                  convergence_parameter = (1e9,10,1e-6),
                  step_resolution = 1e9
                  )

traj = model.run()

# printing the results as a dictinary
print(traj)
