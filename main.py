from multiprocessing import Array

import matplotlib.pyplot as plt
import numpy as np

H_MIN = 1e-8
H_MAX = 0.05
SAFETY = 0.9


class Object:
    def __init__(
        self,
        B: float,  # Wartość wyjściowa histerezy -B = low, B= high
        a: float,  # threshold hoisterezy -a i a
        kp: float,  # Wzmocnienie bloku
        Tp: float,  # W mianowniku bloku
        T: float,  # stała czasowa T
        x1o: float = 0,  # wartość początkowa x1 aka y. Default 0
        x2o: float = 0,  # wartość początkowa x2 aka y'. Default 0
    ):
        # Histereza
        self.B = B
        self.a = a
        # Transmitancja Gp
        self.kp = kp
        self.Tp = Tp
        # Sprzężenie zwrotne
        self.T = T

        self.time = np.array([0], dtype=np.float64)  # Czas symulacji
        self.dt = 0.01  # Krok czasowy (zmienny)

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

    def _f(self, x2, u):
        dx1dt = x2
        dx2dt = self.kp / self.Tp * u - x2 / self.Tp
        return dx1dt, dx2dt

    def simulate(self, t_end, r_func):

        while self.time[-1] < t_end:
            t = self.time[-1]
            x1k = self.x1[-1]
            x2k = self.x2[-1]

            e_k = r_func(t) - x1k
            e1_k = e_k - self.T * x2k
            u_k = self.hysteresis(e1_k)

            self.e = np.append(self.e, e_k)
            self.e1 = np.append(self.e1, e1_k)
            self.u = np.append(self.u, u_k)

            butcher = np.array(
                [
                    [1 / 5, 0, 0, 0, 0, 0, 0],
                    [3 / 40, 9 / 40, 0, 0, 0, 0, 0],
                    [44 / 45, -56 / 15, 32 / 9, 0, 0, 0, 0],
                    [19372 / 6561, -25360 / 2187, 64448 / 6561, -212 / 729, 0, 0, 0],
                    [
                        9017 / 3168,
                        -355 / 33,
                        46732 / 5247,
                        49 / 176,
                        -5103 / 18656,
                        0,
                        0,
                    ],
                    [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0],
                    [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0],
                    [
                        5179 / 57600,
                        0,
                        7571 / 16695,
                        393 / 640,
                        -92097 / 339200,
                        187 / 2100,
                        1 / 40,
                    ],
                ]
            )

            k1_x1, k1_x2 = self._f(x2k, u_k)
            k2_x1, k2_x2 = self._f(x2k + self.dt * butcher[0, 0] * k1_x2, u_k)
            k3_x1, k3_x2 = self._f(
                x2k + self.dt * butcher[1, 0] * k1_x2 + self.dt * butcher[2, 1] * k2_x2,
                u_k,
            )
            k4_x1, k4_x2 = self._f(
                x2k
                + self.dt * butcher[2, 0] * k1_x2
                + self.dt * butcher[2, 1] * k2_x2
                + self.dt * butcher[2, 2] * k3_x2,
                u_k,
            )
            k5_x1, k5_x2 = self._f(
                x2k
                + self.dt * butcher[3, 0] * k1_x2
                + self.dt * butcher[3, 1] * k2_x2
                + self.dt * butcher[3, 2] * k3_x2
                + self.dt * butcher[3, 3] * k4_x2,
                u_k,
            )
            k6_x1, k6_x2 = self._f(
                x2k
                + self.dt * butcher[4, 0] * k1_x2
                + self.dt * butcher[4, 1] * k2_x2
                + self.dt * butcher[4, 2] * k3_x2
                + self.dt * butcher[4, 3] * k4_x2
                + self.dt * butcher[4, 4] * k5_x2,
                u_k,
            )
            k7_x1, k7_x2 = self._f(
                x2k
                + self.dt * butcher[5, 0] * k1_x2
                + self.dt * butcher[5, 1] * k2_x2
                + self.dt * butcher[5, 2] * k3_x2
                + self.dt * butcher[5, 3] * k4_x2
                + self.dt * butcher[5, 4] * k5_x2
                + self.dt * butcher[5, 5] * k6_x2,
                u_k,
            )

            x1_5 = x1k + self.dt * (
                butcher[6, 0] * k1_x1
                + butcher[6, 2] * k3_x1
                + butcher[6, 3] * k4_x1
                + butcher[6, 4] * k5_x1
                + butcher[6, 5] * k6_x1
            )
            x1_4 = x1k + self.dt * (
                butcher[7, 0] * k1_x1
                + butcher[7, 2] * k3_x1
                + butcher[7, 3] * k4_x1
                + butcher[7, 4] * k5_x1
                + butcher[7, 5] * k6_x1
                + butcher[7, 6] * k7_x1
            )

            x2_5 = x2k + self.dt * (
                butcher[6, 0] * k1_x2
                + butcher[6, 2] * k3_x2
                + butcher[6, 3] * k4_x2
                + butcher[6, 4] * k5_x2
                + butcher[6, 5] * k6_x2
            )
            x2_4 = x2k + self.dt * (
                butcher[7, 0] * k1_x2
                + butcher[7, 2] * k3_x2
                + butcher[7, 3] * k4_x2
                + butcher[7, 4] * k5_x2
                + butcher[7, 5] * k6_x2
                + butcher[7, 6] * k7_x2
            )

            atol = 1e-7  # Absolute tolerance
            rtol = 1e-5  # Relative tolerance

            err1 = x1_5 - x1_4
            err2 = x2_5 - x2_4

            s1 = atol + rtol * max(abs(x1k), abs(x1_5))
            s2 = atol + rtol * max(abs(x2k), abs(x2_5))
            # Znormalizowany błąd
            err_norm = max(abs(err1) / s1, abs(err2) / s2)

            # Idziemy dalej jeżeli step size jest mniejszy niż minimum
            if err_norm <= 1 or self.dt <= 1e-8:
                self.time = np.append(self.time, t + self.dt)
                self.x1 = np.append(self.x1, x1_5)
                self.x2 = np.append(self.x2, x2_5)

            # Update step size
            if err_norm == 0:
                h = H_MAX
            else:
                h = SAFETY * self.dt * (1 / err_norm) ** (1 / 5)
            self.dt = np.clip(h, H_MIN, H_MAX)
