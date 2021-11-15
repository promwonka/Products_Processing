import pandas as pd
from statsmodels.graphics.tsaplots import plot_acf,plot_pacf
import statsmodels.api as sm



def sales_fore():

    df = pd.read_csv('sales_all.csv')
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['sale_price'] = df['sale_price'] * df['billed_quantity']
    df = df[['date', 'sale_price', 'item_name']]
    df = df.groupby(['date','item_name'])['sale_price'].sum().reset_index()
    df['date'] = pd.to_datetime(df['date'], errors='coerce')

    df['quarters'] = df.date.dt.month
    df['year'] = pd.DatetimeIndex(df['date']).year
    df['QY']= df['year'].astype(str) + df['quarters'].astype(str)
    df.sort_values("QY", axis = 0, ascending = True, inplace = True, na_position ='last') 
    qy_val = df.QY.unique() 
    list_cust = df['item_name'].unique().tolist()


    #future dates

    strl = qy_val.max()
    splitat = 4
    yr, month = strl[:splitat], strl[splitat:]

    yr = int(yr) 
    month = int(month) 


    i= month
    j = 0
    yrs = yr
    lm = []
    ly = []
    lmy = []

    while(j<12):

        i = i+1
        if i > 12:
            yrs = yr +1
            i = 1
            lm.append(str(i))
            ly.append(str(yrs))

        else:
            lm.append(str(i))
            ly.append(str(yrs))

        lmy.append(ly[j] + lm[j])
        j = j+1

    future_dates = pd.DataFrame(lmy, columns = ['QY'])
    future_dates['item_name'] = 'xyz'
    future_dates['sale_price'] = 0
    future_dates.set_index('QY',inplace=True)




    l = len(qy_val)

    i=0
    while(i<l):
        globals()['df%s' % i] = df[df['QY']==qy_val[i]]
        i = i+1


    i = 0
    while (i<l):

        globals()['df%s' % i] = globals()['df%s' % i].groupby(['QY','item_name'])['sale_price'].sum().reset_index()
        list_cust_quart = globals()['df%s' % i]['item_name'].unique().tolist()
        c = list(set(list_cust).difference(set(list_cust_quart)))
        xtra = {'item_name': c}
        globals()['df%s' % i] = globals()['df%s' % i].append(pd.DataFrame(xtra))
        uni = globals()['df%s' % i]['QY'].unique()
        globals()['df%s' % i]['sale_price'] = globals()['df%s' % i]['sale_price'].fillna(0)
        globals()['df%s' % i]['QY'] = globals()['df%s' % i]['QY'].fillna(uni[0])
        globals()['df_final%s' % i] = globals()['df%s' % i][['item_name','sale_price','QY']].copy() 


        i= i+1



    i = 0
    list_of_dataframes = []
    while(i<l):
        list_of_dataframes.append(globals()['df_final%s' % i])
        i = i+1

    df_all = pd.concat(list_of_dataframes)

    df_all.set_index('QY',inplace=True)

    cl = len(df['item_name'].unique())

    i=0
    while(i<cl):
        globals()['df_cust%s' % i] = df_all[df_all['item_name']==list_cust[i]]
        future_dates['item_name'] = list_cust[i]
        globals()['df_cust%s' % i] = globals()['df_cust%s' % i].append(future_dates, ignore_index=False, sort=False)
        i = i+1



    ln = len(qy_val)
    
    i=0
    while(i<cl):

        model=sm.tsa.statespace.SARIMAX(globals()['df_cust%s' % i]['sale_price'],order=(0, 1, 0),seasonal_order=(0,1,0,12))
        results=model.fit()
        globals()['df_cust%s' % i]['forecast']=results.predict(start=(ln-5),end=(ln+10),dynamic=True)
        i = i+1



    df_major = globals()['df_cust%s' % 8].copy()
    df_major = df_major[0:0]

    i=0
    while(i<cl):
        df_major = df_major.append(globals()['df_cust%s' % i])

        i = i+1

    df_major['QY'] = df_major.index

    df_major.to_csv('sales_forecast.csv', index = False)
   
    
    