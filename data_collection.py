import math
import re
import mysql.connector as mysql
#import csv
from calculations import *


db = mysql.connect(user='PBTK', password='akstr!admin2',
		host='212.227.72.95',
		database='coffee_list')
cursor=db.cursor(buffered=True)


status=""

work_days=[21, 20, 19, 20, 23, 20, 19, 21, 22, 22, 22, 21, 21, 21, 21, 20, 23, 19, 21, 20, 21, 23, 22, 20, 21, 19, 22, 20, 23, 18, 20, 21, 21, 23, 21, 21, 21, 17]  #work days until december 2023

#--------------------------- main function to call from different script
def write_break(coffee_break,breaklen):
    id_ext=""
    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
                              host='127.0.0.1',
                              database='coffee_list')
    cursor=db.cursor(buffered=True)
    
    cursor.execute("use coffee_list")

    cursor.execute("create table if not exists breaks (id int auto_increment, id_ext char(10), day int, month int, year int,  primary key(id), unique key(id_ext))")                 #creatingbreaks table
    cursor.execute("create table if not exists drinkers (id int auto_increment, id_ext char(10), persons varchar(30), coffees varchar(30), primary key(id), CONSTRAINT fk_drinkers_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")   #creating drinkers table
    cursor.execute("create table if not exists members (id int auto_increment, name varchar(3), password varchar(20), primary key(id))")
    cursor.execute("create table if not exists update_status (id int auto_increment, object varchar(5), id_ext int, content varchar(1000), primary key(id))")
    
       #---------------------- creating the extended id -----------------------
    id_ext=""
    date_break=coffee_break[0]
    day_break=str(date_break[0])
    month_break=str(date_break[1])
    if(len(month_break)==1):          #adding "0" if month has 1 digit
        month_break="0"+str(date_break[1])
    if(len(day_break)==1):            #adding "0" if day has 1 digit
        day_break="0"+str(date_break[0])
    id_ext=str(date_break[2])+month_break+day_break
    
    total=0
    cursor.execute("SELECT id_ext FROM breaks WHERE id_ext like '"+id_ext+"%'")    #searching for breaks of the same day as enterd break
    ids=cursor.fetchall()
    ids=list(ids)
    for i in range(len(ids)):
        ids[i]=int(ids[i][0])
    if len(ids)==0:
        id_ext=id_ext+"01"
    else:
        id_ext=str(max(ids)+1)

    temp1=""                                    #converting coffee_break into a list of strings for instertion into database
    temp2=""
    coffee_break_str=[]
    coffee_break_str.append(date_break)

    for i in range(len(coffee_break[1])):
        temp1=temp1+str(coffee_break[1][i])
        temp2=temp2+str(coffee_break[2][i])
        if i<(len(coffee_break[1])-1):
            temp1=temp1+"-"
            temp2=temp2+"-"
    coffee_break_str.append(temp1)
    coffee_break_str.append(temp2)
    
    cursor.execute("INSERT INTO breaks (id_ext, day, month, year) VALUES ("+id_ext+","+str(date_break[0])+","+str(date_break[1])+","+str(date_break[2])+")")
    cursor.execute("INSERT INTO drinkers (id_ext, persons, coffees) VALUES ("+id_ext+",'"+str(coffee_break_str[1])+"','"+str(coffee_break_str[2])+"')")
    #cursor.execute("select * from drinkers")
    #temp=cursor.fetchall()
    #for row in temp:
    #    print(row)
    print("Coffee break saved!")
    print(id_ext+", "+str(coffee_break_str[1])+", "+str(coffee_break_str[2]))

    #--------------------- writing into each person's list -------------------
    persons=coffee_break[1]
    coffees=coffee_break[2]

    for i in range(len(persons)):
        cursor.execute("create table if not exists mbr_"+persons[i]+" (id_ext char(10), n_coffees int, primary key(id_ext), CONSTRAINT fk_member_"+persons[i]+"_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")     #creating a table for each individual person
        cursor.execute("insert into mbr_"+persons[i]+" (id_ext, n_coffees) values (%s, %s)", (id_ext, coffees[i]))              #writes break id and coffees into personal table
        cursor.execute("select count(*) from members where name='"+persons[i]+"'")                                                #checks if person is already written in members table
        tmp=cursor.fetchone()
        if tmp[0] == 0:
            cursor.execute("insert into members (name) values ('"+str(persons[i])+"')")                                             #adding person to members table
            cursor.execute("alter table holidays add "+persons[i]+" varchar(6)")                                                    #adding person to holidays table
            update_database()


                           
    #---------------------- writing break size table ------------------------
    cursor.execute("Create table if not exists break_sizes (id int auto_increment, id_ext char(10), size int, primary key(id), CONSTRAINT fk_breaksize_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")
    cursor.execute("Insert into break_sizes (id_ext, size) values (%s, %s)", (id_ext, len(persons)))

    #---------------------- writing break length table ------------------------
    cursor.execute("create table if not exists break_lengths (id int auto_increment, id_ext char(10), length time(6), primary key(id), CONSTRAINT fk_breaklen_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")
    cursor.execute("insert into break_lengths (id_ext, length) values (%s, %s)",(id_ext,breaklen))



    
    db.commit()
    #cursor.execute("select * from drinkers")
    #databases=cursor.fetchall()
    #for row in databases:
    #    print(row)
    #print("--------------------")
    db.close()


    #---------------------- checking for user and password --------------------

