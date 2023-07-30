import numpy as np
from scipy.optimize import minimize

# # Function to compute the expected return for the portfolio
def EReturn(w, data_mean):
    EReturn = w @ data_mean
    return EReturn


# Function to compute the portfolio standard deviation
def PVol(w, data_cov_mat):
    pvar = w @ data_cov_mat @ w
    return np.sqrt(pvar)


# Function to solve for the optimal solution to the Markowitz Portfolio Optimization Problem
# with specified target return r
# 给定expected returnp，找到weights，使ortfolito volatility最小
def MarkPortOpt(data, target_return,data_mean,data_cov, silent=False):
    # Constraints
    def constraint1(w):
        return np.sum(w) - 1.0  # budget constraint

    def constraint2(w):
        return 1.0 - np.sum(w)  # budget constraint

    def constraint3(w):
        return w  # nonnegative constraint

    def constraint4(w):
        diff = EReturn(w,data_mean=data_mean) - target_return
        return diff  # return constraint

    con1 = {'type': 'ineq', 'fun': constraint1}
    con2 = {'type': 'ineq', 'fun': constraint2}
    con3 = {'type': 'ineq', 'fun': constraint3}
    con4 = {'type': 'ineq', 'fun': constraint4}
    cons = ([con1, con2, con3, con4])

    # Initial x0
    w0 = np.ones(len(data.columns))

    # Solve the problem
    sol = minimize(PVol, w0, args=(data_cov,), method='SLSQP', constraints=cons)

    # Whether the solution will be printed
    if (not silent):
        print("Solution to the Markowitz Problem with r =  ", round(target_return * 100, 3), "%:")
        print(sol)
        print("")
    elif (not sol['success']):  # check if the optimizer exit successfully
        print("WARNING:  the optimizer did NOT exit successfully!!")

    return sol


def load_data():
    pass

if __name__ == '__main__':
    data = load_data()

    data_train = data['data_train']

    # Find the solution given a specified target return r
    sol = MarkPortOpt(data=data_train, target_return=0.001, silent=False)
