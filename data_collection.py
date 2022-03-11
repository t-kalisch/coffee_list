import math
import re
import mysql.connector as mysql
#import csv
from calculations import *

#db = init_connection()
#cursor = db.cursor()

status=""

work_days=[21, 20, 19, 20, 23, 20, 19, 21, 22, 22, 22, 21, 21, 21, 21, 20, 23, 19, 21, 20, 21, 23, 22, 20, 21, 19, 22, 20, 23, 18, 20, 21, 21, 23, 21, 21, 21, 17]  #work days until december 2023


            
    #---------------------- deleting a break by knowing id_ext ----------------
def clear_one_break(del_id, test):
    db = init_connection()
    cursor = db.cursor(buffered=True)
    
    if del_id == "":
         st.warning("Please enter a break ID")
    else:
        cursor.execute("SELECT * FROM breaks WHERE id_ext='"+del_id+"'")
        del_break=cursor.fetchall()

        if del_break != []:
            cursor.execute("DELETE FROM breaks WHERE id_ext='"+del_id+"'")
            cursor.execute("update update_status set last_break = timestamp(subdate(current_date, 1))")
            st.success("Break "+del_id+" has successfully been deleted.")
        else:
           st.error("Break "+del_id+" does not exist, therefore nothing was deleted.")
		
    db.commit()
    db.close()

	 #---------------------- deleting a coffee from a break ----------------
def delete_one_coffee(id_ext, name):
	db = init_connection()
	cursor = db.cursor(buffered=True)
	
	cursor.execute("select persons, coffees from drinkers where id_ext = '"+id_ext+"'")
	tmp=cursor.fetchall()
	persons = tmp[0][0].split("-")
	coffees = tmp[0][1].split("-")

	for i in range(len(persons)):
		if persons[i] == name.upper():
			coffees[i] = int(coffees[i]) - 1
			cursor.execute("update mbr_"+name.upper()+" set n_coffees = "+str(coffees[i])+" where id_ext = '"+id_ext+"'")
		if coffees[i] == 0:
			cursor.execute("delete from mbr_"+name.upper()+" where id_ext = '"+id_ext+"'")

	persons_new = ""
	coffees_new = ""
	for i in range(len(persons)):
		if coffees[i] == 0:
			pass
		else:
			if persons_new == "":
				persons_new += persons[i]
				coffees_new += str(coffees[i])
			else:
				persons_new = persons_new + "-" + persons[i]
				coffees_new = coffees_new + "-" + str(coffees[i])
	if persons_new == "":
		cursor.execute("DELETE FROM breaks WHERE id_ext='"+id_ext+"'")
	else:
		cursor.execute("update drinkers set persons = '"+persons_new+"' where id_ext = '"+id_ext+"'")
		cursor.execute("update drinkers set coffees = '"+coffees_new+"' where id_ext = '"+id_ext+"'")
	db.commit()
	db.close()
	
	
#----------------------- holiday input ----------------------------------------
def submit_holidays(name, month_inp, year_inp, days_inp):
    db = init_connection()
    cursor = db.cursor(buffered=True)
    cursor.execute("create table if not exists holidays (id int auto_increment, month int, work_days int, primary key(id))")            #creating holidays table
    
    if int(month_inp) > 12 or int(year_inp) < 2020:
        st.error("Invalid date: The date you entered does not exist or lies before the age of the coffee list!")
    else:
        if int(month_inp) < 10:
            month_id = int(year_inp+"0"+month_inp)
        else:
            month_id = int(year_inp+month_inp)
    
        cursor.execute("SELECT COUNT(*) FROM INFORMATION_SCHEMA.COLUMNS WHERE TABLE_SCHEMA='coffee_list' AND TABLE_NAME='holidays' AND column_name='"+name.upper()+"'")     #check if name already exists
        tmp = cursor.fetchall()
        if tmp[0][0] == 0:
            cursor.execute("alter table holidays add "+name.upper()+" int")     #adding name if doesn't exist yet

        month_id_all = get_months(datetime.date(2020,11,1))[1]
        for i in range(len(month_id_all)):
            cursor.execute("select count(*) from holidays where month like "+str(month_id_all[i]))
            tmp = cursor.fetchall()
            if tmp[0][0] == 0:
                cursor.execute("insert into holidays (month, work_days) values (%s, %s)", (month_id_all[i], work_days[i]))

        cursor.execute("select "+name.upper()+" from holidays where month = "+str(month_id))
        tmp=cursor.fetchall()
        if tmp[0][0] == None:
            cursor.execute("update holidays set "+name.upper()+" = "+str(int(days_inp))+" where month like "+str(month_id))
        else:
            cursor.execute("update holidays set "+name.upper()+" = "+str(int(days_inp)+tmp[0][0])+" where month like "+str(month_id))
        st.success("The holidays have successfully been saved.")

    db.commit()
    db.close()

    #------------------- Changing a user's profile data --------------------------------------
def change_profile_data(user_old, user, user_pw, admin_status):
	db = init_connection()
	cursor = db.cursor(buffered=True)
	if user != "":
		#cursor.execute("update members set name = '"+user+"' where name = '"+user_old+"'")
		#cursor.execute("RENAME TABLE mbr_"+user_old.upper()+" TO mbr_"+user.upper())
		user_old = user
	if user_pw != "":
		cursor.execute("update members set password = '"+user_pw+"' where name = '"+user_old+"'")
	if admin_status != "":
		if admin_status == "User":
			cursor.execute("update members set admin = null where name = '"+user_old+"'")
		elif admin_status == "Admin":
			cursor.execute("update members set admin = 1 where name = '"+user_old+"'")
	st.success("The requested profile data have successfully been changed")
	db.commit()
	db.close()
	return True



def add_break_sizes():                                                      # inserting values of all breaks into break_sizes
    db = init_connection()
    cursor = db.cursor(buffered=True)
    cursor.execute("use coffee_list")

    cursor.execute("Drop table if exists break_sizes")
    cursor.execute("Create table if not exists break_sizes (id int auto_increment, id_ext char(10), size int, primary key(id), CONSTRAINT fk_breaksize_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")

    cursor.execute("select id_ext from drinkers")
    tmp = cursor.fetchall()
    for i in range(len(tmp)):
        cursor.execute("Select id_ext, coffees from drinkers where id_ext = '"+tmp[i][0]+"'")
        tmp1 = cursor.fetchall()
        
        cursor.execute("Insert into break_sizes (id_ext, size) values (%s, %s)",(tmp1[0][0],len(tmp1[0][1].split("-"))))

    db.commit()
    db.close()

    
