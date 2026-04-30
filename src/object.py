import numpy as np

H_MIN = 1e-8  # Minimalny dopuszczalny krok w symulacji RK
H_MAX = 0.05  # Maksymalny dopuszczalny krok w symulacji RK
SAFETY = 0.9  # Współczynnik bezpieczeństwa do adaptacyjnego sterowania krokiem w RK
# Tolerancje do symulacji RK
# z samą względną tolerancją istniałaby szansa uszyskania tolerancji 0
# co najpewniej zatrzymałoby program
ATOL = 1e-7  # Absolute tolerance
RTOL = 1e-5  # Relative tolerance

# Maksymalna liczba kroków na sekundę, aby uniknąć nieskończonej pętli
MAX_STEPS_PER_SAMPLE = 10e6


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

    def hysteresis(self, u, prev_state=None):
        if u > self.a:
            return self.B
        elif u < -self.a:
            return -self.B
        else:
            if prev_state is not None:
                return prev_state
            elif len(self.u) > 0:
                return self.u[-1]
            else:
                return -self.B  # Default to low state if state can't be determined

    def _f(self, t, x1, x2, u, r_func):  # Wyznaczanie pochodnych x1 oraz x2
        sim_e1 = r_func(t) - x1
        sim_u = self.hysteresis(sim_e1, u)
        dx1dt = x2
        dx2dt = self.kp / self.Tp * sim_u - x2 / self.Tp
        return dx1dt, dx2dt

    def simulate(self, t_end, r_func):
        n = 0
        while self.time[-1] < t_end:
            t = self.time[-1]
            x1k = self.x1[-1]
            x2k = self.x2[-1]

            e_k = r_func(t) - x1k
            e1_k = e_k - self.T * x2k
            u_k = self.hysteresis(e1_k)

            T = np.array([0, 1 / 5, 3 / 10, 4 / 5, 8 / 9, 1, 1], dtype=np.float64)

            A = np.array(
                [
                    [0, 0, 0, 0, 0, 0, 0],
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
                ],
                dtype=np.float64,
            )

            B5 = np.array(
                [35 / 384, 0, 500 / 1113, 125 / 192, -2187 / 6784, 11 / 84, 0],
                dtype=np.float64,
            )

            B4 = np.array(
                [
                    5179 / 57600,
                    0,
                    7571 / 16695,
                    393 / 640,
                    -92097 / 339200,
                    187 / 2100,
                    1 / 40,
                ],
                dtype=np.float64,
            )

            k_x1 = np.array([0, 0, 0, 0, 0, 0, 0], dtype=np.float64)
            k_x2 = np.array([0, 0, 0, 0, 0, 0, 0], dtype=np.float64)

            for i in range(7):
                x1_step = self.dt * np.sum(A[i] * k_x1)
                x2_step = self.dt * np.sum(A[i] * k_x2)
                k_x1[i], k_x2[i] = self._f(
                    t + self.dt * T[i],
                    x1k + x1_step,
                    x2k + x2_step,
                    u_k,
                    r_func,
                )

            x1_5 = x1k + self.dt * np.sum(B5 * k_x1)
            x1_4 = x1k + self.dt * np.sum(B4 * k_x1)

            x2_5 = x2k + self.dt * np.sum(B5 * k_x2)
            x2_4 = x2k + self.dt * np.sum(B4 * k_x2)

            err1 = x1_5 - x1_4
            err2 = x2_5 - x2_4

            s1 = ATOL + RTOL * max(abs(x1k), abs(x1_5))
            s2 = ATOL + RTOL * max(abs(x2k), abs(x2_5))
            # Znormalizowany błąd
            err_norm = max(abs(err1) / s1, abs(err2) / s2)

            # Idziemy dalej jeżeli step size jest mniejszy niż minimum
            # Albo zrobiliśmy za dużo kroków na tą próbkę
            if err_norm <= 1 or self.dt <= 1e-8 or n >= MAX_STEPS_PER_SAMPLE:
                self.time = np.append(self.time, t + self.dt)
                self.x1 = np.append(self.x1, x1_5)
                self.x2 = np.append(self.x2, x2_5)
                self.e = np.append(self.e, e_k)
                self.e1 = np.append(self.e1, e1_k)
                self.u = np.append(self.u, u_k)
                n = 0  # Nowy sample, zerujemy n

            # Update step size
            if err_norm == 0:
                h = H_MAX
            else:
                h = SAFETY * self.dt * (1 / err_norm) ** (1 / 5)
            self.dt = np.clip(h, H_MIN, H_MAX)
            n += 1

    def reset(self):
        self.time = np.array([0], dtype=np.float64)  # Czas symulacji
        self.dt = 0.01  # Krok czasowy (zmienny)

        # Sygnały
        self.x1 = np.array([self.x1[0]], dtype=np.float64)  # Wyjście układu (y)
        self.x2 = np.array([self.x2[0]], dtype=np.float64)  # Pochodna wyjścia (y')
        self.e = np.array([], dtype=np.float64)  # r-y
        self.e1 = np.array([], dtype=np.float64)  # Wejście histerezy
        self.u = np.array([], dtype=np.float64)  # Wyjście histerezy
