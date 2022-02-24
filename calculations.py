import streamlit as st
import math
import mysql.connector as mysql
import numpy
import datetime
from datetime import date
import pandas as pd
from plotly import *
import plotly.express as px


#@st.cache(allow_output_mutation=True, hash_funcs={"_thread.RLock": lambda _: None})
def init_connection():
    return mysql.connect(**st.secrets["mysql"])
db = init_connection()
cursor = db.cursor(buffered=True)


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


#----------------------------------------- getting monthly coffees from database --------------------------------------
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



#------------------ getting expectation values from database, maybe recalculating if functional has been updated ------
def get_expectation_values(names, month_id, func_selected):
    cursor.execute("select active_func from update_status")
    tmp=cursor.fetchall()

    if tmp[0][0] != func_selected:
        update="full"

        write_exp_values_dev(names, month_id, func_selected, update)
        cursor.execute("update update_status set active_func = '"+func_selected+"'")
        db.commit()

        
    cursor.execute("select * from exp_values where month = "+max(month_id))
    tmp=cursor.fetchall()

    exp_values=[]
    for i in range(len(tmp[0])-2):
        exp_values.append(float(tmp[0][i+2]))
    return exp_values

#----------------------- getting standard deviations from database, does not recalculate if functional has been updated! ---
def get_stdev(names, month_id):
	cursor.execute("select * from exp_values_stdev where month = "+str(month_id[len(month_id)-1]))
	tmp=cursor.fetchall()
    
	stdev=[]
	for i in range(len(names)):
		stdev.append(float(tmp[0][i+2]))
	return stdev

#------------------------- getting the MAD for every functional ---------------------------------------------------
def get_mad(names, month_id):
    param = get_parameters()

    mad_total=[]
    for i in range(len(param)):
        for j in range(len(param[i])-1):
            param[i][j+1] = float(param[i][j+1])
        temp=[]
        temp.append(param[i][0])
        temp.append(calc_mad_corr(names, month_id, param[i]))
        mad_total.append(temp)
    return mad_total

#-----------------------------calculating expectation values, deviation and standard deviation-----------------------------
def calc_exp_values_dev(names, month_id, func):
    coffees = get_coffees_per_work_day(names, month_id)[1]
    workdays = get_work_days(names, month_id)

    cursor.execute("select work_days from holidays")
    total_wd = cursor.fetchall()

    expectation_values=[]
    deviation=[]
    standard_dev=[]
    total=[]

    for i in range(len(month_id)):
        temp_exp=[]
        temp_dev=[]
        temp_stdev=[]
        for j in range(len(names)):
            if i == 0:
                if j < 5:
                    exp_value = 10.71               #first month: average of all coffees drank
                else:
                    exp_value = 0.0
            elif i == 1:
                exp_value = coffees[i-1][j] * workdays[i][j]      #second month: coffees from first month scaled to second month
            elif i == 2:
                exp_value = (coffees[i-2][j]*0.33 + coffees[i][j]*0.67) * workdays[i][j]    #third month: 0.33*first month + 0.67*second month scaled to third month
            elif i == 3 or i == 4:
                exp_value = (coffees[i-3][j]*func[1] + coffees[i-2][j]*func[2] + coffees[i-1][j]*func[3]) * workdays[i][j]  #fourth and fifth month: complete original functional
            else:
                if month_id[i] > "202109" and names[j] == "TB":
                    exp_value = 0.0
                else:           #functional values per work day
                    oF = coffees[i-3][j]*func[1] + coffees[i-2][j]*func[2] + coffees[i-1][j]*func[3]        #value of original functional
                    cub = (coffees[i-3][j]-coffees[i-4][j]-(8*coffees[i-3][j] - coffees[i-2][j] - 7*coffees[i-4][j] - 2*(coffees[i-1][j] - 9/2*coffees[i-2][j] + 9*coffees[i-3][j] - 11/2*coffees[i-4][j]))/4 - (coffees[i-1][j] - 9/2*coffees[i-2][j] + 9*coffees[i-3][j] - 11/2*coffees[i-4][j])/3) * 64 + (8*coffees[i-3][j] - coffees[i-2][j] - 7*coffees[i-4][j] - 2*(coffees[i-1][j] - 9/2*coffees[i-2][j] + 9*coffees[i-3][j] - 11/2*coffees[i-4][j])) * 4 + (coffees[i-1][j] - 4.5*coffees[i-2][j] + 9*coffees[i-3][j] - 5.5*coffees[i-4][j]) * 4/3 + coffees[i-4][j] #value of cubic function
                    sq = (coffees[i-3][j]-coffees[i-1][j]+2*coffees[i-2][j]-2*coffees[i-3][j])/2 * 9 + ((coffees[i-1][j]-coffees[i-3][j]+4*coffees[i-3][j]-4*coffees[i-2][j])/2) * 3 - coffees[i-3][j]              #value of squared function
                    lin = (coffees[i-1][j]-coffees[i-2][j])*2+coffees[i-2][j]                               #value of linear function
                    exp_value = (oF * func[4] + cub * func[5] + sq * func[6] + lin * func[7]) * workdays[i][j]    #from fifth month on: original functional with polynomial
            temp_exp.append(exp_value)                                                      #setting up expectation value array
            if not i == len(month_id)-1:         #skips the last month
                temp_dev.append(exp_value-(coffees[i][j]*workdays[i][j]))                   #setting up deviation array
                data=[]
                for k in range(i):
                    data.append(deviation[k][j])
                if data != []:
                    temp_stdev.append(stdev(data))
        expectation_values.append(temp_exp)
        if temp_dev != []:
            deviation.append(temp_dev)
        if temp_stdev != []:
            standard_dev.append(temp_stdev)

    total.append(expectation_values)
    total.append(deviation)
    total.append(standard_dev)

    return total


