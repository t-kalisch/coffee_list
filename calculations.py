import streamlit as st
import math
import mysql.connector as mysql
import numpy
import datetime
from datetime import date
import pandas as pd
from plotly import *
import plotly.express as px

db = mysql.connect(user='PBTK', password='akstr!admin2',
		host='212.227.72.95',
		database='coffee_list')
cursor=db.cursor(buffered=True)



def get_user_data():
	cursor.execute("select name, password, admin from members")
	user_data=cursor.fetchall()
	return user_data


def get_simple_data():							# getting simple data from database
	cursor.execute("select value from simple_data")
	simple_data=cursor.fetchall()
	#simple_data=[]
	#for i in range(len(tmp[0])):
	#	temp=[]
	#	temp.append(tmp[0][i])
	#	temp.append(tmp[1][i])
	#	simple_data.append(temp)
	return simple_data
	

#@st.cache(suppress_st_warning=True)
def write_simple_data():
	cursor.execute("create table if not exists simple_data (id int auto_increment, parameter varchar(10), value int, primary key(id))")		#setting up table
	cursor.execute("select * from simple_data")
	if cursor.fetchall() == []:
		cursor.execute("insert into simple_data (parameter) values ('drinkers')")
		cursor.execute("insert into simple_data (parameter) values ('act_dr')")
		cursor.execute("insert into simple_data (parameter) values ('months')")
		cursor.execute("insert into simple_data (parameter) values ('breaks')")
		cursor.execute("insert into simple_data (parameter) values ('cups')")
		cursor.execute("insert into simple_data (parameter, value) values ('data_sets', 9000)")
		cursor.execute("insert into simple_data (parameter, value) values ('diagrams', 18)")
	
	names = get_members()
	month_id = get_months(datetime.date(2020,11,1))[1]
	coffees = get_monthly_coffees(names, month_id)								#calculating simple data from different tables
	cursor.execute("select count(*) from breaks")
	breaks = cursor.fetchall()
	cups = 0
	for i in range(len(month_id)):
		cups += coffees[1][i]
	act_dr = 0
	for i in range(len(names)):
		if coffees[0][len(month_id)-3][i] > 0 and coffees[0][len(month_id)-2][i] > 0:
			act_dr += 1

	data_sets = len(names)*8+12
	cursor.execute("update simple_data set value = "+str(len(names))+" where parameter = 'drinkers'")	#updating simple_data table
	cursor.execute("update simple_data set value = "+str(act_dr)+" where parameter = 'act_dr'")
	cursor.execute("update simple_data set value = "+str(len(month_id))+" where parameter = 'months'")
	cursor.execute("update simple_data set value = "+str(breaks[0][0])+" where parameter = 'breaks'")
	cursor.execute("update simple_data set value = "+str(cups)+" where parameter = 'cups'")
	cursor.execute("update simple_data set value = "+str(data_sets)+" where parameter = 'data_sets'")
	db.commit()



def get_monthly_coffees(names, month_id):
	cursor.execute("select * from monthly_coffees")
	tmp=cursor.fetchall()
	
	monthly_coffees_all=[]
	monthly_coffees=[]
	total_monthly_coffees=[]
	for i in range(len(month_id)):
		total=0
		temp=[]
		for j in range(len(names)):
			temp.append(tmp[j][i+2])
			total += tmp[j][i+2]
		monthly_coffees.append(temp)
		total_monthly_coffees.append(total)
		
	monthly_coffees_all.append(monthly_coffees)
	monthly_coffees_all.append(total_monthly_coffees)
	return monthly_coffees_all


