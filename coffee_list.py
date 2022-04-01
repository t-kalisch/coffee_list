import streamlit as st
st.set_page_config(page_title="Coffee list",page_icon="chart_with_upwards_trend",layout="wide")
from collections import namedtuple
import math
import pandas as pd
import numpy as npy
import datetime
from datetime import date
import plotly
import plotly.express as px
import mysql.connector as mysql
import extra_streamlit_components as stx
import plotly.graph_objects as go
from data_collection import *
#from calculations import *

@st.cache(allow_output_mutation=True, suppress_st_warning = True)
def get_manager():
    return stx.CookieManager()

cookie_manager = get_manager()
cookie_manager.get_all()

user_data=get_user_data()
simple_data=get_simple_data()
all_func=get_functionals()


if 'logged_in' not in st.session_state:
    st.session_state.logged_in=cookie_manager.get(cookie="logged_in")
if 'user_name' not in st.session_state:
    st.session_state.user_name=cookie_manager.get(cookie="user")
if 'admin' not in st.session_state:
    st.session_state.admin=cookie_manager.get(cookie="status")
if 'attempt' not in st.session_state:
    st.session_state.attempt="false"
    
    
if cookie_manager.get(cookie="logged_in") == "true":
    st.session_state.logged_in="true"
    st.session_state.user_name = cookie_manager.get(cookie="user")
    st.session_state.admin=cookie_manager.get(cookie="status")

logged_in=st.session_state.logged_in
logged_in_user=st.session_state.user_name
admin_status=st.session_state.admin


#@st.cache(suppress_st_warning=True)
def check_login(user, user_pw):                         #login check
    if user == "guest":
        g_pw = get_guest_pw()
        if user_pw == g_pw:
            login_check = True
            admin_status = 2
    else:
        login_check=False
        user_data=get_user_data()
        for i in range(len(user_data)):
            if user == user_data[i][0] and user_pw == user_data[i][1]:
                login_check = True
                admin_status=user_data[i][2]
    if login_check == True:
        st.session_state.logged_in = "true"
        st.session_state.user_name = user
        st.session_state.admin = str(admin_status)
        st.session_state.attempt = "false"
        if remember:
            cookie_manager.set("logged_in", True, expires_at=datetime.datetime(year=2030, month=1, day=1), key="logged_in_true")
            cookie_manager.set("user", user, expires_at=datetime.datetime(year=2030, month=1, day=1), key="logged_in_user")
            cookie_manager.set("status", admin_status, expires_at=datetime.datetime(year=2030, month=1, day=1), key="admin_status")
        else:
            cookie_manager.set("logged_in", False, expires_at=datetime.datetime(year=2030, month=1, day=1), key="logout")
            cookie_manager.set("status", None, expires_at=datetime.datetime(year=2030, month=1, day=1), key="del_admin_status")
            cookie_manager.set("user", None, expires_at=datetime.datetime(year=2030, month=1, day=1), key="logged_in_user")            
    else:
        st.session_state.attempt="true"
        st.session_state.logged_in = "false"
        st.session_state.user_name = ""
        st.session_state.admin = "0"
        #cookie_manager.set("logged_in", False, expires_at=datetime.datetime(year=2030, month=1, day=1), key="logged_in_false")
        #cookie_manager.delete("user")
        logged_in = "false"


#@st.cache(suppress_st_warning=True)       
def logout_check():
    cookie_manager.set("logged_in", "false", expires_at=datetime.datetime(year=2030, month=1, day=1), key="logout")
    cookie_manager.set("status", None, expires_at=datetime.datetime(year=2030, month=1, day=1), key="del_admin_status")
    cookie_manager.set("user", None, expires_at=datetime.datetime(year=2030, month=1, day=1), key="logged_in_user")
    st.session_state.attempt="false"
    st.session_state.logged_in = "false"
    st.session_state.user_name = None
    st.session_state.admin = "0"
    logged_in = "false"
        
        
with st.sidebar:
    
    col1,col2 = st.columns([1,1.65])
    user = col1.text_input(label="", placeholder="Username", key="user")
    user_pw = col2.text_input(label="", type="password", placeholder="Password", key="user_pw")
    col1,col2=st.columns([1,1.65])
    if logged_in == "true":
        logout = col1.button("Logout", help="Log out here", on_click=logout_check)
    else:
        login = col1.button("Login", help="Log in here", on_click=check_login, args=(user, user_pw))
    remember = st.checkbox("Remember me", help="Keep me logged in (uses cookies)")      
      
