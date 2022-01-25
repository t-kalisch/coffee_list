from collections import namedtuple
import altair as alt
import math
import pandas as pd
import streamlit as st
import numpy as npy
import matplotlib.pyplot as plt
import datetime
from datetime import date
import plotly
import plotly.graph_objects as go
import plotly.express as px
import streamlit_echarts as echarts
#from data_collection import *


st.set_page_config(page_title="Coffee list",page_icon="chart_with_upwards_trend",layout="wide")

"""
# Welcome to our coffee list!
In order to submit a coffee break, you need to be logged in with your username and password. Pauses are then automatically generated for you.
"""


def submit_holidays(holidays):
    st.write("Submitted holidays: "+str(holidays))

null = None
user_data=[['TK', 'akstr!admin2'],['PB','akstr!admin2'],['NV',null],['DB',null],['FLG','baddragon'],['SHK',null],['TB',null],['TT',null],['RS',null]]
simple_data=[9, 7, 15, 1879, 720, 66, 9]
monthly_coffees_total=[75,25,59,88,163,196,197,150,127,206,184,144,163,103,32]
monthly_coffees1=[]
monthly_coffees=[[19, 9, 16, 19, 29, 31, 32, 30, 14, 41, 39, 34, 37, 24, 10], [15, 6, 6, 20, 29, 20, 24, 25, 29, 22, 32, 30, 35, 18, 12], [13, 6, 12, 16, 25, 35, 28, 37, 31, 27, 36, 30, 22, 14, 0], [10, 3, 7, 12, 27, 36, 37, 15, 22, 44, 10, 6, 4, 7, 1], [18, 1, 18, 21, 34, 35, 35, 26, 21, 43, 43, 27, 36, 22, 9], [0, 0, 0, 0, 19, 27, 23, 9, 5, 16, 22, 17, 26, 17, 0], [0, 0, 0, 0, 0, 12, 18, 8, 5, 13, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0]]
monthly_ratios=[[25.33,36.0,27.12,21.59,17.9,14.8,16.24,20.0,10.94,19.9,21.31,23.33,23.13,23.0,100],[20.0,24.0,10.17,22.73,17.28,10.2,12.18,16.67,22.66,10.68,17.49,22.67,21.88,18.0,0],[17.33,24.0,20.34,18.18,15.43,17.86,14.21,24.67,24.22,13.11,19.67,18.67,13.13,13.0,0],[13.33,12.0,11.86,13.64,16.67,18.88,18.78,10.0,17.19,21.36,5.46,4.0,3.13,7.0,0],[24.0,4.0,30.51,23.86,20.99,17.86,17.77,17.33,16.41,20.87,22.95,20.0,22.5,22.0,0],[0.0,0.0,0.0,0.0,11.73,14.29,11.68,6.0,4.69,7.77,12.02,11.33,16.25,17.0,0],[0.0,0.0,0.0,0.0,0.0,6.12,9.14,5.33,3.91,6.31,1.09,0.0,0.0,0.0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0]]
total_coffees=[372, 314, 328, 242, 382, 183, 58, 1, 3]
corr_abs=[[0,229,90,123,248,124,37,0,0],[229,1,75,89,205,83,31,0,0],[90,75,160,64,94,64,22,0,0],[123,89,64,21,133,83,40,0,0],[248,205,94,133,20,130,35,0,0],[124,83,64,83,130,25,18,0,0],[37,31,22,40,35,18,11,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
perc_p_m=[[41.38,37.93,36.21,41.38,44.83,27.59,0.0,0.0,0.0],[43.66,28.17,49.3,52.11,49.3,39.44,16.9,0.0,0.0],[44.44,33.33,38.89,51.39,48.61,31.94,25.0,0.0,0.0],[46.88,39.06,57.81,23.44,40.63,14.06,12.5,0.0,0.0],[25.45,52.73,56.36,40.0,38.18,10.91,09.09,0.0,0.0],[61.19,32.84,40.3,65.67,64.18,23.88,19.4,0.0,0.0],[48.15,39.51,44.44,12.35,51.85,27.16,2.47,0.0,0.0],[56.45,54.84,45.16,9.68,48.39,27.42,0.0,0.0,0.0],[69.81,66.04,39.62,9.43,67.92,49.06,0.0,0.0,5.6],[62.16,48.65,35.14,18.92,59.46,45.95,0.0,3.2,0.0],[11,11,11,11,11,11,0,1,0]]
perc_tot=[49.4,42.1,44.7,33.4,51.0,29.0,11.0,0.0,0.0]
names=['TK','PB','NV','DB','FLG','SHK','TB','TT','RS']
months=["Nov '20","Dec '20", "Jan '21", "Feb '21", "Mar '21", "Apr '21", "May '21", "Jun '21", "Jul '21", "Aug '21", "Sep '21", "Oct '21", "Nov '21", "Dec '21", "Jan '22"]
cumulated_coffees1=[]
cumulated_coffees=[[19,28,44,63,92,121,153,183,197,238,277,312,349,372,372],[15,21,27,47,75,95,119,144,173,195,227,261,296,314,314],[13,19,31,47,72,107,135,172,203,230,266,294,315,328,328],[10,13,20,32,59,96,133,148,170,214,224,230,235,242,242],[18,19,37,58,92,127,162,188,209,252,294,324,360,382,382],[0,0,0,0,19,47,70,79,85,101,123,140,166,183,183],[0,0,0,0,0,12,30,38,43,56,58,58,58,58,58],[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],[0,0,0,0,0,0,0,0,0,0,0,0,3,3,3]]
weeks=['10/2021', '11/2021', '12/2021', '13/2021', '14/2021', '15/2021', '16/2021', '17/2021', '18/2021', '19/2021', '20/2021', '21/2021', '22/2021', '23/2021', '24/2021', '25/2021', '26/2021', '27/2021', '28/2021', '29/2021', '30/2021', '31/2021', '32/2021', '33/2021', '34/2021', '35/2021', '36/2021', '37/2021', '38/2021', '39/2021', '40/2021', '41/2021', '42/2021', '43/2021', '44/2021', '45/2021', '46/2021', '47/2021', '48/2021', '49/2021', '50/2021', '51/2021', '52/2021', '01/2022', '02/2022', '03/2022', '04/2022']
coffees_breaks_weekly=[[18, 42], [18, 38], [15, 46], [10, 14], [15, 32], [18, 50], [18, 62], [16, 46], [12, 44], [15, 45], [20, 52], [21, 44], [14, 40], [12, 30], [20, 44], [12, 26], [13, 34], [16, 30], [10, 22], [12, 23], [14, 40], [17, 44], [13, 42], [16, 51], [16, 53], [13, 31], [20, 43], [16, 46], [21, 44], [19, 46], [11, 28], [14, 31], [20, 43], [11, 31], [11, 36], [16, 42], [10, 38], [11, 33], [10, 33], [8, 25], [19, 40], [5, 19], [0, 0], [2, 3], [10, 24], [11, 37], [2, 7]]
logged_in=False


with st.sidebar:   
    st.header("Login:")
    user = st.text_input(label="", placeholder="Username")
    user_pw = st.text_input(label="", type="password", placeholder="Password")
    login = st.checkbox("Login", help="Log in with your username and password")
    hol = st.checkbox("Enter holidays")
    if login:
        for i in range(len(user_data)):
            if user == user_data[i][0] and user_pw == user_data[i][1]:
                logged_in=True
        if logged_in == True:
            st.sidebar.success("Logged in as {}".format(user))
        else:
            st.sidebar.warning("Incorrect username/password")
    st.title("Available diagrams:")
    coffees_monthly = st.checkbox("Monthly coffees")
    c_b_weekly = st.checkbox ("Weekly breaks and coffees")
    coffees_total = st.checkbox("Total coffees")
    ratio_monthly = st.checkbox("Monthly ratios")
    correlation = st.checkbox("Correlation")
    break_percentage = st.checkbox("Percentages of breaks")
    coffees_cumulated = st.checkbox("Cumulated coffees")
    
if hol:
    col1, col2 = st.columns([2,1])
    holidays = col1.date_input("Please enter your holidays", [])
    col2.write(". ")
    sub_hol = col2.button("Submit", on_click = submit_holidays(holidays))




for i in range(15):
    temp=[]
    for j in range(len(monthly_coffees)):
        temp.append(monthly_coffees[j][i])
    monthly_coffees1.append(temp)

for i in range(15):
    temp=[]
    for j in range(len(cumulated_coffees)):
        temp.append(cumulated_coffees[j][i])
    cumulated_coffees1.append(temp)

#col1, buff1, col2, buff2, col3 = st.columns([2,1,2,1,1])
#user = col1.text_input(label="", placeholder="User")
#user_pw = col2.text_input(label="", type="password", placeholder="pw")
#col3.write("")
#col3.write("")
#login = col3.button("Log In", help="Log in with your username and password", on_click=log_in(user, user_pw))

col1,col2,col3,col4 = st.columns([1,1,1,1])
col1.subheader(str(simple_data[0])+" drinkers")
col1.subheader(str(simple_data[1])+" active drinkers")
col2.subheader(str(simple_data[2])+" months of drinking")
col3.subheader(str(simple_data[4])+" coffee breaks")
col3.subheader(str(simple_data[3])+" cups of coffee")
col4.subheader(str(simple_data[5])+" data sets")
col4.subheader(str(simple_data[6])+" diagrams")


if logged_in == True:


    #-------------------------------------------------------------------------------------------------------------- monthly coffees, per person + total (line + bar chart)
    if coffees_monthly:
        st.subheader("Coffees per month")                           
        df = pd.DataFrame(monthly_coffees1, columns=names, index=months)    #coffees per month per person
        fig1 = px.line(df, title="Number of coffees per month per person", labels={"variable":"drinkers", "index":"", "value":"Number of coffees"})
        fig1.update_layout(title_font_size=24)
        st.plotly_chart(fig1, use_container_width=True)

        temp1=[]
        for i in range(len(months)):
             temp=[]
             temp.append(months[i])
             temp.append(monthly_coffees_total[i])
             temp1.append(temp)

        df = pd.DataFrame(temp1, columns={'months','total'})              #total coffees per month)
        fig2 = px.bar(df, x="total", y="months", title="Total number of coffees per month", labels={"months":"Number of coffees", "total":""}, text_auto=True)
        fig2.update_layout(title_font_size=24)
        st.plotly_chart(fig2, use_container_width=True) 

        #fig2_1 = echarts.init(temp1)
        #option = {xAxis: {type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},yAxis: {type: 'value'},series: [{data: [150, 230, 224, 218, 135, 147, 260],type: 'line'}]}

    #-------------------------------------------------------------------------------------------------------------- weekly coffees and breaks (line chart)
    if c_b_weekly:
        st.subheader("Weekly breaks and coffees")
        df = pd.DataFrame(coffees_breaks_weekly, columns={'Breaks','Coffees'}, index=weeks)
        fig3 = px.line(df, labels={"variable":"", "index":"", "value":""})
        fig3.update_layout(hovermode="x unified")
        st.plotly_chart(fig3, use_container_width=True)

    col1, col2 = st.columns([1,1])
    #-------------------------------------------------------------------------------------------------------------- total coffees (pie chart)
    if coffees_total:
        col1.subheader("Total coffees")

        temp=[]
        for i in range(len(total_coffees)):
            temp1=[]
            temp1.append(names[i])
            temp1.append(total_coffees[i])
            temp.append(temp1)
        df = pd.DataFrame(temp, columns={"names","total"}, index=names)              #total coffees pie chart
        fig3 = go.Figure(go.Pie(labels = names, values = total_coffees, sort=False, hole=.4))
        fig3.update_layout(title_font_size=24)
        col1.plotly_chart(fig3, use_container_width=True)



    #-------------------------------------------------------------------------------------------------------------- monthly ratios (stacked bar chart)
    if ratio_monthly:                                                          #with inverted months (top: Nov '20, bottom: now)
       col2.subheader("Monthly ratios")

       months_inv=[]
       temp=[]
       for i in range(len(months)):
          months_inv.append(months[len(months)-i-1])
          temp1=[]
          temp1.append(months[len(months)-i-1])
          for j in range(len(names)):
             temp1.append(monthly_ratios[j][len(months)-i-1])
          temp.append(temp1)
       temp2=[]
       temp2.append("months")
       for i in range(len(names)):
          temp2.append(names[i])

       df_stack=pd.DataFrame(temp, columns = temp2, index = months_inv)
       fig4 = px.bar(df_stack, x=names, y = months_inv, barmode = 'relative', labels={"y":"", "value":"Percentage", "variable":"drinkers"})#, text='value', text_auto=True)
       fig4.update_layout(title_font_size=24, showlegend=False)
       col2.plotly_chart(fig4, use_container_width=True)
    #if ratio_monthly:                                                          #with non-inverted months (top: now, bottom: Nov '20)
    #   col2.header("Monthly ratios")
    #   
    #   temp=[]
    #   for i in range(len(months)):
    #      temp1=[]
    #      temp1.append(months[i])
    #      for j in range(len(names)):
    #         temp1.append(monthly_ratios[j][i])
    #      temp.append(temp1)
    #   temp2=[]
    #   temp2.append("months")
    #   for i in range(len(names)):
    #      temp2.append(names[i])
    #   
    #   df_stack=pd.DataFrame(temp, columns = temp2, index = months)
    #   fig4 = px.bar(df_stack, x=names, y = months, barmode = 'relative', labels={"y":"", "value":"Percentage", "variable":"drinkers"})#, text='value', text_auto=True)
    #   fig4.update_layout(title_font_size=24)
    #   col2.plotly_chart(fig4, use_container_width=True)


    #-------------------------------------------------------------------------------------------------------------- absolute and relative correlations (bubble charts)
    if correlation:
       st.subheader("Correlation diagrams")
       col3, col4 = st.columns([1,1])                        #setting up two columns for narrower charts 
       temp=[]
       temp1=[]
       temp2=[]
       tickval_num=[]
       for i in range(len(names)):
           tickval_num.append(i+1)
           for j in range(len(names)):
               temp=[]
               temp.append(i+1)
               temp.append(j+1)
               temp.append(corr_abs[i][j])      #calculates absolute correlation
               temp2.append(temp)
       columns_corr=['x-values','y-values','size']

       df = pd.DataFrame(temp2, columns=columns_corr)
       st.write(df)
       fig5 = px.scatter(df, x='x-values', y='y-values', size='size', labels={"x-values":"", "y-values":""}, title="Absolute correlation", color='size')#, text='size')
       fig5.update_layout(title_font_size=24, showlegend=False, xaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names), yaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names))
       col3.plotly_chart(fig5, use_container_width=True)#              absolute correlation
       #                                                  --------------------------------------------------
       temp=[]#                                                        relative correlation
       temp1=[]
       temp2=[]
       tickval_num=[]
       for i in range(len(names)):
           tickval_num.append(i+1)
           for j in range(len(names)):
               temp=[]
               temp.append(i+1)
               temp.append(j+1)
               temp.append(round(100*corr_abs[i][j]/total_coffees[i],1))         #!!!!  Calculates relative correlation; uses total_coffees  !!!!
               temp2.append(temp)

       df = pd.DataFrame(temp2, columns=columns_corr)

       fig6 = px.scatter(df, x='x-values', y='y-values', size='size', labels={"x-values":"", "y-values":""}, title="Relative correlation", color='size')#, text='size')
       fig6.update_layout(title_font_size=24, showlegend=False, xaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names), yaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names))
       col4.plotly_chart(fig6, use_container_width=True)

    #-------------------------------------------------------------------------------------------------------------- percentages of breaks (line + bar charts)
    if break_percentage:
        st.subheader("Percentages of breaks")
        col5,col6 = st.columns([2,1])

        months_from_march=[]
        for i in range(len(months)-4):
            months_from_march.append(months[i+4])
        df = pd.DataFrame(perc_p_m, columns=names, index=months_from_march)
        fig7 = px.line(df, title="Monthly percentages of breaks", labels={"variable":"drinkers", "index":"", "value":"Percentage"})
        fig7.update_layout(title_font_size=24)
        col5.plotly_chart(fig7, use_container_width=True)

        percentage_total=[]
        for i in range(len(names)):
            temp=[]
            temp.append(round(perc_tot[i],1))
            percentage_total.append(temp)
        df = pd.DataFrame(percentage_total, columns={'percentage'}, index=names)

        fig8 = px.bar(df, x='percentage', y=names, title="Total percentages of breaks", labels={"y":"", "count":"Percentage", "variable":"drinkers"}, text='percentage', text_auto=True, orientation='h')
        fig8.update_layout(title_font_size=24, showlegend=False)
        col6.plotly_chart(fig8, use_container_width=True)

    #-------------------------------------------------------------------------------------------------------------- cumulated coffees monthly (line chart)
    if coffees_cumulated:
        st.subheader("Cumulated coffees")

        df = pd.DataFrame(cumulated_coffees1, columns=names, index=months)
        fig10 = px.line(df, title="Number of coffees per month per person", labels={"variable":"drinkers", "index":"", "value":"Number of coffees"})
        st.plotly_chart(fig10, use_container_width=True)

        
      

      
      
      
    
#total_points = st.slider("Number of points in spiral", 1, 5000, 2000)
#num_turns = st.slider("Number of turns in spiral", 1, 100, 9)
#test=st.slider("Test", "08.03.2021", "11.01.2022")

#Point = namedtuple('Point', 'x y')
#data = []

#points_per_turn = total_points / num_turns

#or curr_point_num in range(total_points):
#   curr_turn, i = divmod(curr_point_num, points_per_turn)
#   angle = (curr_turn + 1) * 2 * math.pi * i / points_per_turn
#   radius = curr_point_num / total_points
#   x = radius * math.cos(angle)
#   y = radius * math.sin(angle)
#   data.append(Point(x, y))

#t.altair_chart(alt.Chart(pd.DataFrame(data), height=500, width=500)
#   .mark_circle(color='#0068c9', opacity=0.5)
#   .encode(x='x:Q', y='y:Q'))
