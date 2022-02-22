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
	#db = mysql.connect(user='PBTK', password='akstr!admin2',
        #                host='212.227.72.95',
        #                database='coffee_list')
	#cursor=db.cursor(buffered=True)
	
	cursor.execute("select name, password, admin from members")
	user_data=cursor.fetchall()
	#user_data=[['TK', 'akstr!admin2',1],['PB','akstr!admin2',1],['NV',None,None],['DB',None,None],['FLG','baddragon',None],['SHK',None,None],['TB',None,None],['TT',None,None],['RS',None,None]]
	#db.close()
	return user_data


def get_simple_data():
	return
	

@st.cache
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
		cursor.execute("insert into simple_data (parameter, value) values ('diagrams', 22)")
	

	names = get_members()
	month_id = get_months(datetime.date(2020,11,1))[1]
	coffees = get_monthly_coffees(names, month_id)								#calculating simple data from different tables
	st.write(coffees)
	acr_dr = 0
	cursor.execute("select count(*) from breaks")
	breaks = cursor.fetchall()
	cups = 0
	for i in range(len(names)):
		for j in range(len(month_id)):
			cups += coffees[0][i][j]
		if coffees[0][i][len(month_id)-3] != 0 and coffees[0][i][len(month_id)-2] != 0:
			act_dr += 1

	cursor.execute("update simple_data set value = "+str(len(names))+" where parameter = 'drinkers'")	#updating simple_data table
	cursor.execute("update simple_data set value = "+str(act_dr)+" where parameter = 'acr_dr'")
	cursor.execute("update simple_data set value = "+str(len(month_id))+" where parameter = 'months'")
	cursor.execute("update simple_data set value = "+str(breaks[0][0])+" where parameter = 'breaks'")
	cursor.execute("update simple_data set value = "+str(cups)+" where parameter = 'cups'")
	db.commit()
	return simple_data


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

@st.cache
def get_monthly_ratios():
	monthly_ratios = [[25.33,36.0,27.12,21.59,17.9,14.8,16.24,20.0,10.94,19.9,21.31,23.33,23.13,23.0,100],[20.0,24.0,10.17,22.73,17.28,10.2,12.18,16.67,22.66,10.68,17.49,22.67,21.88,18.0,0],[17.33,24.0,20.34,18.18,15.43,17.86,14.21,24.67,24.22,13.11,19.67,18.67,13.13,13.0,0],[13.33,12.0,11.86,13.64,16.67,18.88,18.78,10.0,17.19,21.36,5.46,4.0,3.13,7.0,0],[24.0,4.0,30.51,23.86,20.99,17.86,17.77,17.33,16.41,20.87,22.95,20.0,22.5,22.0,0],[0.0,0.0,0.0,0.0,11.73,14.29,11.68,6.0,4.69,7.77,12.02,11.33,16.25,17.0,0],[0.0,0.0,0.0,0.0,0.0,6.12,9.14,5.33,3.91,6.31,1.09,0.0,0.0,0.0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0],[0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0.0,0]]
	return monthly_ratios

@st.cache
def get_total_coffees():
	total_coffees = [372, 314, 328, 242, 382, 183, 58, 1, 3]
	return total_coffees

@st.cache
def get_corr():
	corr_abs = [[[0, 257, 94, 126, 272, 140, 38, 0, 3], [258, 2, 77, 93, 229, 97, 31, 0, 3], [94, 77, 163, 64, 96, 67, 22, 1, 1], [130, 96, 66, 22, 140, 87, 43, 1, 1], [270, 226, 97, 134, 21, 139, 35, 1, 3], [139, 95, 67, 82, 139, 27, 18, 1, 2], [38, 31, 22, 39, 35, 18, 11, 0, 0], [0, 0, 1, 1, 1, 1, 0, 0, 0], [3, 3, 1, 1, 3, 2, 0, 0, 1]], [[0.0, 74.5, 28.1, 52.1, 66.8, 70.0, 65.5, 0.0, 75.0], [63.7, 0.6, 23.0, 38.4, 56.3, 48.5, 53.4, 0.0, 75.0], [23.2, 22.3, 48.7, 26.4, 23.6, 33.5, 37.9, 100.0, 25.0], [32.1, 27.8, 19.7, 9.1, 34.4, 43.5, 74.1, 100.0, 25.0], [66.7, 65.5, 29.0, 55.4, 5.2, 69.5, 60.3, 100.0, 75.0], [34.3, 27.5, 20.0, 33.9, 34.2, 13.5, 31.0, 100.0, 50.0], [9.4, 9.0, 6.6, 16.1, 8.6, 9.0, 19.0, 0.0, 0.0], [0.0, 0.0, 0.3, 0.4, 0.2, 0.5, 0.0, 0.0, 0.0], [0.7, 0.9, 0.3, 0.4, 0.7, 1.0, 0.0, 0.0, 25.0]]]
	return corr_abs

@st.cache
def get_perc_p_m():
	perc_p_m = [[41.38,37.93,36.21,41.38,44.83,27.59,0.0,0.0,0.0],[43.66,28.17,49.3,52.11,49.3,39.44,16.9,0.0,0.0],[44.44,33.33,38.89,51.39,48.61,31.94,25.0,0.0,0.0],[46.88,39.06,57.81,23.44,40.63,14.06,12.5,0.0,0.0],[25.45,52.73,56.36,40.0,38.18,10.91,09.09,0.0,0.0],[61.19,32.84,40.3,65.67,64.18,23.88,19.4,0.0,0.0],[48.15,39.51,44.44,12.35,51.85,27.16,2.47,0.0,0.0],[56.45,54.84,45.16,9.68,48.39,27.42,0.0,0.0,0.0],[69.81,66.04,39.62,9.43,67.92,49.06,0.0,0.0,5.6],[62.16,48.65,35.14,18.92,59.46,45.95,0.0,3.2,0.0],[11,11,11,11,11,11,0,1,0]]
	return perc_p_m