if logged_in == "true":
    st.title("Logged in as {}".format(logged_in_user))
    if admin_status == "1":
        col2.write("  Status: Administrator")
    elif admin_status == "2":
        col2.write("  Status: guest")
    else:
        col2.write("  Member status: User") 
        
    #if logout:
    #    logout_check()
else:
    st.title("Welcome to the future of coffee drinking **:coffee:**")
    st.write("In order to get access to the visualised data you need to be logged in with your username and password.")
    
    #if login:
    #    check_login(user, user_pw)         


    

if logged_in == "true":
    if admin_status != "1" and admin_status != "2":
        #profile_nav = st.sidebar.selectbox("Profile Options", ("Show diagrams","Enter holidays","Change username","Change password"), 0)
        profile_nav = st.sidebar.selectbox("Profile Options", ("Show diagrams","Enter holidays","Change password"), 0)
    elif admin_status == "1":
        profile_nav = st.sidebar.selectbox("Profile Options", ("Show diagrams","Submit coffee or break","Delete coffee or break","Enter holidays","Change profile data"), 0)
    elif admin_status == "2":
        options = ["Show diagrams"]
        profile_nav = st.sidebar.selectbox("Profile Options", options)
    
    if profile_nav == "Enter holidays":                                             # Enter holidays page
        st.subheader("**:calendar:** Enter holidays")
        if admin_status == "1":
            col1, col2, col3, col4 = st.columns([0.5,1,1,1])
            month = col1.text_input("Month", placeholder=datetime.date.today().month)
            year = col2.text_input("Year", placeholder=datetime.date.today().year)
            person_hol = col3.text_input("Person", placeholder = "User")
            holidays = col4.text_input("Number of holidays", placeholder=0)
            if person_hol == "":
                sub_hol = st.button("Submit holidays", help="Submit holidays for yourself", on_click=submit_holidays, args=(st.session_state.user_name, month, year, holidays))
                #if sub_hol:
                #    submit_holidays(st.session_state.user_name, month, year, holidays)
            else:
                sub_hol = st.button("Submit holidays", help="Submit holidays for "+person_hol, on_click=submit_holidays, args=(person_hol,month,year,holidays))
                #if sub_hol:
                #    submit_holidays(person_hol, month, year, holidays)

            st.write("-" * 34)   
            st.subheader("All holidays")
            all_holidays = get_all_holidays(datetime.datetime.now())
            #print(all_holidays)
            names=get_members()
            columns=["Month","Total work days"]
            for i in range(len(names)):
                columns.append(names[i])
            df=pd.DataFrame(all_holidays,columns=columns)
            st.dataframe(df, width=1000, height=1000)
  
        else:
            col1, col2, col3 = st.columns([0.5,1,2])
            month = col1.text_input("Month", placeholder=datetime.date.today().month)
            year = col2.text_input("Year", placeholder=datetime.date.today().year)
            holidays = col3.text_input("Number of holidays", placeholder=0)
            sub_hol = col1.button("Submit", help="Submit holidays")
            if sub_hol:
                submit_holidays(st.session_state.user_name, month, year, holidays)
            st.write("-" * 34)   
            st.subheader("All holidays")
            all_holidays = get_all_holidays(datetime.datetime.now())
            #print(all_holidays)
            holidays_person=[]
            names=get_members()
            columns=["Month","Total work days"]
            for i in range(len(names)):
                if names[i] == st.session_state.user_name:
                    columns.append(names[i])
                    for j in range(len(all_holidays)):
                        temp=[]
                        temp.append(all_holidays[j][0])
                        temp.append(all_holidays[j][i+2])
                        temp.append(all_holidays[j][1])
                        holidays_person.append(temp)
            print(holidays_person)
            df=pd.DataFrame(holidays_person,columns=columns)
            st.dataframe(df, width=1000, height=1000)
        
    if profile_nav == "Change username":                                            # Change username page
        st.subheader("**:adult:** Change username")
        if admin_status != "1":
            st.markdown("Please enter your current username, password and new username.")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            curr_user = col2.text_input("Username", placeholder = "Username")
            user_pw = col2.text_input("Password", type="password", placeholder = "Password")
            col2.write("-" * 34)
            new_user = col2.text_input("Choose a new username", placeholder = "Username")
            user_change = col2.button("Save new username")
        if admin_status == "1":
            st.markdown("Change username for a member.")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            curr_user = col2.text_input("Old username", placeholder = " Old username")
            user_pw = col2.text_input("New username", placeholder = "New username")
            col2.write("-" * 34)
            new_user = col2.text_input("Please enter your password", type = 'password', placeholder = "Password")
            user_change = col2.button("Confirm")
        
    if profile_nav == "Change password":                                            # Change password page
        st.subheader("**:closed_lock_with_key:** Change password")
        if admin_status != "1":
            st.markdown("You can change your password here.")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            curr_pw = col2.text_input("Current password", type="password", placeholder = "Old password")
            col2.write("-" * 34)
            col1,col2,col3 = st.columns([0.5,1,0.7])
            pw_new = col2.text_input("Choose a new password", type="password", placeholder = "New password")
            conf_pw = col2.text_input("Repeat the new password", type="password", placeholder = "Repeat password")
            pw_change = col2.button("Save new password")
            if pw_new != conf_pw:
                st.error("The entered new passwords differ from each other")
            if pw_change:
                if pw_new == "" or conf_pw == "":
                    st.error("You cannot enter an empty password")
                else:
                    done=False
                    for i in range(len(user_data)):
                        if st.session_state.user_name == user_data[i][0] and curr_pw == user_data[i][1]:
                            done = change_profile_data(st.session_state.user_name, "", pw_new, st.session_state.admin)
                    if done == False:
                        st.warning("Incorrect password")
        if admin_status == "1":
            st.markdown("Change password for another person")
            col1,col2,col3 = st.columns([0.5,1,0.7])
            col2.text_input("Username", placeholder = "User")
            col2.text_input("New password", type = 'password', placeholder = "Password")
            col2.write("-" * 34)
            col2.text_input("Please enter your password to confirm", type = 'password', placeholder = "Password")
            col2.button("Confirm")        
 
    if profile_nav == "Change profile data":                                          # Change profile data page
        st.subheader("**:closed_lock_with_key:** Change the profile of a member")
        st.markdown("You can enter a new username and password for a member, or change their member status.")
        st.markdown("Guest password: "+get_guest_pw())
        col1,col2,col3 = st.columns([0.5,1,0.7])
        change_user = col1.text_input("User", placeholder = "Username")
        username_new = col2.text_input("New username", placeholder = "Username")
        pw_new = col2.text_input("New password", type = "password", placeholder = "Password")
        status=-1
        if change_user != "":
            for i in range(len(user_data)):
                if user_data[i][0] == change_user:
                    if user_data[i][2] == 1:
                        status=1
                        status_str="Admin"
                    else:
                        status=0
                        status_str="User"
        col1,col2 = st.columns([0.5,1.7])
        if status == -1:
            col1.selectbox ("Change member status", (""), 0)
        else: 
            user_status = col1.selectbox ("Change member status", ("User", "Admin"), status)
        st.write("-" * 34)
        col1,col2 = st.columns([0.5,0.5])
        admin_pw = col1.text_input("Please enter your password to confirm", type = 'password', placeholder = "Password")
        confirm = col1.button("Confirm")
        if confirm:
            if status == -1:
                st.error("Wrong username entered")
            else:
                done=False
                for i in range(len(user_data)):
                    if st.session_state.user_name == user_data[i][0] and admin_pw == user_data[i][1]:
                        done = change_profile_data(change_user, username_new, pw_new, user_status)
                if done == False:
                    st.warning("Incorrect password")

    if profile_nav == "Submit coffee or break":                                        # Submit break page
        st.subheader("**:coffee:** Submit a coffee break")
        st.markdown("Please enter the names and number of coffees for the break.")
        col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
        p1_name = col6.text_input("Person 1")
        p2_name = col7.text_input("Person 2")
        p3_name = col8.text_input("Person 3")
        col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
        tk = col1.text_input("TK")
        pb = col2.text_input("PB")
        db = col3.text_input("DB")
        flg = col4.text_input("FLG")
        shk = col5.text_input("SHK")
        p1_coffees = col6.text_input("Coffees 1")
        p2_coffees = col7.text_input("Coffees 2")
        p3_coffees = col8.text_input("Coffees 3")
        col1,col2,col3,col4,col5,col6,col7,col8 = st.columns([1,1,1,1,1,1,1,1])
        date_day = col1.text_input("Day", placeholder = datetime.date.today().day)
        date_month = col2.text_input("Month", placeholder = datetime.date.today().month)
        date_year = col3.text_input("Year", placeholder = datetime.date.today().year)
        persons=['TK','PB','DB','FLG','SHK',p1_name,p2_name,p3_name]
        coffees=[tk,pb,db,flg,shk,p1_coffees,p2_coffees,p3_coffees]
        date_br=[date_day,date_month,date_year]
        col1,col2 = st.columns([2,6])
        col1.button("Submit break", on_click=submit_break, args=(persons,coffees,date_br))
        st.write("-" * 34)
        st.write("Enter an extended ID and Name to add a coffee to a break.")
        last_breaks=get_last_breaks(10)
        col1, col2, col3 = st.columns([1,1,3])
        id_ext = col1.text_input("Extended ID", placeholder=last_breaks[len(last_breaks)-1][0])
        coffee_name = col2.text_input("Username", placeholder=logged_in_user)
        col1.button("Add coffee", on_click=add_coffee_to_break, args=(id_ext, coffee_name, logged_in_user))
        df=pd.DataFrame(last_breaks,columns=['Extended ID','Date','Drinkers','Coffees'])
        col3.markdown("Last 10 breaks")
        col3.dataframe(df, width=600, height=500)
        
    if profile_nav == "Delete coffee or break":                                        # Delete break page
        st.subheader("**:x:** Delete a coffee break")
        st.markdown("Please enter the extended ID of the break you want to delete.")
        last_breaks=get_last_breaks(10)
        col1,col2,col3 = st.columns([1,0.5,3])
        del_id = col1.text_input("Extended ID of break", placeholder=last_breaks[len(last_breaks)-1][0])
        df=pd.DataFrame(last_breaks,columns=['Extended ID','Date','Drinkers','Coffees'])
        col3.markdown("Last 10 breaks")
        col3.dataframe(df, width=600, height=500)
        delete = col1.button("Delete break", on_click=clear_one_break, args=(del_id,""))
        col1.write("-" * 34)
        del_person = col1.text_input("Delete for person", placeholder="Username")
        col1.button("Delete coffee from break", on_click=delete_one_coffee, args=(del_id,del_person))
        
        
        

                