#----------------------------------------- wrtiting monthly coffees into database --------------------------------------
def write_monthly_coffees(names, month_id, update):
    all_coffees=[]
    cursor.execute("create table if not exists monthly_coffees (id int auto_increment, name varchar(3), primary key(id))")

    for i in range(len(names)):                                              #writing total cofees per month into coffees
        cursor.execute("select count(name) from monthly_coffees where name = '"+names[i]+"'")
        tmp = cursor.fetchall()
        if tmp[0][0] == 0:
            cursor.execute("insert into monthly_coffees (name) values ('"+names[i]+"')")

        
        coffees=[]
        for j in range(len(month_id)):
            total=0

            cursor.execute("select n_coffees from mbr_"+names[i]+" where id_ext like '"+str(month_id[j])+"%'")
            tmp=cursor.fetchall()
            tmp=list(tmp)
        
            for k in range(len(tmp)):
                total=total+tmp[k][0]
            coffees.append(total)
            if i < 6:                                                       #input from old breaks
                if j < 5:
                    cursor.execute("select "+names[i].upper()+" from old_breaks where id_ext like'"+str(month_id[j])+"%'")
                    old_coffees=cursor.fetchall()
                    old_coffees=list(old_coffees)
                    coffees[j]=coffees[j]+old_coffees[0][0]
        all_coffees.append(coffees)

    if update == "full":
        for i in range(len(month_id)):
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='monthly_coffees' AND column_name='"+month_id[i]+"'") #check if name is already in table
            tmp = cursor.fetchall()

            if tmp[0][0] == 0:
                cursor.execute("alter table monthly_coffees add `"+month_id[i]+"` int")                     #creating month column if month is not in table
            for j in range(len(names)):
                cursor.execute("update monthly_coffees set `"+month_id[i]+"` = "+str(all_coffees[j][i])+" where name = '"+names[j]+"'")    #always updating last two months
    elif update == "simple":
        for i in range(2):
            cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='monthly_coffees' AND column_name='"+month_id[len(month_id)-2+1]+"'") #check if name is already in table
            tmp = cursor.fetchall()

            if tmp[0][0] == 0:
                cursor.execute("alter table monthly_coffees add `"+month_id[len(month_id)-2+1]+"` int")                     #creating month column if month is not in table
            for j in range(len(names)):
                cursor.execute("update monthly_coffees set `"+month_id[i]+"` = "+str(all_coffees[j][i])+" where name = '"+names[j]+"'")    #always updating last two months

    db.commit()
    return all_coffees


#-------------------------- getting total coffees from database
def get_total_coffees(names):

    coffees=[]
    for i in range(len(names)):
        cursor.execute("select coffees from total_coffees where name like '"+names[i]+"'")
        coffees.append(cursor.fetchall()[0][0])

    return coffees


#-------------------------- writing total coffees into database
def write_total_coffees(names):
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)


    cursor.execute("create table if not exists total_coffees (id int auto_increment, name varchar(3), coffees int, primary key(id))")
    for i in range(len(names)):
        cursor.execute("select count(*) from total_coffees where name like '"+names[i]+"'")     #does the name alreaedy exists?
        tmp = cursor.fetchall()

        if tmp[0][0] == 0:
            cursor.execute("insert into total_coffees (name) values ('"+names[i]+"')")           #creating name if it doesn't exist

        total=0
        cursor.execute("select n_coffees from mbr_"+names[i])       #getting new data if update status not up to date
        tmp=cursor.fetchall()
        total=0
        for j in range(len(tmp)):
            total=total+tmp[j][0]
        if i < 6:
            cursor.execute("select "+names[i]+" from old_breaks")       #inserting old coffees from before March 8, 2021
            tmp = cursor.fetchall()

            for j in range(len(tmp)):
                total=total+tmp[j][0]

        cursor.execute("update total_coffees set coffees = "+str(total)+" where name = '"+names[i]+"'")

    db.commit()



#--------------------------- calculating monthly ratios from database -----------------------------
def get_monthly_ratio(names, month_id):
    
    monthly_ratio=[]
    monthly_coffees = get_monthly_coffees(names, month_id)
    
    for i in range(len(month_id)):
        temp=[]
        for j in range(len(names)):
            ratio=100*monthly_coffees[0][i][j]/monthly_coffees[1][i]
            temp.append(ratio)
        monthly_ratio.append(temp)

    return monthly_ratio


#----------------------------- getting all weekly breaks and weekly coffees ------------------------------
def get_weekly_coffees_breaks(names):
    weekly_data=[]

    cursor.execute("select week_id, breaks, coffees from weekly_data")
    tmp = cursor.fetchall()

    for i in range(len(tmp)):
        temp=[]
        temp.append(tmp[i][0])
        temp.append(tmp[i][1])
        temp.append(tmp[i][2])
        weekly_data.append(temp)

    return weekly_data