@st.cache
def get_perc_tot():
	perc_tot = [49.4,42.1,44.7,33.4,51.0,29.0,11.0,0.0,0.0]
	return perc_tot

@st.cache
def get_names():
	names = ['TK','PB','NV','DB','FLG','SHK','TB','TT','RS']
	return names

@st.cache
def get_cumulated_coffees():
	cumulated_coffees = [[19,28,44,63,92,121,153,183,197,238,277,312,349,372,372],[15,21,27,47,75,95,119,144,173,195,227,261,296,314,314],[13,19,31,47,72,107,135,172,203,230,266,294,315,328,328],[10,13,20,32,59,96,133,148,170,214,224,230,235,242,242],[18,19,37,58,92,127,162,188,209,252,294,324,360,382,382],[0,0,0,0,19,47,70,79,85,101,123,140,166,183,183],[0,0,0,0,0,12,30,38,43,56,58,58,58,58,58],[0,0,0,0,0,0,0,0,0,0,0,0,0,1,1],[0,0,0,0,0,0,0,0,0,0,0,0,3,3,3]]
	return cumulated_coffees

@st.cache
def get_weeks():
	weeks = ['10/2021', '11/2021', '12/2021', '13/2021', '14/2021', '15/2021', '16/2021', '17/2021', '18/2021', '19/2021', '20/2021', '21/2021', '22/2021', '23/2021', '24/2021', '25/2021', '26/2021', '27/2021', '28/2021', '29/2021', '30/2021', '31/2021', '32/2021', '33/2021', '34/2021', '35/2021', '36/2021', '37/2021', '38/2021', '39/2021', '40/2021', '41/2021', '42/2021', '43/2021', '44/2021', '45/2021', '46/2021', '47/2021', '48/2021', '49/2021', '50/2021', '51/2021', '52/2021', '01/2022', '02/2022', '03/2022', '04/2022']
	return weeks

@st.cache
def get_coffee_breaks_weekly():
	coffee_breaks_weekly = [[18, 42], [18, 38], [15, 46], [10, 14], [15, 32], [18, 50], [18, 62], [16, 46], [12, 44], [15, 45], [20, 52], [21, 44], [14, 40], [12, 30], [20, 44], [12, 26], [13, 34], [16, 30], [10, 22], [12, 23], [14, 40], [17, 44], [13, 42], [16, 51], [16, 53], [13, 31], [20, 43], [16, 46], [21, 44], [19, 46], [11, 28], [14, 31], [20, 43], [11, 31], [11, 36], [16, 42], [10, 38], [11, 33], [10, 33], [8, 25], [19, 40], [5, 19], [0, 0], [2, 3], [10, 24], [11, 37], [2, 7]]
	return coffee_breaks_weekly

@st.cache
def get_coffees_per_work_day():
	coffees_per_work_day_total = [[1.324, 1.158, 1.006, 0.785, 1.344, 0.654, 0.18, 0.006, 0.012], [[0.905, 0.714, 0.619, 0.476, 0.857, 0.0, 0.0, 0.0, 0.0], [0.529, 0.429, 0.3, 0.176, 0.071, 0.0, 0.0, 0.0, 0.0], [0.842, 0.316, 0.632, 0.368, 0.947, 0.0, 0.0, 0.0, 0.0], [0.95, 1.0, 0.8, 0.6, 1.05, 0.0, 0.0, 0.0, 0.0], [1.261, 1.261, 1.087, 1.174, 1.7, 0.826, 0.0, 0.0, 0.0], [1.55, 1.25, 1.75, 1.8, 1.944, 1.35, 1.2, 0.0, 0.0], [1.684, 1.263, 1.474, 1.947, 1.842, 1.211, 0.947, 0.0, 0.0], [1.429, 1.19, 1.762, 0.714, 1.238, 0.429, 0.381, 0.0, 0.0], [1.4, 1.381, 1.409, 1.294, 1.167, 0.238, 0.227, 0.0, 0.0], [1.864, 1.833, 1.227, 2.0, 1.955, 0.941, 0.591, 0.0, 0.0], [1.773, 1.455, 1.636, 0.769, 1.955, 1.0, 0.091, 0.0, 0.0], [1.571, 1.579, 1.429, 0.3, 1.688, 0.81, 0.0, 0.0, 0.0], [1.762, 1.667, 1.048, 0.19, 1.714, 1.238, 0.0, 0.0, 0.143], [1.6, 1.2, 0.667, 0.412, 1.375, 1.133, 0.0, 0.048, 0.0], [1.381, 1.476, 0.143, 0.048, 1.143, 0.762, 0.0, 0.0, 0.048]]]
	return coffees_per_work_day_total

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
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

    cursor.execute("select update_date from update_status")
    tmp = cursor.fetchall()

    if datetime.date.today() > tmp[0][0]:
        print("Database not up to date")
        update_database(tmp[0][0].month)
        
    else:
        print("Database up to date")
    
    db.commit()
    db.close
    
#------------------------- updates database -------------------------------------
def update_database(month):
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

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
    db.close


#------------------------- updates database -------------------------------------
def manual_update():
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
    host='212.227.72.95',
    database='coffee_list')
    cursor=db.cursor(buffered=True)

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
    db.close


#calc_polynomial_functional(get_members(), get_months(datetime.date(2020,11,1))[1])

write_simple_data()
#-------------------------------------------------------------------------------------------------------------------------------------------------------------
check_update_status()        #------------------------------------------------------- updating database to current day ---------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------