with st.sidebar:
    act_func = get_active_func()
    if logged_in == "true":
        if admin_status == "1":
            for i in range(len(all_func)):
                if all_func[i] == act_func:
                    curr=i
            func_selected = st.selectbox("Functional selector", all_func, curr)
        else:
            act_func_l=[]
            act_func_l.append(act_func)
            func_selected = st.selectbox("Active functional", act_func_l, 0)

    st.title("Available diagrams:")
    coffees_monthly = st.checkbox("Monthly coffees")
    coffees_total = st.checkbox("Total coffees / Monthly ratios")
    expectation_data = st.checkbox("Expectation values / Prize history")
    c_b_weekly = st.checkbox ("Weekly breaks and coffees")
    correlation = st.checkbox("Correlation")
    break_percentage = st.checkbox("Percentages of breaks")
    soc_sc = st.checkbox("Social score")
    coffees_pwd = st.checkbox("Coffees per work day")
    coffees_cumulated = st.checkbox("Cumulated coffees")
    
if admin_status == "1":
    update_simple = st.sidebar.button("Simple database update", help="Click here to update the last two months", on_click = manual_update_simple)
    update_full = st.sidebar.button("Full database update", help="Click here to perform a full update of the database", on_click = manual_update)

                
                
if logged_in == "true":
    if profile_nav == "Show diagrams":
        st.markdown("You now have access to the coffee list.")
        col1,col2,col3,col4 = st.columns([1,1,1,1])
        col1.subheader(str(simple_data[0][0])+" drinkers")
        col1.subheader(str(simple_data[1][0])+" active drinkers")
        col2.subheader(str(simple_data[2][0])+" months of drinking")
        col3.subheader(str(simple_data[3][0])+" coffee breaks")
        col3.subheader(str(simple_data[4][0])+" cups of coffee")
        col4.subheader(str(simple_data[5][0])+" data sets")
        col4.subheader(str(simple_data[6][0])+" diagrams")