#----------------------------- calculating parameters for dynamic functional -----------------------------
def calc_dynamic_functional(names, month_id):
    step = 0.05
    best_mad = 99999
    func=['dynamic',0,0,0,1,0.0,0.0,0.0]
    param=[0.0,0.0,0.0]
    m_3 = 1
    m_2 = 0
    m_1 = 0
    for i in range(int(1/step)+1):
        m_3 = round(1 - (i*step),2)
        for j in range(i+1):                            #permutating the 3 parameters in 0.05 steps (so that the sum is always 1)
            m_2 = abs(round((1-m_3) - (j*step),2))
            m_1 = abs(round(1-m_3-m_2,2))
            func[1] = m_3
            func[2] = m_2
            func[3] = m_1
            mad = calc_mad_corr(names, month_id, func)       #calculating MAD for given parameters
            if mad < best_mad:
                best_mad = mad
                param[0] = m_3
                param[1] = m_2
                param[2] = m_1
    
    cursor.execute("update func_param set m_3 = "+str(param[0])+", m_2 = "+str(param[1])+", m_1 = "+str(param[2])+" where name = 'dynamic'")
    #cursor.execute("update func_param set m_3 = "+str(param[0])+", m_2 = "+str(param[1])+", m_1 = "+str(param[2])+" where name = 'dynamicp'")
    db.commit()


#----------------------------- calculating parameters for dynamic functional of all parameters -----------------------------
def calc_dynamic_all(names, month_id):
    step = 0.05
    best_mad = 99999
    func=['dynamicp',0,0,0,1,0.0,0.0,0.0]
    param=[0.0,0.0,0.0,0.0,0.0,0.0,0.0]
    m_3 = 1
    m_2 = 0
    m_1 = 0
    print(datetime.datetime.now())
    print("calculating...")
    for i in range(int(1/step)+1):
        m_3 = round(1 - (i*step),2)
        func[1] = m_3
        for j in range(i+1):                            #permutating the 3 parameters in 0.05 steps (so that the sum is always 1)
            m_2 = abs(round((1-m_3) - (j*step),2))
            m_1 = abs(round(1-m_3-m_2,2))
            orig_func = 1
            cub_func=0
            sq_func=0
            lin_func=0
            func[2] = m_2
            func[3] = m_1
            print(func)
            for k in range(int(1/step)+1):
                orig_func = round(1 - (k*step),2)
                func[4] = orig_func
                
                for l in range(k+1):
                    cub_func = abs(round((1-orig_func) - (l*step),2))
                    func[5] = cub_func
                    for m in range(l+1):
                        sq_func = abs(round((1-orig_func-cub_func) - (m*step),2))
                        lin_func = abs(round(1- orig_func - cub_func - sq_func,2))
                        func[6] = sq_func
                        func[7] = lin_func
                        
                        mad = calc_mad_corr(names, month_id, func)       #calculating MAD for given parameters
                        if mad < best_mad:
                            best_mad = mad
                            param[0] = m_3
                            param[1] = m_2
                            param[2] = m_1
                            param[3] = orig_func
                            param[4] = cub_func
                            param[5] = sq_func
                            param[6] = lin_func
                            print("Found better values:", end=" ", flush=True)
                            print(param, end=", ", flush=True)
                            print(mad)
    

    cursor.execute("update func_param set m_3 = "+str(param[0])+", m_2 = "+str(param[1])+", m_1 = "+str(param[2])+", orig_func = "+str(param[3])+", cub_func = "+str(param[4])+", sq_func = "+str(param[5])+", lin_func = "+str(param[6])+" where name = 'dynamicp'")

    db.commit()