#----------------------------- writing all weekly breaks and weekly coffees into table ------------------------------
def write_weekly_coffees_breaks(names, month_id, update):
    cursor.execute("create table if not exists weekly_data (id int auto_increment, week_id char(7), breaks int, coffees int, primary key(id))")

    cursor.execute("SELECT max(id_ext) FROM breaks")  #getting month names from beginning to current
    temp=cursor.fetchone()
    temp=list(temp)
    last_date=datetime.date(int(temp[0][0:4]),int(temp[0][4:6]),int(temp[0][6:8]))
    if update == "full":
        start_date=datetime.date(2021, 3, 8)
    elif update == "simple":
        start_year = str(month_id[len(month_id)-2])[0:4]
        start_month = str(month_id[len(month_id)-2])[5:6]
        start_date=datetime.date(int(start_year), int(start_month), 1)

    if start_date > last_date:
        raise ValueError(f"Start date {start_date} is not before end date {last_date}")
    else:
        curr_date = start_date
        year = curr_date.year
        month = curr_date.month
        day = curr_date.day
        delta_days = (last_date-start_date).days
        weeknum_ids=[]
        breaks_daily=[]
        breaks_weekly=[]
        coffees_daily=[]
        coffees_weekly=[]
        text_weekly=[]
        weekly_data=[]

        for i in range(delta_days+1):
            id_day = str(curr_date.year)
            if curr_date.month < 10:
                id_day = id_day + "0" + str(curr_date.month)
            else:
                id_day = id_day + str(curr_date.month)
            if curr_date.day < 10:
                id_day = id_day + "0" + str(curr_date.day)
            else:
                id_day = id_day + str(curr_date.day)

            weeknum = datetime.date(curr_date.year, curr_date.month, curr_date.day).isocalendar()[1]
            
            cursor.execute("select count(id_ext) from breaks where id_ext like '"+id_day+"%'")
            tmp=cursor.fetchall()
            temp=[]
            if weeknum < 10:
                temp.append(int(str(curr_date.year)+"0"+str(weeknum)))
            else:
                if weeknum > 10 and curr_date.month == 1:                                   #avoiding new year in last week
                    temp.append(int(str(int(curr_date.year)-1)+str(weeknum)))
                else:
                    temp.append(int(str(curr_date.year)+str(weeknum)))
            temp.append(tmp[0][0])
            curr_date=curr_date+datetime.timedelta(days=1)
            breaks_daily.append(temp)
            
            total=0
            for j in range(len(names)):
                cursor.execute("select n_coffees from mbr_"+names[j]+" where id_ext like '"+id_day+"%'")
                tmp=cursor.fetchall()

                for k in range(len(tmp)):
                    total=total+tmp[k][0]
                    
            temp=[]
            if weeknum < 10:
                if int(str(curr_date.year)+"0"+str(weeknum)) not in weeknum_ids:
                    weeknum_ids.append(int(str(curr_date.year)+"0"+str(weeknum)))
                    text_weekly.append("0"+str(weeknum)+"/"+str(curr_date.year))
                temp.append(int(str(curr_date.year)+"0"+str(weeknum)))
            else:
                if weeknum > 10 and curr_date.month == 1:                                   #avoiding new year in last week
                    if int(str(int(curr_date.year)-1)+str(weeknum)) not in weeknum_ids:
                        weeknum_ids.append(int(str(int(curr_date.year)-1)+str(weeknum)))
                        text_weekly.append(str(weeknum)+"/"+str(int(curr_date.year)-1))
                    temp.append(int(str(int(curr_date.year)-1)+str(weeknum)))
                else:
                    if int(str(curr_date.year)+str(weeknum)) not in weeknum_ids:
                        weeknum_ids.append(int(str(curr_date.year)+str(weeknum)))
                        text_weekly.append(str(weeknum)+"/"+str(curr_date.year))
                    temp.append(int(str(curr_date.year)+str(weeknum)))
            temp.append(total)
            coffees_daily.append(temp)
    
    for i in range(len(weeknum_ids)):
        total_breaks=0
        total_coffees=0
        for j in range(len(breaks_daily)):
            if breaks_daily[j][0] == weeknum_ids[i]:
                total_breaks=total_breaks+breaks_daily[j][1]
            if coffees_daily[j][0] == weeknum_ids[i]:
                total_coffees=total_coffees + coffees_daily[j][1]
    
        cursor.execute("select count(*) from weekly_data where week_id like '"+text_weekly[i]+"'")
        tmp = cursor.fetchall()

        if tmp[0][0] == 0:
            cursor.execute("insert into weekly_data (week_id, breaks, coffees) values (%s, %s, %s)", (text_weekly[i], total_breaks, total_coffees))                     #inserting new week into table

        if i > len(weeknum_ids)-3:                         #checking for last 2 months  (on first date of a month the data of previous day, aka previous month, also have to be updated)
            cursor.execute("update weekly_data set breaks = "+str(total_breaks)+" where week_id = '"+text_weekly[i]+"'")    #always updating last two weeks
            cursor.execute("update weekly_data set coffees = "+str(total_coffees)+" where week_id = '"+text_weekly[i]+"'")

    db.commit()


