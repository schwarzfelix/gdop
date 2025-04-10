import matplotlib as mpl

from plot import Plot
from simulation import Simulation

mpl.use('macosx')

if __name__ == "__main__":
    simulation = Simulation()
    p = Plot(simulation)