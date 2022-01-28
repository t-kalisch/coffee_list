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
import mysql.connector as mysql
from data_collection import *
from calculations import *
#import change_password


st.set_page_config(page_title="Coffee list",page_icon="chart_with_upwards_trend",layout="wide")



def submit_holidays(holidays):
    st.write("Submitted holidays: "+str(holidays))

null = None
user_data=get_user_data()
simple_data=get_simple_data()
monthly_coffees_total=get_monthly_coffees_total()
monthly_coffees1=[]
monthly_coffees=get_monthly_coffees()
monthly_ratios=get_monthly_ratios()
total_coffees=get_total_coffees()
corr_abs=get_corr()
perc_p_m=get_perc_p_m()
perc_tot=get_perc_tot()
names=get_names()
months=get_months()
cumulated_coffees1=[]
cumulated_coffees=get_cumulated_coffees()
weeks=get_weeks()
coffees_breaks_weekly=get_coffee_breaks_weekly()
last_breaks=get_last_breaks()
logged_in=False
admin_status=0


with st.sidebar:
    #page_nav = st.selectbox('Page navigation', ("Login","Data visualisation"), 0)
    #if page_nav == 'Login':
    
    col1,col2 = st.columns([1,1.65])
    user = col1.text_input(label="", placeholder="Username")
    user_pw = col2.text_input(label="", type="password", placeholder="Password")
    login = col1.checkbox("Login", help="You are logged in while this checkbox is ticked")

if login:
    for i in range(len(user_data)):
        if user == user_data[i][0] and user_pw == user_data[i][1]:
            admin_status=user_data[i][2]
            logged_in=True
    if logged_in == True:
        st.title("Logged in as {}".format(user))
        if admin_status == 1:
            col2.write("Status: Administrator")
        else:
            st.sidebar.write("Member status: User") 
    else:
        st.title("Welcome to the future of coffee drinking")
        st.write("In order to get access to the visualised data you need to be logged in with your username and password.")
else:
    st.title("Welcome to the future of coffee drinking")
    st.write("In order to get access to the visualised data you need to be logged in with your username and password.")
    

if logged_in == True:
    if admin_status != 1:
        profile_nav = st.sidebar.selectbox("Profile Options", ("Show diagrams","Enter holidays","Change username","Change password"), 0)
    elif logged_in == True and admin_status == 1:
        profile_nav = st.sidebar.selectbox("Profile Options", ("Show diagrams","Submit coffee break","Delete coffee break","Enter holidays","Change profile data"), 0)
    
    if profile_nav == "Enter holidays":                                             # Enter holidays page
        st.subheader("Enter holidays")
        col1, col2 = st.columns([2,1])
        holidays = col1.date_input("Please enter your holidays", [])
        col2.write(". ")
        sub_hol = col2.button("Submit", on_click = submit_holidays(holidays))
        if admin_status == 1:
            st.write("-" * 34)
            st.subheader("Enter holidays for another person")
            col1,col2 = st.columns([1,3])
            col1.text_input("Person", placeholder = "User")
            holidays_admin = col2.date_input("Holidays", [])
            st.button("Submit holidays")
        
    if profile_nav == "Change username":                                            # Change username page
        st.subheader("Change username")
        if admin_status != 1:
            st.markdown("Please enter your current username, password and new username.")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            curr_user = col2.text_input("Username", placeholder = "Username")
            user_pw = col2.text_input("Password", type="password", placeholder = "Password")
            col2.write("-" * 34)
            new_user = col2.text_input("Choose a new username", placeholder = "Username")
            user_change = col2.button("Save new username")
        if admin_status == 1:
            st.markdown("Change username for a member.")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            curr_user = col2.text_input("Old username", placeholder = " Old username")
            user_pw = col2.text_input("New username", placeholder = "New username")
            col2.write("-" * 34)
            new_user = col2.text_input("Please enter your password", type = 'password', placeholder = "Password")
            user_change = col2.button("Confirm")
        
    if profile_nav == "Change password":                                            # Change password page
        st.subheader("Change password")
        if admin_status != 1:
            st.markdown("You can change your password here.")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            curr_user = col2.text_input("Current password", type="password", placeholder = "Old password")
            col2.write("-" * 34)
            col1,col2,col3 = st.columns([0.5,1,0.7])
            user_pw = col2.text_input("Choose a new password", type="password", placeholder = "New password")
            new_user = col2.text_input("Repeat the new password", type="password", placeholder = "Repeat password")
            pw_change = col2.button("Save new password")
        if admin_status == 1:
            st.markdown("Change password for another person")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            col2.text_input("Username", placeholder = "User")
            col2.text_input("New password", type = 'password', placeholder = "Password")
            col2.write("-" * 34)
            col2.text_input("Please enter your password to confirm", type = 'password', placeholder = "Password")
            col2.button("Confirm")        
 
    if profile_nav == "Change profile data":
        st.subheader("Change the profile of a member")
        st.markdown("You can enter a new username and password for a member, or change their member status.")
        col1,col2,col3 = st.columns([0.5,1,0.7])
        change_user = col1.text_input("User", placeholder = "Username")
        col2.text_input("New username", placeholder = "Username")
        col2.text_input("New password", type = "password", placeholder = "Password")
        status=-1
        if change_user != "":
            for i in range(len(user_data)):
                if user_data[i][0] == change_user:
                    if user_data[i][2] == 1:
                        status=1
                    else:
                        status=0
        col1,col2 = st.columns([0.5,1.7])
        if status == -1:
            col1.selectbox ("Change member status", (""), 0)
        else: 
            col1.selectbox ("Change member status", ("User", "Admin"), status)
        st.write("-" * 34)
        col1,col2 = st.columns([0.5,0.5])
        col1.text_input("Please enter your password to confirm", type = 'password', placeholder = "Password")
        col1.button("Confirm")       

    if profile_nav == "Submit coffee break":                                        # Submit break page
        st.subheader("Submit a coffee break")
        st.markdown("Please enter the names and number of coffees for the break.")
        col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
        p1_coffees = col6.text_input("Person 1")
        p2_coffees = col7.text_input("Person 2")
        p3_coffees = col8.text_input("Person 3")
        col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
        tk = col1.text_input("TK")
        pb = col2.text_input("PB")
        db = col3.text_input("DB")
        flg = col4.text_input("FLG")
        shk = col5.text_input("SHK")
        p1_name = col6.text_input("Coffees 1")
        p2_name = col7.text_input("Coffees 2")
        p3_name = col8.text_input("Coffees 3")
        
        st.write("-" * 34)
        col1,col2,col3 = st.columns([1,1,6])
        col1.button("Start break")
        col2.button("End break")
        
    if profile_nav == "Delete coffee break":                                        # Delete break page
        st.subheader("Delete a coffee break")
        st.markdown("Please enter the extended ID of the break you want to delete.")
        
        temp=[]
        for i in range(len(last_breaks)):
            temp.append(int(last_breaks[i][0]))
        max_id = max(temp)
        
        col1,col2,col3 = st.columns([1,0.5,3])
        col1.text_input("Extended ID of break", placeholder=str(max_id))
        col1.button("Delete break")
        columns=['Extended ID','Date','Drinkers','Coffees']
        df=pd.DataFrame(last_breaks,columns=columns)
        col3.markdown("Last 10 breaks")
        col3.dataframe(df, width=600, height=500)
        
        
    
    
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

