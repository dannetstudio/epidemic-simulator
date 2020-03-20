from epidemic import calculate_epidemic
from data import get_data

import scipy.optimize
from scipy import interpolate
import csv
import matplotlib.pyplot as plt
from matplotlib import rc
import argparse


parser = argparse.ArgumentParser()
parser.add_argument(
    "country",
    help="simulate the epidemic in this country. Ex: China")
args = parser.parse_args()


def cost_function(x):
    (a, b, c, d, e, f) = x
    v = a*10**(-b)
    K_r_0 = c*10**(-d)
    K_d_0 = e*10**(-f)
    time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim \
        = calculate_epidemic(
            C=0, v=v, x_n=x_n, y_n=y_n, t_final=60, K_r_0=K_r_0, K_r_minus=0,
            K_d_0=K_d_0, K_d_plus=0)
    interp_cases = interpolate.interp1d(
        time_sim, cases_sim, fill_value='extrapolate')
    interp_deaths = interpolate.interp1d(
        time_sim, deaths_sim, fill_value='extrapolate')
    fitness = 0
    N = 0

    for i in range(len(time_number_days)):
        if time_number_days[i] > 25:
            coeff = 1
        else:
            coeff = 1
        fitness += coeff*abs(
            deaths_ref[i] - interp_deaths(time_number_days[i])) / \
            max(deaths_ref)
        fitness += coeff*abs(
            cases_ref[i] - interp_cases(time_number_days[i])) / \
            max(cases_ref)
        N += 2*coeff

    fitness /= 2*N
    print("Fit accuracy : " + str(fitness), end='\r')

    return fitness


country = args.country
x_n = 1e5  # initial healthy population arbitrary
time, time_number_days, cases_ref, deaths_ref = get_data(country)

y_n = cases_ref[0]
x0 = (2.78, 6.08, 25, 1.9, 1, 2)
print('Fitting...')
res = scipy.optimize.minimize(cost_function, x0, method="Nelder-Mead")
x_opt = res.x
print(x_opt)

(a, b, c, d, e, f) = x_opt
v = a*10**(-b)
K_r_0 = c*10**(-d)
K_d_0 = e*10**(-f)
time_sim, cases_sim, healthy_sim, recovered_sim, deaths_sim \
    = calculate_epidemic(
        C=0, v=v, x_n=x_n, y_n=y_n, t_final=60, K_r_0=K_r_0, K_r_minus=0,
        K_d_0=K_d_0, K_d_plus=0)


def plot(x1, y1, x2, y2, ylabel, legends, color):

    fig, ax = plt.subplots()
    plt.title(country)
    plt.ylabel(ylabel)
    plt.xlabel("Days")
    plt.fill_between(x1, 0, y1, facecolor=color, alpha=0.1)
    plt.plot(x1, y1, label=legends[0],
             color=color, zorder=1)
    plt.scatter(x2, y2, label=legends[1],
                color=color, zorder=3, edgecolors="white", s=40)
    plt.minorticks_on()
    ax.grid(which='minor', alpha=0.3)
    ax.grid(which='major', alpha=0.7)
    ax.set_axisbelow(True)
    plt.legend()


plot(time_sim, cases_sim, time_number_days, cases_ref,
     "Number of actives cases",
     ["Predicted cases", "Actual cases"],
     "tab:blue")
plot(time_sim, deaths_sim, time_number_days, deaths_ref,
     "Number of actives cases",
     ["Predicted deaths", "Actual number of deaths"],
     "tab:red")

plt.show()