#--------------------------- getting correlations between drinkers ------------------------------------
def get_correlation(names):
    corr_all=[]
    tot_coffees = get_total_coffees(names)

    corr_abs=[]
    corr_rel=[]
    for i in range(len(names)):

        cursor.execute("select "+names[i]+" from corr_abs")             #getting absolute correlation from table corr_abs
        temp_abs=cursor.fetchall()

        cursor.execute("select "+names[i]+" from corr_rel")             #getting relative correlation from table corr_rel
        temp_rel=cursor.fetchall()

        temp1=[]
        temp2=[]
        for j in range(len(names)):
            temp1.append(temp_abs[j][0])
            temp2.append(float(temp_rel[j][0]))
        corr_abs.append(temp1)                              #writing into array
        corr_rel.append(temp2)
    corr_all.append(corr_abs)
    corr_all.append(corr_rel)

    return corr_all

#--------------------------- writing correlations between drinkers into tables ------------------------------------
def write_correlation(names):
    #cursor.execute("drop table if exists corr_abs")
    #cursor.execute("drop table if exists corr_rel")
    cursor.execute("create table if not exists corr_abs (id int auto_increment, primary key(id))")
    cursor.execute("create table if not exists corr_rel (id int auto_increment, primary key(id))")      #creating tables

    tot_coffees=[]
    temp = get_total_coffees(names)
    for i in range(len(names)):
        tot_coffees.append(temp[i][1])
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='corr_abs' AND column_name='"+names[i]+"'") #check if name is already in table
        tmp = cursor.fetchall()
        
        if tmp[0][0] == 0:
            cursor.execute("alter table corr_abs add "+names[i]+" int")                     #creating name column if name is not in table
            cursor.execute("insert into corr_abs ("+names[i]+") values ("+str(0)+")")       #inserting dummy values for table size
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='corr_rel' AND column_name='"+names[i]+"'") #check if name is already in table
        tmp = cursor.fetchall()
        if tmp[0][0] == 0:       
            cursor.execute("alter table corr_rel add "+names[i]+" varchar(5)")                     #creating name column if name is not in table
            cursor.execute("insert into corr_rel ("+names[i]+") values ("+str(0)+")")       #inserting dummy values for table size

    for i in range(len(names)):
        cursor.execute("select id_ext from mbr_"+names[i])
        all_breaks=cursor.fetchall()
        for j in range(len(names)):
            temp=[]
            if i==j:
                cursor.execute("select n_coffees from mbr_"+names[j]+" inner join break_sizes on mbr_"+names[j]+".id_ext = break_sizes.id_ext where break_sizes.size = 1")   #for self-correlation in the sense of lonely breaks
                tmp=cursor.fetchall()
                
                for k in range(len(tmp)):
                    temp.append(int(tmp[k][0]))
            else:
                for k in range(len(all_breaks)):
                    cursor.execute("SELECT n_coffees from mbr_"+str(names[j])+" where id_ext = "+all_breaks[k][0])  #for correlation with other people
                    tmp=cursor.fetchall()
                    if len(tmp)>0:
                        temp.append(tmp[0][0])
            temp_abs1=0
            for l in range(len(temp)):
                temp_abs1=temp_abs1+temp[l]
            cursor.execute("update corr_abs set "+names[j]+" = "+str(temp_abs1)+" where id = "+str(i+1))            #updating corr_abs table
            cursor.execute("update corr_rel set "+names[j]+" = "+str(round(100*temp_abs1/tot_coffees[i],1))+"where id = "+str(i+1)) #updating corr_rel table
    db.commit()



#----------------------------- getting the percentage of total breaks per month and in total per person ------------------------
def get_perc_breaks(names, month_id):
    percentage=[]
    total_percentage=[]
    cursor.execute("select * from percentage_breaks")
    tmp = cursor.fetchall()

    for i in range(len(tmp)):
        temp=[]
        for j in range(len(names)):
            temp.append(float(tmp[i][j+2]))
        percentage.append(temp)

    return percentage

#---------------------------- calculating total breaks per month ---------------------------------------------
def get_tot_br_p_m(month_id):
    total_breaks=[]
    for i in range(len(month_id)):
        cursor.execute("select count(id_ext) from breaks where id_ext like '"+str(month_id[i])+"%'")
        tmp = cursor.fetchall()

        for j in range(len(tmp)):
            total_breaks.append(tmp[j][0])
    return total_breaks


