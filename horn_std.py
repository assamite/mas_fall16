'''
Test to compute standard deviations for the parameters for the accepted domain
artifacts, etc.
'''
import logging
import numpy as np

from creamas.core import Simulation

from horn_agent import HornAgent, HornEnvironment


# Basic run configuration.
# More options available in HornAgent and HornEnvironment
N_AGENTS = 1
# Total amount of artifacts considered per iteration (divided among all agents)
TOTAL_SEARCH_WIDTH = 128
# Target number of domain artifacts
N_ARTIFACTS = 20
# Maximum iterations for simulation
MAX_STEPS = 1000
# Domain learning method
LEARN_METHOD = 'closest' # or 'random' / 'none'
# how many artifacts agents learn from environment per iteration omitted if method is 'none'
LEARN_AMOUNT = 3
# Move radius (0.0, 1.0)
RAD = 0.05 
# 0.24-0.27 seems to be about right atm
THRESHOLDS = 0.20
# Created images are scaled to this size (faster debugging with smaller images)
IMG_SIZE = 256

# Logging folder w.r.t current folder. If None, then simulation does not
# give you nearly as much information of it at runtime. If HornAgent's
# _save_images is True, then it will create image for each agent on each
# iteration
LOG_FOLDER = 'log_std_full_circle_12'
LOG_LEVEL = logging.INFO

env = HornEnvironment(log_folder=LOG_FOLDER)
for e in range(0, N_AGENTS):
    sw = int(TOTAL_SEARCH_WIDTH / N_AGENTS)
    a = HornAgent(env, desired_novelty=-1, search_width=sw, 
                  veto_threshold=THRESHOLDS, critic_threshold=THRESHOLDS,
                  img_size=IMG_SIZE, log_folder=LOG_FOLDER, 
                  move_radius=RAD, log_level=LOG_LEVEL)
sim = Simulation(env, log_folder=LOG_FOLDER,
                 callback=env.vote_and_save_info)

while len(sim.env.artifacts) < N_ARTIFACTS:
    if sim.age >= MAX_STEPS:
        break
    sim.step()

# Array of genes for all domain artifacts
gene_array = np.array([a.framings[a.creator]['genes'] for a in
                       sim.env.artifacts if a.accepted])

print("\n")
print("STD:  {}".format(np.std(gene_array, axis=0)))
print("MEAN: {}".format(np.mean(gene_array, axis=0)))
print("MIN:  {}".format(np.min(gene_array, axis=0)))
print("MAX:  {}".format(np.max(gene_array, axis=0)))
print("\n")

ret = sim.end()
#print(ret)