#----------------------------- calculating parameters for dynamic polynomial functional -----------------------------
def calc_polynomial_functional(names, month_id):
    step = 0.05
    best_mad = 99999
    func=['polypony',0,0,0,0,1,0.0,0.0]
    param=[0.0,0.0,0.0]
    cub = 1
    sq = 0
    lin = 0
    for i in range(int(1/step)+1):
        cub = round(1 - (i*step),2)
        for j in range(i+1):                            #permutating the 3 parameters in 0.05 steps (so that the sum is always 1)
            sq = abs(round((1-cub) - (j*step),2))
            lin = abs(round(1-cub-sq,2))
            func[5] = cub
            func[6] = sq
            func[7] = lin
            mad = calc_mad_corr(names, month_id, func)       #calculating MAD for given parameters
            if mad < best_mad:
                best_mad = mad
                param[0] = cub
                param[1] = sq
                param[2] = lin
    
    cursor.execute("update func_param set cub_func = "+str(param[0])+", sq_func = "+str(param[1])+", lin_func = "+str(param[2])+" where name = 'polypony'")
    db.commit()



#----------------------------- writing expectation values, deviation and standard deviation into database -----------------------------
def write_exp_values_dev(names, month_id, functional, update):
    param=get_parameters()
    for i in range(len(param)):
        if param[i][0] == functional:
            func = param[i]                 #getting functional parameters for active functional
    for i in range(len(func)-1):
        func[i+1] = float(func[i+1])        #converting parameters to float


    temp = calc_exp_values_dev(names, month_id, func)
    exp_values = temp[0]
    dev = temp[1]
    stdev = temp[2]

    #cursor.execute("drop table if exists exp_values")
    #cursor.execute("drop table if exists exp_values_dev")
    #cursor.execute("drop table if exists exp_values_stdev")
    cursor.execute("create table if not exists exp_values (id int auto_increment, month int, primary key(id))")
    cursor.execute("create table if not exists exp_values_dev (id int auto_increment, month int, primary key(id))")
    cursor.execute("create table if not exists exp_values_stdev (id int auto_increment, month int, primary key(id))")
    
    for i in range(len(names)):
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='exp_values' AND column_name='"+names[i]+"'") #check if name is already in table
        tmp=cursor.fetchall()

        if tmp[0][0] == 0:
            cursor.execute("alter table exp_values add "+names[i]+" varchar(4)")
            cursor.execute("alter table exp_values_dev add "+names[i]+" varchar(5)")
            cursor.execute("alter table exp_values_stdev add "+names[i]+" varchar(4)")

    if update == "full":
        for i in range(len(month_id)):
            cursor.execute("select count(*) from exp_values where month = "+str(month_id[i]))
            tmp = cursor.fetchall()
            if tmp[0][0] == 0:
                cursor.execute("insert into exp_values (month) values ("+str(month_id[i])+")")      #creating month if not exists
                cursor.execute("insert into exp_values_dev (month) values ("+str(month_id[i])+")")
                cursor.execute("insert into exp_values_stdev (month) values ("+str(month_id[i])+")")
            for j in range(len(names)):
                cursor.execute("update exp_values set "+names[j]+" = "+str(round(exp_values[i][j],1))+" where month = "+str(month_id[i]))   #writes expectation value
                if not i == len(month_id)-1:
                    cursor.execute("update exp_values_dev set "+names[j]+" = "+str(round(dev[i][j],1))+" where month = "+str(month_id[i]))      #writes deviation of expectation value from actual value
                    if not i == len(month_id)-2:
                        cursor.execute("update exp_values_stdev set "+names[j]+" = "+str(round(stdev[i][j],1))+" where month = "+str(month_id[i+2]))    #writes standard deviations
   
    elif update == "simple":
        cursor.execute("select count(*) from exp_values where month = "+str(month_id[len(month_id)-1]))
        tmp = cursor.fetchall()
        if tmp[0][0] == 0:
            cursor.execute("insert into exp_values (month) values ("+str(month_id[len(month_id)-1])+")")      #creating month if not exists
            for j in range(len(names)):
                cursor.execute("update exp_values set "+names[j]+" = "+str(round(exp_values[len(month_id)-1][j],1))+" where month = "+str(month_id[len(month_id)-1]))
                cursor.execute("update exp_values_dev set "+names[j]+" = "+str(round(dev[len(dev)-1][j],1))+" where month = "+str(month_id[len(month_id)-1]))      #calculates deviation of expectation value from actual value
                cursor.execute("update exp_values_stdev set "+names[j]+" = "+str(round(stdev[len(stdev)-1][j],1))+" where month = "+str(month_id[len(month_id)-1]))
    
    db.commit()




