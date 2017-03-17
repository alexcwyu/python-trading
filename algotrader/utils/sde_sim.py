import math

import numpy as np


def euler(drift, diffusion, x0, T, Tstep, Nsim):
    """
    Simulate solution of Stochastic Differential Equation by discretization using
    Euler's method
    :param drift: lambda function with signature x, t
    :param diffusion: lambda function with signature x, t
    :param x0: initial position
    :param T: terminal time in double
    :param Tstep: number of time steps
    :param Nsim: number of path simulated
    :return: np array of simulated stochastic process
    """
    dt = T / (Tstep - 1)
    dW = np.random.normal(0, math.sqrt(dt), Nsim * Tstep).reshape(Nsim, Tstep)

    x = np.zeros([Nsim, Tstep])
    t = np.linspace(0, T, Tstep)
    x[:, 0] = x0

    for i in range(1, Tstep):
        x[:, i] = x[:, i - 1] + drift(x[:, i - 1], t[i - 1]) * dt + diffusion(x[:, i - 1], t[i - 1]) * dW[:, i - 1]
    return x


def euler2d(drift0, drift1, diffusion0, diffusion1, rho, x0, y0, T, Tstep, Nsim):
    """
    :param drift0:
    :param drift1:
    :param diffusion0:
    :param diffusion1:
    :param rho:
    :param x0:
    :param y0:
    :param T:
    :param Tstep:
    :param Nsim:
    :return:
    """
    dt = T / (Tstep - 1)
    dW0 = np.random.normal(0, dt, Nsim * Tstep).reshape(Nsim, Tstep)
    dW1 = np.random.normal(0, dt, Nsim * Tstep).reshape(Nsim, Tstep)

    x = np.zeros([Nsim, Tstep])
    y = np.zeros([Nsim, Tstep])
    t = np.linspace(0, T, Tstep)

    x[:, 0] = x0
    y[:, 0] = y0

    for i in range(1, Tstep):
        dWy = rho * dW0[:, i - 1] + np.sqrt(1.0 - rho ** 2) * dW1[:, i - 1]
        x[:, i] = x[:, i - 1] + drift0(x[:, i - 1], y[:, i - 1], t[i - 1]) * dt \
                  + diffusion0(x[:, i - 1], y[:, i - 1], t[i - 1]) * dW0[:, i - 1]
        y[:, i] = y[:, i - 1] + drift1(x[:, i - 1], y[:, i - 1], t[i - 1]) * dt \
                  + diffusion1(x[:, i - 1], y[:, i - 1], t[i - 1]) * dWy[:, i - 1]

    return x, y