if logged_in == False or (logged_in == True and profile_nav == "Show diagrams"):
    if logged_in == True:
        st.write("You now have access to the coffee list.")
    col1,col2,col3,col4 = st.columns([1,1,1,1])
    col1.subheader(str(simple_data[0])+" drinkers")
    col1.subheader(str(simple_data[1])+" active drinkers")
    col2.subheader(str(simple_data[2])+" months of drinking")
    col3.subheader(str(simple_data[4])+" coffee breaks")
    col3.subheader(str(simple_data[3])+" cups of coffee")
    col4.subheader(str(simple_data[5])+" data sets")
    col4.subheader(str(simple_data[6])+" diagrams")

if login and logged_in == False:
    st.write("-" * 34)
    st.warning("Incorrect username/password")
    
with st.sidebar:
    st.title("Available diagrams:")
    coffees_monthly = st.checkbox("Monthly coffees")
    c_b_weekly = st.checkbox ("Weekly breaks and coffees")
    coffees_total = st.checkbox("Total coffees / Monthly ratios")
    #ratio_monthly = st.checkbox("Monthly ratios")
    correlation = st.checkbox("Correlation")
    break_percentage = st.checkbox("Percentages of breaks")
    coffees_cumulated = st.checkbox("Cumulated coffees")





if logged_in == True and profile_nav == "Show diagrams":
    #-------------------------------------------------------------------------------------------------------------- monthly coffees, per person + total (line + bar chart)
    st.write("-" * 34)
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
        fig2 = px.bar(df, y="months", x="total", title="Total number of coffees per month", labels={"months":"Number of coffees", "total":""}, text_auto=True)
        fig2.update_layout(title_font_size=24)
        fig2.update_traces(hovertemplate='<br>%{x}<br>Number of coffees: %{y}<extra></extra>')
        st.plotly_chart(fig2, use_container_width=True) 

        #fig2_1 = echarts.init(temp1)
        #option = {xAxis: {type: 'category', data: ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun']},yAxis: {type: 'value'},series: [{data: [150, 230, 224, 218, 135, 147, 260],type: 'line'}]}


    #-------------------------------------------------------------------------------------------------------------- weekly coffees and breaks (line chart)
    if c_b_weekly:
        st.subheader("Weekly breaks and coffees")
        columns=['Breaks','Coffees']
        df = pd.DataFrame(coffees_breaks_weekly, columns=columns, index=weeks)
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
    #if ratio_monthly:                                                          #with inverted months (top: Nov '20, bottom: now)
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
        fig4 = px.bar(df_stack, x=names, y = months_inv, barmode = 'relative', labels={"y":"", "value":"Percentage", "variable":"drinker"})#, text='value', text_auto=True)
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
       fig6.update_traces(hovertemplate='<br>%{x} with %{y}<br>Percentage: %{size} %<extra></extra>')
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

        fig7.update_traces(hovertemplate='<br>%{x}<br>Percentage: %{y} %<extra></extra>')
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