#----------------------------- getting the coffee prize history -----------------------------------------
@st.cache
def get_prizes(names, month_id, func_selected):
    cursor.execute("select active_func from update_status")
    tmp=cursor.fetchall()

    if tmp[0][0] != func_selected:
        update="full"
        write_exp_values_dev(names, month_id, func_selected, update)
        cursor.execute("update update_status set active_func = '"+func_selected+"'")
        db.commit()

    cursor.execute("select * from monthly_coffees")
    coffees=cursor.fetchall()
    cursor.execute("select * from exp_values")
    exp_values=cursor.fetchall()
    social = get_social_score(names, month_id)[1]

    total_data=[]        
    for i in range(len(month_id)):
        temp_km=0
        name_km=""
        temp_hs=100
        name_hs=""
        temp_gn=0
        name_gn=""
        for j in range(len(names)):
            if coffees[j][i+6] > temp_km:
                temp_km = coffees[j][i+6]
                name_km = j
            if coffees[j][i+6] > 0 and coffees[j][i+5] > 0 and abs(float(exp_values[i][j+2])-coffees[j][i+6]) < temp_hs:
                temp_hs = abs(float(exp_values[i][j+2])-coffees[j][i+6])
                name_hs = j
            if social[i][j] > temp_gn:
                temp_gn = social[i][j]
                name_gn = j
        temp=[]
        temp.append(month_id[i])    
        temp.append(name_km)
        temp.append('Kaffeemeister')
        temp.append(40)
        total_data.append(temp)
        temp=[]
        temp.append(month_id[i])    
        temp.append(name_hs)
        temp.append('Hotshot')
        temp.append(25)
        total_data.append(temp)
        temp=[]
        temp.append(month_id[i])    
        temp.append(name_gn)
        temp.append('Genosse')
        temp.append(10)
        total_data.append(temp)
        
    return total_data


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
            total_workdays[j]=total_workdays[j]+workdays[i][j] 	 #getting total workdays per person
        temp1.append(temp)
    
    cursor.execute("select coffees from total_coffees")
    tmp=cursor.fetchall()
    for i in range(len(names)):
        total_p_w.append(round(tmp[i][0]/total_workdays[i],3))
        
    coffees_per_work_day.append(total_p_w)
    coffees_per_work_day.append(temp1)
        
    return coffees_per_work_day