def safety_check(command):
    sfycheck_fld = Tk()
    sfycheck_fld.geometry("400x100")
    sfycheck_fld.title("Safety Check")
    frame_sfycheck = LabelFrame(sfycheck_fld, width= 400, height=200, bd = 0)
    frame_sfycheck.place (x=0, y= 10)
    header_sfycheck=Label(frame_sfycheck, text="Please enter your user name and password:", fg="red", font=("Helvetica", 14))
    header_sfycheck.place(x=20, y = 0)
    user_inp=ttk.Entry(frame_sfycheck, text="", width=4)
    user_inp.place(x=120, y = 30)
    pw_inp=ttk.Entry(frame_sfycheck, show="*", text="", width=8)
    pw_inp.place(x=161, y = 30)
    conf_sfycheck=ttk.Button(frame_sfycheck, text="Login", command=lambda: user_pw_database_search(sfycheck_fld,user_inp,pw_inp,command) )
    conf_sfycheck.place(x=119, y= 60)
    sfycheck_fld.bind('<Return>', (lambda event: user_pw_database_search(sfycheck_fld,user_inp,pw_inp,command)))

def user_pw_database_search(sfycheck_fld,user_inp,pw_inp,status):
    user_inp=str(user_inp.get()).upper()
    pw_inp=str(pw_inp.get())
    
    #print(user_inp, pw_inp)

    db = mysql.connect(user='PBTK', password='akstr!admin2', #connecting to mysql
                              host='127.0.0.1',
                              database='coffee_list')
    cursor=db.cursor(buffered=True)
    
    cursor.execute("use coffee_list")
    cursor.execute("SELECT * FROM members WHERE name='"+user_inp+"'")
    user_data=""
    user_data=cursor.fetchall()
    #print(user_data)
    if user_data==[]:
        sfycheck_fld.destroy()
        messagebox.showinfo("Log-In status", "No such User!")
        
    else:
        user_data_check=list(user_data[0])
    
        #print(user_data)
        #print(pw_inp)     
        
        if user_data_check[2]==pw_inp:
            sfycheck_fld.destroy()

            if status=="delete_one":                            # to delete one break
                clear_ONE_break()
            elif status=="delete_db":                           # to clear the whole database
                if user_data_check[3]==1:
                    answer = messagebox.askokcancel("Confirmation", "Are you REALLY sure to clear the database?",icon="warning")
                    if answer:
                        answer = messagebox.askokcancel("Confirmation", "Final warning!",icon="warning")
                        if answer:
                            #clear_database()
                            messagebox.showinfo("Deletion status", "The database has successfully been cleared.")
                else:
                    messagebox.showerror("Access denied", "You do not have admin rights. Please contact your system administrator.")
            elif status=="input_holiday":
                input_holiday(user_inp)
        else:
            sfycheck_fld.destroy()
            messagebox.showinfo("Log-In status", "Wrong Password!")

        return
            
    #---------------------- deleting a break by knowing id_ext ----------------
def clear_one_break(del_id):

    cursor.execute("SELECT * FROM breaks WHERE id_ext='"+del_id+"'")
    del_break=cursor.fetchall()

    if del_break != []:
        cursor.execute("DELETE FROM breaks WHERE id_ext='"+del_ID+"'")
        st.success("Break "+del_id+" has successfully been deleted.")
    else:
        st.error("Break "+del_id+" does not exist, therefore nothing was deleted.")
		
    db.commit()