#----------------------------- writing the percentage of total breaks per month and in total per person ------------------------
def write_perc_breaks(names, month_id, update):
    tot_breaks_pm = get_tot_br_p_m(month_id)
    #cursor.execute("drop table if exists percentage_breaks")
    cursor.execute("create table if not exists percentage_breaks (id int auto_increment, month varchar(6), primary key(id))")

    for i in range(len(names)):                                              #writing total cofees per month into coffees
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='percentage_breaks' AND column_name='"+names[i]+"'") #check if name is already in table
        tmp = cursor.fetchall()
        if tmp[0][0] == 0:
            cursor.execute("alter table percentage_breaks add "+names[i]+" varchar(5)")

    #cursor.execute("insert into percentage_breaks (month) values ('total')")
   
    percentage = []
    if update =="full":                                                                 #updating whole table
        for i in range(len(month_id)):  #writing total cofees per month into coffees
            cursor.execute("select count(*) from percentage_breaks where month = "+month_id[i])
            tmp = cursor.fetchall()
            if tmp[0][0] == 0:
                cursor.execute("insert into percentage_breaks (month) values ("+month_id[i]+")")
            for j in range(len(names)):
                cursor.execute("select count(id_ext) from mbr_"+names[j]+" where id_ext like '"+str(month_id[i])+"%'")
                tmp=cursor.fetchall()
                cursor.execute("update percentage_breaks set "+names[j]+" = "+str(round(100*tmp[0][0]/tot_breaks_pm[i],1))+" where month like '"+str(month_id[i])+"'")
    elif update == "simple":                                                            #updating only last two months
        for i in range(2):  #writing total cofees per month into coffees
            cursor.execute("select count(*) from percentage_breaks where month = "+month_id[len(month_id)-2+i])
            tmp = cursor.fetchall()
            if tmp[0][0] == 0:
                cursor.execute("insert into percentage_breaks (month) values ("+month_id[len(month_id)-2+i]+")")
            for j in range(len(names)):
                cursor.execute("select count(id_ext) from mbr_"+names[j]+" where id_ext like '"+str(month_id[len(month_id)-2+i])+"%'")
                tmp=cursor.fetchall()
                cursor.execute("update percentage_breaks set "+names[j]+" = "+str(round(100*tmp[0][0]/tot_breaks_pm[len(month_id)-2+i],1))+" where month like '"+str(month_id[len(month_id)-2+i])+"'")

    total_breaks = get_total_breaks(names)
    total = total_breaks[len(total_breaks)-1]

    for i in range(len(names)):
        cursor.execute("update percentage_breaks set "+names[i]+" = "+str(round(100*total_breaks[i]/total,1))+" where month like 'total'")
        
    db.commit()


#---------------------------- calculating monthly and total coffees per work day ------------------------
def get_coffees_per_work_day(names, month_id):
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)    

    coffees_per_work_day = []
    
    workdays = get_work_days(names, month_id)           #getting monthly work days
    total_workdays=[]
    total_p_w=[]

    for i in range(len(names)):
        total_workdays.append(0)                        #creating total workdays array
    
    cursor.execute("select * from monthly_coffees")     #getting monthly coffees
    tmp = cursor.fetchall()
    temp1=[]

    for i in range(len(month_id)):
        temp=[]
        
        for j in range(len(names)):
            temp.append(round(tmp[j][i+2]/workdays[i][j],3))     #dividing monthly coffees by monthly work days
            total_workdays[j]=total_workdays[j]+workdays[i][j] #getting total workdays per person
        temp1.append(temp)
    
    cursor.execute("select coffees from total_coffees")
    tmp=cursor.fetchall()
    for i in range(len(names)):
        total_p_w.append(round(tmp[i][0]/total_workdays[i],3))
        
    coffees_per_work_day.append(total_p_w)
    coffees_per_work_day.append(temp1)
        
    return coffees_per_work_day





@st.cache
def get_cumulated_coffees():
	cumulated_coffees = [[19,28,44,63,92,121,153,183,197,238,277,312,349,372,372],[15,21,27,47,75,95,119,144,173,195,227,261,296,314,314],[13,19,31,47,72,107,135,172,203,230,266,294,315,328,328],[10,13,20,32,59,96,133,148,170,214,224,230,235,242,242],[18,19,37,58,92,127,162,188,209,252,294,324,360,382,382],[0,0,0,0,19,47,70,79,85,101,123,140,166,183,183],[0,0,0,0,0,12,30,38,43,56,58,58,58,58,58],[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],[0,0,0,0,0,0,0,0,0,0,0,0,3,3,3]]
	return cumulated_coffees



