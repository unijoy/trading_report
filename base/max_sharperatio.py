import numpy as np
from scipy.optimize import minimize

from base.markowitz import PVol
from base.metrics import ann_ret, ann_std


# Function to find the optimal portfolio that maximize the Sharpe ratio
# Returns the optimal solution
def MaxSR(data, rf,freq,data_cov_mat, silent=False):
    # Function to compute the annualized sharpe ratio for the portfolio given portfolio weight
    # Note that it returns the -1 * Annualized Sharpe Ratio
    def AnnSR(w, data, rf,freq):
        excess_ret = data @ w - rf
        AnnSR = ann_ret(excess_ret.mean(),freq) / ann_std(PVol(w,data_cov_mat),freq)
        return AnnSR

    # Objective Function
    def SR(w):
        excess_ret = data @ w - rf
        SR = (excess_ret.mean()) / (PVol(w,data_cov_mat))
        return -SR

    n = len(data.columns)

    # Bounds
    bnds = tuple((0, 1) for i in range(n))  # nonnegativity constraint

    # Constraints
    def constraint1(w):
        return np.sum(w) - 1.0  # budget constraint

    def constraint2(w):
        diff = 0.25 * np.ones(len(data.columns)) - w
        return diff

    con1 = {'type': 'eq', 'fun': constraint1}
    cons = ([con1])
    # con2 = {'type': 'ineq', 'fun': constraint2}
    # cons = ([con1, con2])
    # Initial x0
    w0 = np.array(np.ones(n))

    # Solve the problem
    sol = minimize(SR, w0, method='SLSQP', bounds=bnds, constraints=cons)

    # Whether the solution will be printed
    if (not silent):
        print("Solution to the Max Sharpe Ratio Problem is:")
        print(sol)
        print("")
    elif (not sol['success']):  # check if the optimizer exist successfully
        print("WARNING:  the optimizer did NOT exit successfully!!")

    return sol, AnnSR(sol['x'], data, rf,freq)