else:
    col1,col2,col3,col4 = st.columns([1,1,1,1])
    col1.subheader(str(simple_data[0][0])+" drinkers")
    col1.subheader(str(simple_data[1][0])+" active drinkers")
    col2.subheader(str(simple_data[2][0])+" months of drinking")
    col3.subheader(str(simple_data[3][0])+" coffee breaks")
    col3.subheader(str(simple_data[4][0])+" cups of coffee")
    col4.subheader(str(simple_data[5][0])+" data sets")
    col4.subheader(str(simple_data[6][0])+" diagrams")

if st.session_state.attempt == "true":
    st.write("-" * 34)
    st.warning("Incorrect username/password")
   
    


if logged_in == "true" and profile_nav == "Show diagrams":
    
    names = get_members()
    month_info=get_months(datetime.date(2021,3,8))
    months_dly=month_info[0]
    month_id_dly=month_info[1]
    month_info=get_months(datetime.date(2020,11,1))
    months_all=month_info[0]
    month_id_all=month_info[1]
    
    
    
    
    st.write("-" * 34)
    #-------------------------------------------------------------------------------------------------------------- monthly coffees, per person + total (line + bar chart)
    if coffees_monthly:
        st.subheader("Coffees per month") 
        
        monthly_coffees_all = get_monthly_coffees(names, month_id_all)
        df = pd.DataFrame(monthly_coffees_all[0], columns=names, index=months_all)    #coffees per month per person

        fig1 = px.line(df, title="Number of coffees per month per person", labels={"variable":"", "index":"", "value":"Number of coffees"})
        fig1.update_traces(hovertemplate='%{y}')
        fig1.update_layout(title_font_size=24, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        st.plotly_chart(fig1, use_container_width=True)

        temp1=[]
        for i in range(len(months_all)):
             temp=[]
             temp.append(months_all[i])
             temp.append(monthly_coffees_all[1][i])
             temp1.append(temp)
        
        columns=['months','total']
        df = pd.DataFrame(temp1, columns=columns)              #total coffees per month)
        fig2 = px.bar(df, y="total", x="months", title="Total number of coffees per month", labels={"months":"", "total":"Number of coffees"}, text_auto=True)
        fig2.update_layout(title_font_size=24)
        fig2.update_traces(hovertemplate='%{x}<br>%{y} coffees')
        st.plotly_chart(fig2, use_container_width=True) 

 
        
        
        col1, col2 = st.columns([1,1])
    #-------------------------------------------------------------------------------------------------------------- total coffees (pie chart)
    if coffees_total:
        col1, col2 = st.columns([1,1])
        col1.subheader("Total coffees")

        total_coffees = get_total_coffees(names)
        
        temp=[]
        for i in range(len(total_coffees)):
            temp1=[]
            temp1.append(names)
            temp1.append(total_coffees[i])
            temp.append(temp1)
        df = pd.DataFrame(temp, columns={"names","total"}, index=names)              #total coffees pie chart

        #fig3 = px.pie(df, names = names, values = total_coffees)
        fig3 = go.Figure(go.Pie(labels = names, values = total_coffees, sort=False, hole=.4))
        fig3.update_layout(title_font_size=24)
        col1.plotly_chart(fig3, use_container_width=True)

        
    #-------------------------------------------------------------------------------------------------------------- monthly ratios (stacked bar chart)
        col2.subheader("Monthly ratios")

        monthly_ratios=get_monthly_ratio(names, month_id_all)

        months_inv=[]
        monthly_ratios_inv=[]
        for i in range(len(months_all)):
            months_inv.append(months_all[len(months_all)-i-1])
            monthly_ratios_inv.append(monthly_ratios[len(monthly_ratios)-i-1])

        df_stack=pd.DataFrame(monthly_ratios_inv, columns = names, index = months_inv)
        fig4 = px.bar(df_stack, x=names, y = months_inv, barmode = 'relative', labels={"y":"", "value":"Percentage", "variable":"drinker"})#, text='value', text_auto=True)
        fig4.update_layout(title_font_size=24, showlegend=False)
        fig4.update_traces(hovertemplate='%{y}<br>%{x} %')
        col2.plotly_chart(fig4, use_container_width=True)
        
        
        
    #-------------------------------------------------------------------------------------------------------------- expectation values and MAD (scatter chart and bar chart)
    if expectation_data:
        act_func=get_active_func()
        st.subheader("Prediction Data (active functional: "+act_func+")")
        col7,col8 = st.columns([1,1])
        
        exp_values = get_expectation_values(names, month_id_all, func_selected)
        stdev = get_stdev(names, month_id_all)
        
        max_values=[]
        for i in range(len(names)):
            if exp_values[i] < 0:
                exp_values[i] = 0
            max_values.append(exp_values[i]+stdev[i])
        
        mad_total = get_mad(names, month_id_all)
        
        df = pd.DataFrame(exp_values, columns={'Number of coffees'}, index=names)                #expectation values with standard deviation
        df["e"] = stdev

        info = act_func
        fig8 = px.scatter(df, x=names, y='Number of coffees', error_y='e', title="Expect. val.  ± σ for "+months_all[len(months_all)-1], labels={"x":"", "y":"Number of coffees", "variable":"drinkers"}, text="Number of coffees")
        fig8.update_layout(title_font_size=24, showlegend=False)
        fig8.update_traces(marker = dict(symbol = 'line-ew-open'), hovertemplate='%{x}: %{y}', textposition='middle right')
        fig8.update_yaxes(range=[0,max(max_values)+2])
        col7.plotly_chart(fig8, use_container_width=True)
        
        columns=['Functional','MAD']
        df = pd.DataFrame(mad_total, columns=columns)
        
        fig8 = px.bar(df, x='Functional', y='MAD', title="Mean absolute deviations", labels={"x":"Functional", "count":"MAD"}, text='MAD', text_auto=True).update_xaxes(categoryorder="total ascending")
        fig8.update_layout(title_font_size=24, showlegend=False)
        fig8.update_traces(hovertemplate='%{x}<br>MAD = %{y}')
        col8.plotly_chart(fig8, use_container_width=True)
        
        
        
        #-------------------------------------------------------------------------------------------------------------- coffee prize history (scatter + bar chart)
        st.subheader("Prize history")
        col1, col2 = st.columns([2,1])
        prizes = get_prizes(names, month_id_dly, act_func)
        
        tickval_num=[]
        total_prizes=[]
        for i in range(len(names)):
            tickval_num.append(i)
            total=0
            for j in range(len(prizes)):
                if prizes[j][1] == i:
                    total += 1
            total_prizes.append(total)

        columns=['Month','Persons','Coffee prizes','sizes']
        df = pd.DataFrame(prizes, columns=columns)

        fig2 = px.scatter(df, x='Month', y='Persons', title="Coffee prize history ("+act_func+")", labels={"variable":"", "index":"", "value":""}, size='sizes', color='Coffee prizes', color_discrete_sequence=['gold','black','red'])      #plotting social score
        fig2.update_layout(title_font_size=24, yaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names), hovermode="x unified", xaxis=dict(tickmode = 'array', tickvals = month_id_dly, ticktext = months_dly), legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        fig2.update_traces(hovertemplate='%{y}')
        col1.plotly_chart(fig2, use_container_width=True)


        df = pd.DataFrame(total_prizes, columns={'Number of prizes'}, index=names)                #total number of prizes

        fig8 = px.bar(df, x='Number of prizes', y=names, title="Total number of prizes", labels={"y":"", "count":"Social score", "variable":"drinkers"}, text='Number of prizes', text_auto=True, orientation='h').update_yaxes(categoryorder="total ascending")
        fig8.update_layout(title_font_size=24, showlegend=False)
        fig8.update_traces(hovertemplate='%{y}: %{x}')
        fig8.update_xaxes(showticklabels=False)
        col2.plotly_chart(fig8, use_container_width=True)
        
        
        
        
    #-------------------------------------------------------------------------------------------------------------- weekly coffees and breaks (line chart)
    if c_b_weekly:
        st.subheader("Weekly breaks and coffees")
        columns=['Breaks','Coffees']
        weekly_data = get_weekly_coffees_breaks(names)

        weeks=[]
        weekly_br_c=[]
    
        for i in range(len(weekly_data)):
            temp=[]
            weeks.append(weekly_data[i][0])
            temp.append(weekly_data[i][1])
            temp.append(weekly_data[i][2])
            weekly_br_c.append(temp)

        df = pd.DataFrame(weekly_br_c, columns=columns, index=weeks)              #weekly coffees/breaks

        fig3 = px.line(df, title="Weekly coffee breaks and coffees", labels={"variable":"", "index":"", "value":""})
        fig3.update_layout(title_font_size=24, hovermode="x unified", legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        fig3.update_traces(hovertemplate='%{y}')
        st.plotly_chart(fig3, use_container_width=True)


    #-------------------------------------------------------------------------------------------------------------- absolute and relative correlations (bubble charts)
    if correlation:
        st.subheader("Correlation diagrams")
        col3, col4 = st.columns([1,1])                        #setting up two columns for narrower charts        
        corr_tot=get_correlation(names)
        corr_abs_raw=corr_tot[0]
        corr_rel_raw=corr_tot[1]
        print(corr_tot)
        temp1=[]
        temp2_abs=[]
        temp2_rel=[]
        tickval_num=[]
        names_inv=[]
        for i in range(len(names)):
            tickval_num.append(i+1)
            names_inv.append(names[len(names)-i-1])
            for j in range(len(names)):
               temp_abs=[]
               temp_rel=[]
               temp_abs.append(i+1)
               temp_rel.append(i+1)
               temp_abs.append(j+1)
               temp_rel.append(j+1)
               #temp_abs.append(corr_abs_raw[len(names)-j-1][i])      #calculates absolute correlation
               #temp_rel.append(corr_rel_raw[len(names)-j-1][i])      #calculates relative correlation
               temp_abs.append(corr_abs_raw[i][len(names)-j-1])      #calculates absolute correlation
               temp_rel.append(corr_rel_raw[i][len(names)-j-1])      #calculates relative correlation
               temp2_abs.append(temp_abs)
               temp2_rel.append(temp_rel)
        columns_corr_abs=['x-values','y-values','Coffees']
        columns_corr_rel=['x-values','y-values','Percent']
        
        df = pd.DataFrame(temp2_abs, columns=columns_corr_abs)
        fig5 = px.scatter(df, x='x-values', y='y-values', size='Coffees', custom_data=['Coffees'], labels={"x-values":"", "y-values":""}, title="Absolute correlation", color='Coffees')
        fig5.update_layout(title_font_size=24, showlegend=False, xaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names), yaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names_inv))
        #fig5.update_traces(hovertemplate="%{y} with %{x}:<br>%{customdata[0]} coffees")
        fig5.update_traces(hovertemplate="%{y} drank %{customdata[0]} coffees with %{x}")
        fig5.update_xaxes(side="top")
        col3.plotly_chart(fig5, use_container_width=True)#              absolute correlation
        #                                                  --------------------------------------------------
        df = pd.DataFrame(temp2_rel, columns=columns_corr_rel)
        fig6 = px.scatter(df, x='x-values', y='y-values', size='Percent', custom_data=['Percent'], labels={"x-values":"", "y-values":""}, title="Relative correlation", color='Percent')#, text='size')
        fig6.update_layout(title_font_size=24, showlegend=False, xaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names), yaxis=dict(tickmode = 'array', tickvals = tickval_num, ticktext = names_inv))
        #fig6.update_traces(hovertemplate="%{x} with %{y}:<br>%{customdata[0]} %")
        fig6.update_traces(hovertemplate="%{y} drank %{customdata[0]} % of<br>their coffees with %{x}")
        fig6.update_xaxes(side="top")
        col4.plotly_chart(fig6, use_container_width=True)

    #-------------------------------------------------------------------------------------------------------------- percentages of breaks (line + bar charts)
    if break_percentage:
        st.subheader("Percentages of breaks")
        col5,col6 = st.columns([2,1])

        percentages=get_perc_breaks(names, month_id_dly)
        percentage_total=percentages[0]
        percentage=[]
        for i in range(len(percentages)-1):
            percentage.append(percentages[i+1])
        
        df = pd.DataFrame(percentage, columns=names, index=months_dly)
        fig7 = px.line(df, title="Monthly percentages of breaks", labels={"variable":"", "index":"", "value":"Percentage"})
        fig7.update_layout(title_font_size=24, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        fig7.update_traces(hovertemplate='%{x}<br>%{y} %')
        col5.plotly_chart(fig7, use_container_width=True)

        df = pd.DataFrame(percentage_total, columns={'percentage'}, index=names)

        fig8 = px.bar(df, x='percentage', y=names, title="Total percentages of breaks", labels={"y":"", "count":"Percentage", "variable":"drinkers"}, text='percentage', text_auto=True, orientation='h').update_yaxes(categoryorder="total ascending")
        fig8.update_layout(title_font_size=24, showlegend=False)
        fig8.update_traces(hovertemplate='%{y}: %{x} %')
        col6.plotly_chart(fig8, use_container_width=True)
    
    #-------------------------------------------------------------------------------------------------------------- social score (line chart + bar chart)
    if soc_sc:
        st.subheader("Social Score")
        col7,col8 = st.columns([2,1])
    
        socialscore_total = get_social_score(names, month_id_dly)
        total = socialscore_total[0]
        socialscore=[]
        #for i in range(len(socialscore_total[1])):
        #    socialscore.append(socialscore_total[1][i])
        
        df = pd.DataFrame(socialscore_total[1], columns=names, index=months_dly)                 #data frame for social score

        fig2 = px.line(df, title="Monthly social scores", labels={"variable":"", "index":"", "value":"Social score / a.u."})      #plotting social score
        fig2.update_layout(title_font_size=24, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        fig2.update_traces(hovertemplate='%{x}<br>%{y}')
        fig2.update_yaxes(showticklabels=False)
        col7.plotly_chart(fig2, use_container_width=True)

        df = pd.DataFrame(total, columns={'Social score'}, index=names)                #total social score

        fig8 = px.bar(df, x='Social score', y=names, title="Total social score", labels={"y":"", "count":"Social score", "variable":"drinkers"}, text='Social score', text_auto=True, orientation='h').update_yaxes(categoryorder="total ascending")
        fig8.update_layout(title_font_size=24, showlegend=False)
        fig8.update_traces(hovertemplate='%{y}: %{x} %')
        fig8.update_xaxes(showticklabels=False,range=[0,100])
        col8.plotly_chart(fig8, use_container_width=True)  

    
    
    #-------------------------------------------------------------------------------------------------------------- coffees per work day (line chart + bar chart)
    if coffees_pwd:
        st.subheader("Coffees per work day")
        col7,col8 = st.columns([2,1])
        
        total_cpwd = get_coffees_per_work_day(names, month_id_all)
        total = total_cpwd[0]
        coffees_per_work_day = total_cpwd[1]
        
        df = pd.DataFrame(coffees_per_work_day, columns = names, index = months_all)
    
        fig9 = px.line(df, title="Monthly coffees per work day", labels={"variable":"", "index":"", "value":"Number of coffees"})      #plotting monthly coffees
        fig9.update_layout(title_font_size=24, legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        fig9.update_traces(hovertemplate='%{x}<br>%{y}')
        col7.plotly_chart(fig9, use_container_width=True)


        df = pd.DataFrame(total, columns={'Number of coffees'}, index=names)                #total percentages

        fig11 = px.bar(df, x='Number of coffees', y=names, title="Total coffees per work day", labels={"y":"", "count":"Number of coffees", "variable":"drinkers"}, text='Number of coffees', text_auto=True, orientation='h').update_yaxes(categoryorder="total ascending")
        fig11.update_layout(title_font_size=24, showlegend=False)
        fig11.update_traces(hovertemplate='%{y}: %{x}')
        col8.plotly_chart(fig11, use_container_width=True)
    
    
    #-------------------------------------------------------------------------------------------------------------- cumulated coffees monthly (line chart)
    if coffees_cumulated:
        st.subheader("Cumulated coffees")
        
        cumulated_coffees = get_cumulated_coffees(names, month_id_all)
        df = pd.DataFrame(cumulated_coffees, columns=names, index=months_all)
        
        fig10 = px.line(df, title="Number of coffees per month per person", labels={"variable":"", "index":"", "value":"Number of coffees"})
        fig10.update_layout(legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="center", x=0.5))
        fig10.update_traces(hovertemplate='%{x}<br> %{y}')
        st.plotly_chart(fig10, use_container_width=True)
      

#col1, col2 = st.columns([1,1])
#col1.write("Session states:")
#col1.write(logged_in)
#col1.write(logged_in_user)
#col1.write(admin_status)
#col2.write("Cookies:")
#col2.write(cookie_manager.get(cookie="logged_in"))
#col2.write(cookie_manager.get(cookie="user"))
#col2.write(cookie_manager.get(cookie="status"))
    

#st.write("# Cookie Manager")
#
#@st.cache(allow_output_mutation=True)
#def get_manager():
#    return stx.CookieManager()
#
#cookie_manager = get_manager()
#
#st.subheader("All Cookies:")
#cookies = cookie_manager.get_all(key = "penis")
#st.write(cookies)
#
#c1, c2, c3 = st.columns(3)
#
#with c1:
#    st.subheader("Get Cookie:")
#    cookie = st.text_input("Cookie", key="0")
#    clicked = st.button("Get")
#    if clicked:
#        value = cookie_manager.get(cookie=cookie)
#        st.write(value)
#    with c2:
#        st.subheader("Set Cookie:")
#        cookie = st.text_input("Cookie", key="1")
#        val = st.text_input("Value")
#        if st.button("Add"):
#            cookie_manager.set(cookie, val, expires_at=datetime.datetime(year=2030, month=1, day=1))
#    with c3:
#        st.subheader("Delete Cookie:")
#        cookie = st.text_input("Cookie", key="2")
#        if st.button("Delete"):
#            cookie_manager.delete(cookie)
    
    
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
