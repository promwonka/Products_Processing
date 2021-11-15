from datetime import datetime, timedelta
import pandas as pd
from sklearn.cluster import KMeans
from sklearn.preprocessing import MinMaxScaler
import glob


def item_seg():
    df = pd.read_csv('sales_all.csv')

    df['date'] = pd.to_datetime(df['date']).dt.date
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df['sale_price'] = df['billed_quantity']*(df['sale_price'])
    df['cost_price'] = df['billed_quantity']*(df['cost_price'])
    df['profit'] = (df['sale_price'] - df['cost_price'])

    df_bq = df.groupby('item_name').billed_quantity.sum().reset_index()
    df_bq.columns = ['item_name','bq']

    df_date = df.groupby('item_name').date.max().reset_index()
    df_date.columns = ['item_name','date']

    df_profit = df.groupby('item_name').profit.sum().reset_index()
    df_profit.columns = ['item_name','profit']

    df_sales = df.groupby('item_name').sale_price.sum().reset_index()
    df_sales.columns = ['item_name','sales']


    counts_item = {}
    counts_item = df['item_name'].value_counts().to_dict()
    df['invoice_freq'] = df['item_name'].map(counts_item)  

    df_invoice_freq = df[['item_name','invoice_freq']]
    df_invoice_freq = df_invoice_freq.drop_duplicates()

    df_user = pd.merge(df_invoice_freq,df_bq, on='item_name')  
    df_user = pd.merge(df_user,df_profit, on='item_name')  
    df_user = pd.merge(df_user,df_date, on='item_name')  
    df_user = pd.merge(df_user,df_sales, on='item_name')
    df_user['margin'] = df_user['profit']/df_user['sales']


    df_user['bq'] = df_user.bq.rank(pct = True) 
    df_user['invoice_freq'] = df_user.invoice_freq.rank(pct = True) 
    df_user['profit'] = df_user.profit.rank(pct = True) 


    df_user['bq'] = df_user['bq']*100
    df_user['invoice_freq'] = df_user['invoice_freq']*100
    df_user['profit'] = df_user['profit']*100
    df_user['margin'] = df_user['margin']*100


    df_user['Fast Moving Score'] = 0.5*(df_user['bq'] + df_user['invoice_freq'])
    df_user['overall_score'] = 0.5*(df_user['Fast Moving Score'] + df_user['profit'])


    df_user['Segment'] = 'Low-Value'
    df_user.loc[df_user['overall_score'] > 40,'Segment'] = 'Average' 
    df_user.loc[df_user['overall_score'] > 80,'Segment'] = 'High-Value' 


    df_user.to_csv('fast_score.csv', index = False)



    df = pd.read_csv('sales_all.csv')
    df['date'] = pd.to_datetime(df['date']).dt.date
    df['date'] = pd.to_datetime(df['date'], errors='coerce')
    df.sort_values(['item_name', 'date'])
    df = df.groupby(['date','item_name'])['sale_price'].sum().reset_index()


    df_last = df.groupby(['item_name'])['date'].max().reset_index()
    df['difference'] = df.groupby('item_name')['date'].diff().dt.days.fillna(0).astype(int)
    df['difference'] = df.groupby('item_name')['date'].diff().dt.days.fillna(0).astype(int)

    df_mean = df.groupby(['item_name'])['difference'].mean().reset_index()
    df_mean.columns = ['item_name', 'mean_period']


    last_sale = df.date.max()
    list_cust = df['item_name'].unique().tolist()
    cl = len(df['item_name'].unique())


    i = 0
    list_cn = []
    list_prd = []

    while (i<cl):


        num = (df_mean[df_mean['item_name']==list_cust[i]].mean_period).reset_index()
        x = num.iloc[0]['mean_period']

        if (last_sale > df[df['item_name']==list_cust[i]].date.max() + timedelta(days = x)):
           #(‘last sale date’ - ‘last purchase date’)/(‘mean purchase period’)
            if x == 0:
                skip_prd = 'no second sale'
                list_cn.append(list_cust[i]) 
                list_prd.append(skip_prd)

            else:            
                skip_prd = ((last_sale - df[df['item_name']==list_cust[i]].date.max())/x).days
                list_cn.append(list_cust[i]) 
                list_prd.append(skip_prd)

        else:

            list_cn.append(list_cust[i]) 
            list_prd.append(0)



        i = i+1



    data = {'item_name': list_cn, 
            'skipped_period': list_prd}  
    new = pd.DataFrame.from_dict(data) 


    df_final_merge = pd.merge(df_mean,new, how='left', left_on=["item_name"], right_on=["item_name"])




    df_final_merge = df_final_merge.replace(['no second purchase'],'no second sale')

    df_user = pd.merge(df_user,df_final_merge, on='item_name') 

    df_user = df_user.round(0)
    df_user.to_csv('item_scores.csv', index = False)