#----------------------------- calculating break sizes per month per person and total --------------------
def get_break_sizes_per_month(names, month_id):
    break_sizes=[]
    break_sizes_total=[]
    for i in range(len(month_id)):
        #break_sizes.append(round(total/len(tmp),2))
        temp=[]

        for j in range(len(names)):
            cursor.execute("select size from break_sizes inner join mbr_"+names[j]+" on break_sizes.id_ext = mbr_"+names[j]+".id_ext where mbr_"+names[j]+".id_ext like '"+str(month_id[i])+"%'")
            tmp=cursor.fetchall()
            #print(tmp)
            total=0
            for k in range(len(tmp)):
                total = total + tmp[k][0]
            if len(tmp) == 0:
                temp.append(0)
            else:
                temp.append(round(total/len(tmp),2))
                
        cursor.execute("select size from break_sizes where id_ext like '"+str(month_id[i])+"%'")
        tmp=cursor.fetchall()
        #print(tmp)
        total=0
        for j in range(len(tmp)):
            total = total + tmp[j][0]
        break_sizes_total.append(round(total/len(tmp),2))
        
        break_sizes.append(temp)
    break_sizes.append(break_sizes_total)
    
    return break_sizes


#----------------------------- calculating variation factor -----------------------------------------------
def write_variation_factor(names, month_id, update):
    #cursor.execute("drop table if exists variation")
    cursor.execute("create table if not exists variation (id int auto_increment, month char(6), primary key(id))")

    for i in range(len(names)):
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='variation' AND column_name='"+names[i]+"'") #check if name is already in table
        tmp=cursor.fetchall()
        if tmp[0][0] == 0:
            cursor.execute("alter table variation add "+names[i]+" varchar(6)")

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
        var_daily=[]

        
        for i in range(delta_days+1):
            
            temp=[]
            id_day = str(curr_date.year)
            if curr_date.month < 10:
                id_day = id_day + "0" + str(curr_date.month)
            else:
                id_day = id_day + str(curr_date.month)
            if curr_date.day < 10:
                id_day = id_day + "0" + str(curr_date.day)
            else:
                id_day = id_day + str(curr_date.day)
            curr_date=curr_date+datetime.timedelta(days=1)
            temp.append(id_day)
            
            var_total = 0
            for j in range(len(names)):
                cursor.execute("select count(*) from mbr_"+names[j]+" where id_ext like '"+str(id_day)+"%'")       
                tmp = cursor.fetchall()

                if tmp[0][0] > 0:
                    var_total += 1                                      #total number of people who drank coffee per day
            
            for j in range(len(names)):
                var = 0
                for k in range(len(names)):                             #permutations of every person for every person who drank coffee per day
                    if j != k:
                        cursor.execute("select count(*) from mbr_"+names[j]+" inner join mbr_"+names[k]+" on mbr_"+names[j]+".id_ext = mbr_"+names[k]+".id_ext where mbr_"+names[j]+".id_ext like '"+str(id_day)+"%'")
                        tmp = cursor.fetchall()

                        if tmp[0][0] > 0:
                            var += 1
                
                if var_total == 0 or var == 0:
                    var = 0
                else:
                    var = (var+1)/(var_total)                                     #ratio of variation
                temp.append(var)
            var_daily.append(temp)

        if update == "full":                                                                                 #updating everything
            for i in range(len(month_id)):
                cursor.execute("select count(*) from variation where month = "+str(month_id[i]))
                tmp=cursor.fetchall()
                if tmp[0][0] == 0:
                    cursor.execute("insert into variation (month) values ('"+str(month_id[i])+"')")

                for j in range(len(names)):
                    temp=0
                    temp1=0
                    for k in range(len(var_daily)):
                        if (var_daily[k][0])[0:6] == month_id[i]:
                            temp=temp + var_daily[k][j+1]
                            temp1 += 1
                    cursor.execute("update variation set "+names[j]+" = "+str(round(temp/temp1,2))+" where month like '"+month_id[i]+"'")
                
        elif update == "simple":                                                                             #updating only last 2 months
            for i in range(2):
                cursor.execute("select count(*) from variation where month = "+str(month_id[len(month_id)-2+i]))
                tmp=cursor.fetchall()
                if tmp[0][0] == 0:
                    cursor.execute("insert into variation (month) values ('"+str(month_id[len(month_id)-2+i])+"')")

                for j in range(len(names)):
                    temp=0
                    temp1=0
                    for k in range(len(var_daily)):
                        if (var_daily[k][0])[0:6] == month_id[len(month_id)-2+i]:
                            temp=temp + var_daily[k][j+1]
                            temp1 += 1
                    cursor.execute("update variation set "+names[j]+" = "+str(round(temp/temp1,2))+" where month like '"+month_id[len(month_id)-2+i]+"'")

    db.commit()



