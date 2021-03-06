from typing import Iterable, List

import Commuter


##############################################################
##                                                          ##
## right now just fixed numbers, no distribution sampling   ##
## change in future for MCMC                                ##
##                                                          ##
##############################################################

def apply_sir_differential(o, beta, gamma, ir):
    ds = beta * ir * o.S
    dr = o.I * gamma
    o.S -= ds
    o.I += ds - dr
    o.R += dr


class SIRModel:
    id = ""
    name = ""

    outgoingCommuters: {int: Commuter}

    NwC = 0
    SwC = 0
    IwC = 0
    RwC = 0

    dayBeta = 1.1
    nightBeta = 0.5
    gamma = 1 / 28

    timeStep = 0

    def __init__(self, id, N, S, I, R, commuters: List[Commuter.Commuter], name="NO_NAME"):
        # print("init id: " + str(id) + ", name: "+ str(name) + " with N: " + str(N) + ", S: " + str(I) + ", I: " + str(I) + ", R: " + str(R))
        self.id = id
        self.name = name

        self.N = N
        self.S = S
        self.I = I
        self.R = R

        assert N == S + I + R

        self.outgoingCommuters = commuters
        for c in commuters:
            assert c.idFrom == self.id

        self.timeStep = 0

        self.sirSeries = []

    def nextTimeStep(self, commuter: List[Commuter.Commuter]):

        # imitate day and night cycle
        dayTime = self.timeStep % 2 == 0

        present = commuter if dayTime else self.outgoingCommuters

        self.includeCommuters(present)

        if self.NwC:

            beta = self.nightBeta
            if dayTime:
                beta = self.dayBeta

            ir = self.IwC / self.NwC  # infection ratio

            apply_sir_differential(self, beta=beta, gamma=self.gamma, ir=ir)

            for c in present:
                apply_sir_differential(c, beta=beta, gamma=self.gamma, ir=ir)

        # capture SIR for plotting
        self.sirSeries.append((self.SwC, self.IwC, self.RwC))

        self.timeStep += 1

    # add commuters from outside or add comuters coming home
    def includeCommuters(self, commuter: Iterable[Commuter.Commuter]):
        self.NwC = self.N
        self.SwC = self.S
        self.IwC = self.I
        self.RwC = self.R

        for cIn in commuter:
            self.NwC += cIn.N
            self.SwC += cIn.S
            self.IwC += cIn.I
            self.RwC += cIn.R

    ##########################Setter and toString

    def setBeta(self, beta):
        self.dayBeta = beta
        self.nightBeta = beta
        print("set beta to :" + str(self.dayBeta))

    def setGamma(self, gamma):
        self.gamma = gamma
        print("set gamma to :" + str(self.gamma))

    def setGammaWithDuration(self, duration):
        self.gamma = 1 / duration
        print("set gamma to :" + str(self.gamma))

    def computeGamma(self):
        self.gamma = self.R / self.I
        print("set gamma to :" + str(self.gamma))

    def plot(self):
        import pandas as pd
        import matplotlib.pyplot as plt
        df = pd.DataFrame(self.sirSeries, columns=['S', 'I', 'R'])
        df.plot()
        df.sum(axis=1).plot(label='N')
        plt.axhline(0, c='k')
        plt.grid()
        plt.title(self.name)

    def __str__(self):
        msg = "SIRModel " + str(self.name) + " at t=" + str(self.timeStep / 2) + "\n"
        msg += "Population: " + str(self.N) + "\n"
        msg += "Suseptible: " + str(self.S) + "P(S): " + str(self.S / self.N) + "\n"
        msg += "Infected: " + str(self.I) + "P(I): " + str(self.I / self.N) + "\n"
        msg += "Recovered: " + str(self.R) + "P(R): " + str(self.R / self.N) + "\n"
        msg += "TotalCHECK: " + str(self.R + self.I + self.S) + "\n"
        return msg

        '''
        msg = "SIRModel at t=" + str(self.timeStep) + "\n"
        msg += "Population: " + str(self.NwC) + "\n"
        msg += "Suseptible: " + str(self.SwC) + "P(S): " + str(self.SwC / self.NwC) + "\n"
        msg += "Infected: " + str(self.IwC) + "P(I): " + str(self.IwC / self.NwC) + "\n"
        msg += "Recovered: " + str(self.RwC) + "P(R): " + str(self.RwC / self.NwC) + "\n"
        msg += "TotalCHECK: " + str(self.RwC + self.IwC + self.SwC) + "\n"
        '''