#----------------------- holiday input ----------------------------------------
def submit_holidays(name, month_inp, year_inp, days_inp):
    cursor.execute("create table if not exists holidays (id int auto_increment, month int, work_days int, primary key(id))")            #creating holidays table
    
    if int(month_inp) > 12 or int(year_inp) < 2020:
        st.warning("Invalid date: The date you entered does not exist or lies before the age of the coffee list!")
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

    #------------------- Changing a user's profile data --------------------------------------
def change_profile_data(user_old, user, user_pw, admin_status):
	st.write(admin_status)
	if user != "":
		#cursor.execute("update members set name = "+user+" where name = '"+user_old+"'")
		#cursor.execute("RENAME TABLE mbr_"+user_old.upper()+" TO mbr_"+user.upper())
		user_old = user
	if user_pw != "":
		cursor.execute("update members set password = "+user_pw+" where name = '"+user_old+"'")
	if admin_status != "":
		if admin_status == "User":
			cursor.execute("update members set admin = null where name = '"+user_old+"'")
			st.write("updated to user")
		elif admin_status == "Admin":
			cursor.execute("update members set admin = 1 where name = '"+user_old+"'")
			st.write("updated to admin")
	st.success("The selected profile data have successfully been changed")
	db.commit()
	return True




    #------------------- deleting the whole database --------------------------------------
def clear_database():
    db = mysql.connect(user='PBTK', password='akstr!admin2',
                              host='127.0.0.1',
                              database='coffee_list')
    cursor=db.cursor()

    cursor.execute("use coffee_list")
    cursor.execute("SHOW tables")
    databases=cursor.fetchall()
    #print(databases)
    #print("yes")
    cursor.execute("select name from members")
    mbrs=cursor.fetchall()
    mbrs=list(mbrs)
    for i in range(len(mbrs)):
        cursor.execute("drop table if exists mbr_"+mbrs[i][0])
    
    cursor.execute("drop table if exists break_ID,breaks, drinkers, members, total_coffees, break_lengths")
    cursor.execute("SHOW tables")
    databases=cursor.fetchall()
    #print(databases)
    db.commit()
    db.close()

   
    #------------------------- reading breaks from 2021 into database ---------------------
def breaks_2021():
    db = mysql.connect(user='PBTK', password='akstr!admin2',
                              host='127.0.0.1',
                              database='coffee_list')
    cursor=db.cursor()

    cursor.execute("use coffee_list")

    inp = []
    file = open("breaks_2021.txt","r")
    lines = file.readlines()
    file.close()
    persons=['TK','PB','NV','DB','FLG','SHK','TB']
    for line in lines:
        #print(line)
        #inp.append(list(map(int,line.split())))
        inp=list(map(int,line.split()))                     #getting lines from input file
        
        cursor.execute("SELECT * FROM breaks WHERE id_ext='"+str(inp[0])+"'")   #check if break is already in database
        exists=""
        exists=cursor.fetchall()
        if exists==[]:
            #print(str(inp[0])+","+str(inp[0])[0:4]+","+str(inp[0])[4:6]+","+str(inp[0])[6:8])
            
            temp1=""
            temp2=""
            temp3=0
            temp4=0
            for j in range(7):                              #checking how many persons took part in break
                if inp[j+1]!=0:
                    temp3+=1

            cursor.execute("insert into breaks (id_ext, year, month, day) VALUES ("+str(inp[0])+","+str(inp[0])[0:4]+","+str(inp[0])[4:6]+","+str(inp[0])[6:8]+")")
            
            for j in range(7):                              #creating string for input into drinkers table
                if inp[j+1]!=0:
                    temp1+=persons[j]
                    temp2+=str(inp[j+1])
                    temp4+=1
                    if temp4 < temp3:
                        temp1+="-"
                        temp2+="-"
                    print(inp)
                    cursor.execute("create table if not exists mbr_"+persons[j]+" (id_ext char(10), n_coffees int, primary key(id_ext), CONSTRAINT fk_member_"+persons[j]+"_break_ID_ext FOREIGN KEY(id_ext) REFERENCES breaks(id_ext) ON DELETE CASCADE)")
                    cursor.execute("insert into mbr_"+persons[j]+" (id_ext, n_coffees) values (%s, %s)", (inp[0], inp[j+1]))
            
            cursor.execute("INSERT INTO drinkers (id_ext, persons, coffees) VALUES ("+str(inp[0])+",'"+temp1+"','"+temp2+"')")

    db.commit()
    db.close()

def add_break_sizes():                                                      # inserting values of all breaks into break_sizes
    db = mysql.connect(user='PBTK', password='akstr!admin2',
                              host='127.0.0.1',
                              database='coffee_list')
    cursor=db.cursor()
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

    
