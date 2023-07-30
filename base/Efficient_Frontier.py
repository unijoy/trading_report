import numpy as np

from base.markowitz import MarkPortOpt, PVol, EReturn



def run(data, r_bar, optimazer):
    # Print the number of target returns actually specified:
    numR = len(r_bar)
    print("Number of targeted returns (or r-bar) specified is: ", numR)

    data_train_mean = data.mean()
    data_train_cov_mat = data.cov()
    # Two lists to record the volatility and expected return for each portfilio
    port_vol = []
    port_return = []

    # A matrix storing the portfolio alloaction
    alloc_r = np.zeros((len(data.columns), numR))

    # Solve the Markowitz problem for each r-bar and output the results
    for i in range(numR):
        r = r_bar[i]
        print("* For the case r-bar = ", round(r * 100, 3), "%:")
        sol = optimazer(data=data, target_return=r, data_mean=data_train_mean, data_cov=data_train_cov_mat,
                        silent=True)

        if (not sol['success']):  # check if the optimizer exit successfully
            print("NOTE: solution to this r-bar will be dropped!")
        else:  # only keeping the r-bar that has sucessful optmization
            print(sol['message'])
            alloc_r[:, i] = sol['x']
            port_vol.append(sol['fun'])
            port_return.append(EReturn(sol['x'], data_train_mean))
        print("")

    port_vol = np.asarray(port_vol)
    port_return = np.asarray(port_return)

    num_rbar = len(port_vol)  # update the number of r-bar recorded/kept
    print("The number of recoreded the efficient frontier points is:", num_rbar)
    return alloc_r, port_return, port_vol


def gen_bars(freq=250):
    # todo hard code
    return [(1 + i / 100) ** (1 / freq) - 1 for i in range(10, 210, 10)]