#-------------------------------------- calculating social scores -------------------------------------------------
def get_social_score(names, month_id):
    social_score=[]

    cursor.execute("select * from variation")
    variation = cursor.fetchall()
    cursor.execute("select * from percentage_breaks")
    percentage = cursor.fetchall()
    corrections = holiday_corrections(names, month_id)
    break_sizes = get_break_sizes_per_month(names, month_id)
    #print(corrections)

    for i in range(len(month_id)):
        temp=[]
        for j in range(len(names)):
            temp.append(float(percentage[i+1][j+2])*break_sizes[i][j]*float(variation[i][j+2])*corrections[i][j])       #calculating social score per person per month
        social_score.append(temp)

    total=[]
    for i in range(len(names)):
        temp = 0
        for j in range(len(month_id)):
            temp = temp + social_score[j][i]                                                                            #calculating total social score
        total.append(temp)
        
    max_value = max(total)
    for i in range(len(names)):
        total[i] = round(100*total[i]/max_value,1)                                                                      #normalising on max value

    social_score_total=[]
    social_score_total.append(total)
    social_score_total.append(social_score)
    return social_score_total


#----- calculating all holiday corrections, namely recalculating factor for work days of month and damping factor -----
def holiday_corrections(names, month_id):            
    cursor.execute("select * from holidays where month > 202102")       #getting holidays
    tmp = cursor.fetchall()

    correction_factors=[]
    total=[]
    holidays=[]
    for i in range(len(month_id)):
        total.append(tmp[i][2])
        temp1=[]
        for j in range(len(names)):
            if tmp[i][j+3] == None:
                temp1.append(1)
            else:
                f_damp = (1-((tmp[i][j+3]/tmp[i][2])**2))               #damping function: f = 1 - (d_hol/t_tot)^2
                p_wd = (total[i]-tmp[i][j+3])/total[i]                  #correction for holidays: d_tot-d_hol / d_tot
                temp1.append(f_damp/p_wd)                               #scaling month according to holidays: 1/p_wd; multiplying with damping factor
        correction_factors.append(temp1)
    return correction_factors


def get_cumulated_coffees(names, month_id):
    all_coffees=get_monthly_coffees(names, month_id)[0]         #getting monthly coffees

    coffees_cumulated=[]

    for i in range(len(month_id)):
        coffees=[]
        if i > 0:
            for j in range(len(names)):
                    coffees.append(coffees_cumulated[i-1][j]+all_coffees[i][j])  #adding up monthly coffees
        else:
            for j in range(len(names)):
                  coffees.append(all_coffees[i][j])
        coffees_cumulated.append(coffees)
    return coffees_cumulated



#------------------------ getting functionals from database ------------------
def get_functionals():
	cursor.execute("select name from func_param")
	tmp=cursor.fetchall()

	func_names=[]
	for i in range(len(tmp)):
		func_names.append(tmp[i][0])
 
	return sorted(func_names, key=str.lower)

#------------------------ getting active functional from database ------------------
def get_active_func():
	    cursor.execute("select active_func from update_status")
	    func = cursor.fetchall()
	    return func[0][0]

#------------------------- getting all functional parameters -------------------
def get_parameters():
    cursor.execute("select * from func_param")
    tmp = cursor.fetchall()

    parameters=[]
    for i in range(len(tmp)):
        temp=[]
        for j in range(8):
            temp.append(tmp[i][j+1])
        parameters.append(temp)
    
    return parameters
	
	
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

#-------------------------------------------------------------------------------------------------------------------------------------------------------------
check_update_status()        #------------------------------------------------------- updating database to current day ---------------------------------------
#-------------------------------------------------------------------------------------------------------------------------------------------------------------


