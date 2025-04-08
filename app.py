import matplotlib as mpl

from plot import Plot
from gdop.simulation import Simulation

mpl.use('macosx')

if __name__ == "__main__":
    simulation = Simulation()
    Plot(simulation)