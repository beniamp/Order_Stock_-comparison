# -*- coding: utf-8 -*-
"""
Created on Sun Sep  8 11:41:20 2024

@author: b.aminpour
"""

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import jdatetime
from convertdate import persian
import streamlit as st



df = pd.read_excel('stock_facts.xlsx')
df_orders = pd.read_csv('Orders.csv')





# Configution of widget 

def persian_to_gregorian(date):
  year, month, day = date.split('-')
  year = int(year)
  month = int(month)
  day = int(day)
  
  persian_date = jdatetime.date(year, month, day)
  gre_date = persian_date.togregorian()
  return gre_date

df_orders = df_orders[df_orders['Date_Formatted'] > '1403-05-09']

df_orders['Gregorian_Date'] = df_orders['Date_Formatted'].apply(persian_to_gregorian)
df['Gregorian_Date'] = df['Gregorian_Date'].apply(persian_to_gregorian)

df['Category'] = df['Category'].replace('گوشی موبایل ', 'گوشی موبایل')
categories_ord = ['All categories'] + df_orders['Category'].unique().tolist()
categories_stc = ['All categories'] + df['Category'].unique().tolist()

sorted_dates_gregorian = df_orders['Gregorian_Date'].unique()
sorted_dates_gregorian = sorted(sorted_dates_gregorian)

# date range selection
b1, b2 = st.columns(2)
start_date, end_date = b1.date_input(
    'Select Date Range', 
    value=[sorted_dates_gregorian[0], sorted_dates_gregorian[-1]],
    min_value=sorted_dates_gregorian[0], 
    max_value=sorted_dates_gregorian[-1]
)
selected_category = b2.selectbox('Select Category', categories_ord)


def gregorian_to_persian(gregorian_date):
  persian_date = persian.from_gregorian(gregorian_date.year,
                                        gregorian_date.month,
                                        gregorian_date.day)
  return f'{persian_date[0]:04}-{persian_date[1]:02}-{persian_date[2]:02}'


start_date_persian = gregorian_to_persian(start_date)
end_date_persian = gregorian_to_persian(end_date)

st.write(f'Current Period Range: {start_date_persian} to {end_date_persian}')


if selected_category != 'All categories':
  filtered_ord = df_orders[df_orders['Category'] == selected_category]
  filtered_stc = df[df['Category'] == selected_category]
else: 
  filtered_ord = df_orders
  filtered_stc = df



filtered_ord = filtered_ord[(filtered_ord['Gregorian_Date'] >= start_date) &
                            (filtered_ord['Gregorian_Date'] <= end_date)]
filtered_stc = filtered_stc[(filtered_stc['Gregorian_Date'] >= start_date) &
                            (filtered_stc['Gregorian_Date'] <= end_date)]


agg_stock = filtered_stc.groupby(['Name', 'Color', 'Date_Formatted', 'Category', 'Brand']).agg({'Quantity': 'sum', 'BasePrice': 'min'}).reset_index()
agg_order = filtered_ord.groupby.groupby(['ProductColorName', 'ColorName', 'Date_Formatted', 'Category']).agg({'Quantity': 'sum', 'BasePrice': 'max'}).reset_index()




st.dataframe(agg_stock)
st.dataframe(agg_order)