@st.cache
def get_social_score():
	social_score_total = [[100.0, 80.4, 24.0, 37.7, 99.1, 50.8, 6.4, 0.1, 0.2], [[81.14399999999999, 68.10535, 10.831040000000002, 63.7146, 92.42434782608694, 27.048000000000005, 0.0, 0.0, 0.0], [118.28099999999999, 76.44780000000002, 67.98, 82.65937, 122.81499999999997, 72.568, 33.87852000000001, 0.0, 0.0], [91.85471999999999, 53.34992999999999, 28.52148, 97.36888, 95.41152, 39.09664, 23.25, 0.0, 0.0], [91.17360000000001, 61.19932000000001, 45.3152, 28.454399999999996, 85.07730000000001, 11.280000000000001, 7.5, 0.0, 0.0], [29.304600000000004, 81.81675, 46.6992, 58.57527272727273, 54.89687272727273, 4.947090909090909, 4.2588, 0.0, 0.0], [156.83787, 67.02525090909091, 40.84476, 153.5523, 148.42398, 34.67020909090909, 22.575779999999998, 0.0, 0.0], [97.36402000000001, 71.495, 35.43119999999999, 1.8718363636363635, 104.5008, 37.47071999999999, 0.5625, 0.0, 0.0], [95.79024, 95.41933333333333, 22.1996, 4.501891428571429, 85.82832761904761, 33.638400000000004, 0.0, 0.0, 0.0], [175.51908, 165.594, 32.187400000000004, 4.725, 161.7792, 108.17712, 0.0, 0.0, 2.73429], [107.14062857142859, 64.38528000000002, 12.5307, 12.521249999999998, 119.0085, 85.66513714285715, 0.0, 0.4821428571428571, 0.0], [150.4267142857143, 123.95040000000002, 1.7836199999999998, 0.162, 114.62267142857144, 66.816, 0.0, 0.0, 0.0]]]
	return social_score_total

#@st.cache
def get_expectation_values():
	exp_values = [37.1, 33.2, 2.6, -2.7, 31.8, 34.2, 0.0, -0.7, 2.5]
	return exp_values

@st.cache
def get_stdev():
	stdev = [4.8, 5.8, 7.8, 10.3, 7.5, 7.1, 5.7, 0.3, 1.3]
	return stdev

@st.cache
def get_mad():
	mad = [['TKPBW95', 6.2], ['TKPBW95p', 6.06], ['dynamic', 6.13], ['KKBK21', 6.67], ['KKBK21-G2', 6.4], ['BS3LYP', 6.29], ['BS3LYPp', 6.06], ['PBTK', 7.94], ['PJGL21', 6.73], ['KKBK21-G2I', 8.12], ['dynamicp', 6.07]]
	return mad	

@st.cache
def get_functionals():
	all_func = ['BS3LYP', 'BS3LYPp', 'dynamic', 'dynamicp', 'KKBK21', 'KKBK21-G2', 'KKBK21-G2I', 'PBTK', 'PJGL21', 'TKPBW95', 'TKPBW95p']
	return all_func

@st.cache
def get_active_func():
	act_func = "TKPBW95p"
	return act_func

@st.cache
def get_prizes():
	prizes = [['202103', 4, 'Kaffeemeister', 40], ['202103', 2, 'Hotshot', 25], ['202103', 4, 'Genosse', 10], ['202104', 3, 'Kaffeemeister', 40], ['202104', 1, 'Hotshot', 25], ['202104', 4, 'Genosse', 10], ['202105', 3, 'Kaffeemeister', 40], ['202105', 1, 'Hotshot', 25], ['202105', 3, 'Genosse', 10], ['202106', 2, 'Kaffeemeister', 40], ['202106', 3, 'Hotshot', 25], ['202106', 0, 'Genosse', 10], ['202107', 2, 'Kaffeemeister', 40], ['202107', 4, 'Hotshot', 25], ['202107', 1, 'Genosse', 10], ['202108', 3, 'Kaffeemeister', 40], ['202108', 5, 'Hotshot', 25], ['202108', 0, 'Genosse', 10], ['202109', 4, 'Kaffeemeister', 40], ['202109', 5, 'Hotshot', 25], ['202109', 4, 'Genosse', 10], ['202110', 0, 'Kaffeemeister', 40], ['202110', 0, 'Hotshot', 25], ['202110', 0, 'Genosse', 10], ['202111', 0, 'Kaffeemeister', 40], ['202111', 3, 'Hotshot', 25], ['202111', 0, 'Genosse', 10], ['202112', 0, 'Kaffeemeister', 40], ['202112', 1, 'Hotshot', 25], ['202112', 4, 'Genosse', 10], ['202201', 1, 'Kaffeemeister', 40], ['202201', 5, 'Hotshot', 25], ['202201', 0, 'Genosse', 10]]
	return prizes


