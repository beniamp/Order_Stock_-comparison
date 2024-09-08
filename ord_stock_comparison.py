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
import matplotlib.pyplot as plt

# Streamlit cache to load data
@st.cache_data
def load_data():
    df = pd.read_excel('stock_facts.xlsx')
    df_orders = pd.read_csv('Orders.csv')
    return df, df_orders

df, df_orders = load_data()

# Helper function: Convert Persian to Gregorian date
def persian_to_gregorian(date):
    year, month, day = map(int, date.split('-'))
    persian_date = jdatetime.date(year, month, day)
    return persian_date.togregorian()

# Filter Persian dates in df_orders
df_orders = df_orders[df_orders['Date_Formatted'] > '1403-05-09']

# Apply date conversion
df_orders['Gregorian_Date'] = df_orders['Date_Formatted'].apply(persian_to_gregorian)
df['Gregorian_Date'] = df['Date_Formatted'].apply(persian_to_gregorian)

# Replace category value with the correct one
df['Category'] = df['Category'].replace('گوشی موبایل ', 'گوشی موبایل')

# Generate category options for selection
categories_ord = ['All categories'] + df_orders['Category'].unique().tolist()
categories_stc = ['All categories'] + df['Category'].unique().tolist()

# Sort the dates
sorted_dates_gregorian = sorted(df_orders['Gregorian_Date'].unique())

# Date range selection in Streamlit UI
b1, b2 = st.columns(2)
start_date, end_date = b1.date_input(
    'Select Date Range', 
    value=[sorted_dates_gregorian[0], sorted_dates_gregorian[-1]],
    min_value=sorted_dates_gregorian[0], 
    max_value=sorted_dates_gregorian[-1]
)

# Category selection
selected_category = b2.selectbox('Select Category', categories_ord)

# Helper function: Convert Gregorian date to Persian date
def gregorian_to_persian(gregorian_date):
    persian_date = persian.from_gregorian(gregorian_date.year, gregorian_date.month, gregorian_date.day)
    return f'{persian_date[0]:04}-{persian_date[1]:02}-{persian_date[2]:02}'

# Display the current selected period range
start_date_persian = gregorian_to_persian(start_date)
end_date_persian = gregorian_to_persian(end_date)
st.write(f'Current Period Range: {start_date_persian} to {end_date_persian}')

# Filter data by selected category and date range
if selected_category != 'All categories':
    filtered_ord = df_orders[df_orders['Category'] == selected_category]
    filtered_stc = df[df['Category'] == selected_category]
else: 
    filtered_ord = df_orders
    filtered_stc = df

filtered_ord = filtered_ord[(filtered_ord['Gregorian_Date'] >= start_date) & (filtered_ord['Gregorian_Date'] <= end_date)]
filtered_stc = filtered_stc[(filtered_stc['Gregorian_Date'] >= start_date) & (filtered_stc['Gregorian_Date'] <= end_date)]

# Aggregation of stock and order data
agg_stock = filtered_stc.groupby(['Name', 'Date_Formatted', 'Category', 'Brand']).agg({'Quantity': 'max', 'BasePrice': 'min'}).reset_index()
agg_order = filtered_ord.groupby(['ProductName', 'Date_Formatted', 'Category']).agg({'Quantity': 'sum', 'UnitBasePrice': 'min'}).reset_index()


# Add a bar plot for stock quantities by category and date
agg_stock_bar = filtered_stc.groupby(['Date_Formatted', 'Category']).agg({'Quantity': 'sum'}).reset_index()

# Plotly bar plot
fig = px.bar(agg_stock_bar, 
             x='Date_Formatted', 
             y='Quantity', 
             color='Category', 
             title='Stock Quantities by Category Over Time')
# Bar plot for order quantities
fig.add_trace(go.line(
    x=agg_order['Date_Formatted'], 
    y=agg_order['Quantity'], 
    name='Order Quantity',
    marker_color='red'
))

# Update layout to ensure bars are stacked
fig.update_layout(
    title="Stock and Order Quantities by Date",
    xaxis_title="Date",
    yaxis_title="Quantity",
    barmode='overlay',  # Allows overlay of bars
    xaxis_type='category',  # Treat x-axis as categorical
    bargap=0.15  # Slight gap between bars
)

# Display the bar plot in Streamlit
st.plotly_chart(fig)


# Product selection
products = filtered_stc['Name'].unique()
selected_product = st.selectbox('Select Product', products)

# Filter aggregated data by selected product
agg_order = agg_order[agg_order['ProductName'] == selected_product]
agg_stock = agg_stock[agg_stock['Name'] == selected_product]

# Merge the stock and order data on 'Date_Formatted'
merged_data = pd.merge(agg_stock[['Date_Formatted', 'Quantity']], 
                       agg_order[['Date_Formatted', 'Quantity']], 
                       on='Date_Formatted', 
                       how='outer', 
                       suffixes=('_stock', '_order'))

# Fill missing values with 0
merged_data.fillna(0, inplace=True)

# Plot the merged data as a line plot
plt.figure(figsize=(12, 6))
plt.plot(merged_data['Date_Formatted'], merged_data['Quantity_stock'], label='Stock Quantity', color='blue')
plt.plot(merged_data['Date_Formatted'], merged_data['Quantity_order'], label='Order Quantity', color='red')
plt.xlabel('Date')
plt.ylabel('Volume/Quantity')
plt.title('Volume/Quantity Over Time')
plt.xticks(rotation=45)
plt.legend()

# Display the line plot in Streamlit
st.pyplot(plt)


