import pandas as pd

from item_segmentation import item_seg
from item_forecast import sales_fore



def itm_proc():
    
    sales_fore()
    item_seg()
    df0 = pd.read_csv('item_scores.csv')
    df1 = df0[df0['skipped_period']!= 'no second sale']
    df1['skipped_period'] = df1['skipped_period'].astype(int)
    df_sk = df1[df1['skipped_period']< 5]


    sk_list  = df_sk['item_name'].unique()
    df2 = df0[['item_name', 'Segment']]
    df_fore = pd.read_csv('sales_forecast.csv')
    df_fore = pd.merge(df_fore, df2, on='item_name')
    df_fore1 = df_fore[df_fore['item_name'].isin(sk_list)]
    df_fore2 = df_fore[~df_fore['item_name'].isin(sk_list)]
    df_fore2['forecast'] = 0
    df_res = df_fore1.append(df_fore2)
    df_res['forecast'] = df_res['forecast'].abs()
    df_res.to_csv('item_forecast_seg.csv',index = False)
    
itm_proc()