#----------------------------------------- getting all members from database ---------------------------------------
@st.cache
def get_members():
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

    names=[]

    cursor.execute("select name from members")              #getting all members tables
    mbrs=cursor.fetchall()
    mbrs=list(mbrs)
    for i in range(len(mbrs)):
        names.append(mbrs[i][0])
    db.close()
    return names



#----------------------------- getting last 10 breaks from database ---------------------------------
#@st.cache
def get_last_breaks(last_break):
	cursor.execute("select * from breaks order by id_ext desc limit 10")
	breaks=cursor.fetchall()
	cursor.execute("select * from drinkers order by id_ext desc limit 10")
	drinkers=cursor.fetchall()

	last_breaks=[]
	for i in range(len(breaks)):
		temp=[]
		date=str(breaks[len(breaks)-i-1][2])+"."+str(breaks[len(breaks)-i-1][3])+"."+str(breaks[len(breaks)-i-1][4])
		temp.append(breaks[len(breaks)-i-1][1])
		temp.append(date)
		temp.append(drinkers[len(drinkers)-i-1][2])
		temp.append(drinkers[len(drinkers)-i-1][3])
		last_breaks.append(temp)

	return last_breaks


#------------------------------------------------------------------------------------------------------------------------------------------------------------

#----------------------------- getting all months from start date to now ---------------------------------
@st.cache
def get_months(first_date):
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)
    
    month_info=[]
    months=[]
    month_id=[]

    cursor.execute("SELECT max(id_ext) FROM breaks")        #getting month names from beginning to current
    temp=cursor.fetchone()
    temp=list(temp)

    last_date=datetime.date(int(temp[0][0:4]),int(temp[0][4:6]),int(temp[0][6:8]))
    for month in months_between(first_date,last_date):
    #for i in range(months_between(first_date,last_date)):
        if(month.month<10):
            month_id.append(str(month.year)+"0"+str(month.month))
        else:
            month_id.append(str(month.year)+str(month.month))
        months.append(month.strftime("%B")[0:3]+" '"+month.strftime("%Y")[2:4])
    month_info.append(months)
    month_info.append(month_id)
    
    db.close()
    return month_info
    

def months_between(start_date, end_date):                   #method to get months between two dates
    if start_date > end_date:
        raise ValueError(f"Start date {start_date} is not before end date {end_date}")
    else:
        year = start_date.year
        month = start_date.month
	
        #counter=0
        while (year, month) <= (end_date.year, end_date.month):
            yield datetime.date(year, month, 1)
            # Move to the next month.  If we're at the end of the year, wrap around
            # to the start of the next.
            #
            # Example: Nov 2017
            #       -> Dec 2017 (month += 1)
            #       -> Jan 2018 (end of year, month = 1, year += 1)
            #
            if month == 12:
                month = 1
                year += 1
            else:
                month += 1
            #counter += 1
    #return counter

#------------------------- getting work days per month per person ------------------------
@st.cache
def get_work_days(names, month_id):
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

    cursor.execute("select * from holidays")            #getting holidays
    tmp = cursor.fetchall()

    workdays=[]
    for i in range(len(month_id)):
        temp=[]
        for j in range(len(names)):
            if tmp[i][j+3] == None:
                temp.append(tmp[i][2])
            else:
                temp.append(tmp[i][2]-tmp[i][j+3])
        workdays.append(temp)
    return workdays

#------------------------ getting functionals from database ------------------
@st.cache
def get_functionals():
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

    cursor.execute("select name from func_param")
    tmp=cursor.fetchall()

    func_names=[]
    for i in range(len(tmp)):
        func_names.append(tmp[i][0])
 
    return sorted(func_names, key=str.lower)

#------------------------- getting all functional parameters -------------------
def get_parameters():
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

    cursor.execute("select * from func_param")
    tmp = cursor.fetchall()

    parameters=[]
    for i in range(len(tmp)):
        temp=[]
        for j in range(8):
            temp.append(tmp[i][j+1])
        parameters.append(temp)
    
    return parameters


def get_active_func():
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

    cursor.execute("select active_func from update_status")
    func = cursor.fetchall()
    return func[0][0]

