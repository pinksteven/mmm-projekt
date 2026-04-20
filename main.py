from multiprocessing import Array

import matplotlib.pyplot as plt
import numpy as np


class Object:
    def __init__(
        self,
        B: float,  # Wartość wyjściowa histerezy -B = low, B= high
        a: float,  # threshold hoisterezy -a i a
        kp: float,  # Wzmocnienie bloku
        Tp: float,  # W mianowniku bloku
        T: float,  # stała czasowa T
        x1o: float = 0,  # wartość początkowa x1 aka y. Default 0
        x2o: float = 0,  # wartość początkowa x2 aka y'. Defauly 0
    ):
        # Histereza
        self.B = B
        self.a = a
        # Transmitancja Gp
        self.kp = kp
        self.Tp = Tp
        # Sprzężenie zwrotne
        self.T = T
        # Kanoniczny sterowalny model stanowy z transmitancji Gp
        self.Ap = -1 / Tp
        self.Bp = 1
        self.Cp = kp / Tp
        self.Dp = 0

        # Sygnały
        self.x1 = np.array([x1o], dtype=np.float64)  # Wyjście układu (y)
        self.x2 = np.array([x2o], dtype=np.float64)  # Pochodna wyjścia (y')
        self.e = np.array([], dtype=np.float64)  # r-y
        self.e1 = np.array([], dtype=np.float64)  # Wejście histerezy
        self.u = np.array([], dtype=np.float64)  # Wyjście histerezy

    def hysteresis(self, u):
        if u > self.a:
            return self.B
        elif u < -self.a:
            return -self.B
        else:
            return (
                self.u[-1] if len(self.u) > 0 else -self.B
            )  # Default to low state if state can't be determined

    def step(self, dT, r):
        self.e = np.append(self.e, r - self.x1[-1])
        self.e1 = np.append(self.e1, self.e[-1] - self.T * self.x2[-1])
        self.u = np.append(self.u, self.hysteresis(self.e1[-1]))
