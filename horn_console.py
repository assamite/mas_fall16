'''
Console script for running the experiments
'''
import os
import logging
import operator

import numpy as np
from matplotlib import pyplot as plt

from horn_agent import HornAgent, HornArtifact, HornEnvironment
from creamas.core import Simulation

N_AGENTS = [1, 2, 4, 8, 16]
N_MEM = 512 # Total number of memory slots divided evenly across all the agents
HORNS_PER_ITER = 256 # Total number of horns generated per iteration
MAX_STEPS = 1000    # Maximum number of iterations the simulation is run.
N_ARTIFACTS = 200   # Target number of accepted artifacts
RAD = 0.1
LOG_FOLDER = 'logs_256_026'
L_METHODS = ['closest']
L_LAST = [False]
L_AMOUNTS = [3]
# (self-criticism, veto)
NOVELTY_THRESHOLDS = [(0.26, 0.26)]
JUMPS = ['none']
RUNS = 1
VOTING_METHOD = 'mean'

for n in N_AGENTS:
    log_folder = os.path.join(LOG_FOLDER, "N{}".format(n))
    for m in L_METHODS:
        for last in L_LAST:
            for nov_threshold in NOVELTY_THRESHOLDS:
                for L_AMOUNT in L_AMOUNTS:
                    # Variables to save info of each run for this setting.
                    dists = []
                    iters = []
                    mscs = []
                    mvcs = []
                    ameans = []
                    # Run same setting specified number of times to diminish
                    # effects of RNG.
                    for r in range(1, RUNS+1):
                        # Initialize environment
                        env = HornEnvironment(log_folder=log_folder)
                        env.voting_method = VOTING_METHOD
                        env.run_number = r
                        memsize = int(N_MEM / n)
                        nspiro = int(HORNS_PER_ITER / n)
                        print("\n\n\n\n\n")
                        print("--- agents={} {} learn={},{} last={} run={} ---"
                              .format(n, nov_threshold, m, L_AMOUNT, last, r))
                        print("\n\n\n\n\n")

                        # Initialize agents
                        for i in range(n):
                            a = HornAgent(env, desired_novelty=-1, search_width=nspiro,
                                           memsize=memsize, learning_method=m,
                                           learn_on_add=last,
                                           learning_amount=L_AMOUNT, move_radius=RAD,
                                           critic_threshold=nov_threshold[0],
                                           veto_threshold=nov_threshold[1],
                                           jump='none', log_folder=log_folder,
                                           log_level=logging.DEBUG)
                        sim = Simulation(env, log_folder=log_folder,
                             callback=env.vote_and_save_info)

                        # Run simulation to generate specified number of artifacts
                        # or break if maximum amount of steps is reached
                        while len(sim.env.artifacts) < N_ARTIFACTS:
                            if sim.age >= MAX_STEPS:
                                break
                            sim.step()

                        # Save run info, etc.
                        iter = sim.age
                        iters.append(iter)
                        vmethod = sim.env.voting_method
                        mean_dist, accs, rejs, msc, mvc, am = sim.end()
                        arts = len(sim.env.artifacts)
                        axs, adists = accs
                        dists.append((axs,adists))
                        mscs.append(msc)
                        mvcs.append(mvc)
                        ameans.append(am[2])
                        if len(axs) > 0:
                            fname = "arts={}_A{}_s={}_v={}_t={}_learn={}{}_onadd={}_run={}_mean={}_i={}_msc={}_mvc={}.txt".format(arts, n, HORNS_PER_ITER, vmethod, nov_threshold, m, L_AMOUNT, last, r, mean_dist, iter, msc, mvc)
                            log_file = os.path.join(LOG_FOLDER, fname)
                            with open(log_file, 'w') as f:
                                f.write(" ".join([str(p) for p in axs]))
                                f.write("\n")
                                f.write(" ".join([str(p) for p in adists]))

                    # Compute mean info for this setting among all the runs.
                    mean_all = 0.0
                    mean_arts = 0.0
                    axss = {}
                    for d in dists:
                        axs, adists = d
                        for i,a in zip(axs, adists):
                            if i in axss:
                                axss[i].append(a)
                            else:
                                axss[i] = [a]
                        if len(adists) > 0:
                            mean_all += np.mean(adists)
                            mean_arts += len(adists)
                    mean_all = mean_all / len(dists)
                    mean_arts = mean_arts / len(dists)
                    mean_iter = np.mean(iters)
                    mmsc = np.mean(mscs)
                    mmvc = np.mean(mvcs)
                    amean = np.mean(ameans)

                    axs = []
                    adists = []
                    items = sorted(axss.items(), key=operator.itemgetter(0))
                    for i,a in items:
                        axs.append(i)
                        adists.append(np.mean(a))

                    fname = "means_arts={}_A{}_s={}_v={}_t={}_learn={}{}_onadd={}_mean={}_i={}_msc={}_mvc={}_am={}.txt".format(mean_arts, n, HORNS_PER_ITER, vmethod, nov_threshold, m, L_AMOUNT, last, mean_all, mean_iter, mmsc, mmvc, amean)
                    log_file = os.path.join(LOG_FOLDER, fname)
                    with open(log_file, 'w') as f:
                        f.write(" ".join([str(p) for p in axs]))
                        f.write("\n")
                        f.write(" ".join([str(p) for p in adists]))