#-------------------------- calculating standard deviation of deviations etc ---------------------------------
def variance(data, ddof=0):
    n = len(data)
    mean = sum(data) / n
    return sum((x - mean) ** 2 for x in data) / (n - ddof)

def stdev(data):
    var = variance(data)
    std_dev = math.sqrt(var)
    return std_dev

#------------------------- getting the MAD for given functional ---------------------------------------------------
def calc_mad_corr(names, month_id, func):
    func_data = calc_exp_values_dev(names, month_id, func)

    ratio =  0.2

    total_mad=0
    total_stdev=0
    counter=0
    for i in range(len(func_data[1])):
        for j in range(len(names)):
             counter += 1
             total_mad += abs(func_data[1][i][j])
    mad = total_mad/counter
    counter=0
    for i in range(len(func_data[2])):
        for j in range(len(names)):
            if func_data[2][i-1][j] != 0 and func_data[2][i][j] != 0:
                counter += 1
                total_stdev += func_data[2][i][j]
    m_stdev = total_stdev/counter

    mad_corr = ratio * mad + (1-ratio) * m_stdev
    
    return round(mad_corr,2)

#--------------------------- getting all holidays ------------------------------
@st.cache
def get_all_holidays(timestamp):
	cursor.execute("select * from holidays")
	tmp=cursor.fetchall()
	
	holidays=[]
	for i in range(len(tmp)):
		temp=[]
		for j in range(len(tmp[i])-1):
			if tmp[i][j+1] == None:
				temp.append(0)
			else:
				temp.append(tmp[i][j+1])
		holidays.append(temp)
   
	return holidays


#--------------------------- checking if database is up to date ----------------
def check_update_status():
    cursor.execute("select update_date from update_status")
    tmp = cursor.fetchall()

    if datetime.date.today() > tmp[0][0]:
        print("Database not up to date")
        update_database(tmp[0][0].month)
        
    else:
        print("Database up to date")
    
    
#------------------------- updates database -------------------------------------
def update_database(month):

    print("Recalculating ", end="", flush=True)
    cursor.execute("update update_status set update_date = curdate()")

    names = get_members()
    month_id_all = get_months(datetime.date(2020,11,1))[1]
    month_id_daily = get_months(datetime.date(2021,3,8))[1]

    update="simple"     #keyword for variation function

    cursor.execute("select active_func from update_status")         #getting functional currently in use
    functional=cursor.fetchall()[0][0]
    
    write_monthly_coffees(names,month_id_all, update)
    print("...", end="", flush=True)
    write_total_coffees(names)
    print("...", end="", flush=True)
    write_correlation(names)
    print("..", end="", flush=True)
    write_weekly_coffees_breaks(names, month_id_daily, update)
    print(".", end="", flush=True)
    write_perc_breaks(names, month_id_daily, update)
    print(".", end="", flush=True)
    if datetime.date.today().month != month:    #checking for new month
        write_exp_values_dev(names, month_id_all, update)
        calc_dynamic_functional(names,month_id)
        print("..", end="", flush=True)
    write_variation_factor(names, month_id_daily,update)
    print(".")


    
    print("Database was successfully updated")
    
    db.commit()


#------------------------- updates database -------------------------------------
def manual_update():

    print("Recalculating ", end="", flush=True)
    cursor.execute("update update_status set update_date = curdate()")

    names = get_members()
    month_id_all = get_months(datetime.date(2020,11,1))[1]
    month_id_daily = get_months(datetime.date(2021,3,8))[1]

    update="full"     #keyword for variation function

    cursor.execute("select active_func from update_status")         #getting functional currently in use
    func_selected=cursor.fetchall()[0][0]
    
    write_monthly_coffees(names,month_id_all, update)
    print("...", end="", flush=True)
    write_total_coffees(names)
    print("...", end="", flush=True)
    write_correlation(names)
    print("..", end="", flush=True)
    write_weekly_coffees_breaks(names, month_id_daily, update)
    print(".", end="", flush=True)
    write_perc_breaks(names, month_id_daily, update)
    print(".", end="", flush=True)
    write_exp_values_dev(names, month_id_all, func_selected, update)
    print("..", end="", flush=True)
    write_variation_factor(names, month_id_daily,update)
    print(".")
    
    print("Database was successfully updated")
    
    db.commit()


#calc_polynomial_functional(get_members(), get_months(datetime.date(2020,11,1))[1])

write_simple_data()
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
check_update_status()        #------------------------------------------------------- updating database to current day ---------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------


