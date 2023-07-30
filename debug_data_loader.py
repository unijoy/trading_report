import pandas as pd

def load_data():
    file_name = 'data/ReturnsData_Daily.csv'
    df = pd.read_csv(file_name, low_memory=False, index_col=0)  # set the first column (date) as index
    df.index = pd.to_datetime(df.index)  # set index (i.e. date) as a datetime object
    df = df.drop('BABA', axis=1)  # drop BABA return data from our dataframe
    df = df.dropna()  # drop rows which contain missing values.
    df_week = (df + 1).resample('W').prod() - 1
    df_week = df_week.drop(df_week.index[[0]])  # mannually remove the returns data for the first week
    df_week = df_week.drop(df_week.index[[-1]])  # mannually remove the returns data for the last week
    SP500 = df_week[['SP500']]
    data = df_week.drop('SP500', axis=1)

    file_name = 'data/WTB3MS.csv'  # datafile downloaded from FRED
    df = pd.read_csv(file_name)

    df['DATE'] = pd.to_datetime(df['DATE'])  # set the DATE column as datetime object
    df['WTB3MS'] = pd.to_numeric(df['WTB3MS'], errors='coerce')  # set the return column as numeric

    RET_data = pd.DataFrame(columns=['RET'], index=df.DATE)  # create a new dataframe
    RET_data['RET'] = (df['WTB3MS'].values / 100 + 1) ** (1 / 52) - 1  # edit the unit of the return data

    RET_data_weekly = (RET_data['RET'] + 1).resample(
        'W').prod() - 1  # convert the data to the same weekly frequency as above
    TBill = pd.DataFrame(columns=['T-Bill'], index=RET_data_weekly.index)
    TBill['T-Bill'] = RET_data_weekly

    ind = (TBill.index >= df_week.index[[0]][0]) * (TBill.index <= df_week.index[[-1]][0])
    TBill = TBill[ind]

    start_date = '2010-12-19'
    end_date = '2020-06-28'

    ind = (data.index >= start_date) * (data.index <= end_date)

    data = data[ind]

    SP500 = SP500[ind]

    TBill = TBill[ind]

    start_date_train = '2010-12-19'
    end_date_train = '2020-06-28'

    ind = (data.index >= start_date_train) * (data.index <= end_date_train)
    # data_train = data[ind].copy()
    # SP500_train = SP500[ind].copy()
    # TBill_train = TBill[ind].copy()

    return {'data': data, 'rf': TBill['T-Bill'], 'benchmark': SP500, 'freq': 52}