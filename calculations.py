import mysql.connector as mysql
import streamlit as st

@st.cache
def get_user_data():
	user_data=[['TK', 'akstr!admin2',1],['PB','akstr!admin2',1],['NV',None,None],['DB',None,None],['FLG','baddragon',None],['SHK',None,None],['TB',None,None],['TT',None,None],['RS',None,None]]
	return user_data

@st.cache
def get_simple_data():
	simple_data=[9, 7, 15, 1879, 720, 66, 9]
	return simple_data

@st.cache
def get_monthly_coffees_total():
	monthly_coffees_total=[75,25,59,88,163,196,197,150,127,206,184,144,163,103,32]
	return monthly_coffees_total

@st.cache
def get_monthly_coffees():
	monthly_coffees = [[19, 9, 16, 19, 29, 31, 32, 30, 14, 41, 39, 34, 37, 24, 10], [15, 6, 6, 20, 29, 20, 24, 25, 29, 22, 32, 30, 35, 18, 12], [13, 6, 12, 16, 25, 35, 28, 37, 31, 27, 36, 30, 22, 14, 0], [10, 3, 7, 12, 27, 36, 37, 15, 22, 44, 10, 6, 4, 7, 1], [18, 1, 18, 21, 34, 35, 35, 26, 21, 43, 43, 27, 36, 22, 9], [0, 0, 0, 0, 19, 27, 23, 9, 5, 16, 22, 17, 26, 17, 0], [0, 0, 0, 0, 0, 12, 18, 8, 5, 13, 2, 0, 0, 0, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 0], [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 3, 0, 0]]
	return monthly_coffees

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
	corr_abs = [[0,229,90,123,248,124,37,0,0],[229,1,75,89,205,83,31,0,0],[90,75,160,64,94,64,22,0,0],[123,89,64,21,133,83,40,0,0],[248,205,94,133,20,130,35,0,0],[124,83,64,83,130,25,18,0,0],[37,31,22,40,35,18,11,0,0],[0,0,0,0,0,0,0,0,0],[0,0,0,0,0,0,0,0,0]]
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
def get_months():
	months = ["Nov '20","Dec '20", "Jan '21", "Feb '21", "Mar '21", "Apr '21", "May '21", "Jun '21", "Jul '21", "Aug '21", "Sep '21", "Oct '21", "Nov '21", "Dec '21", "Jan '22"]
	return months

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
def get_last_breaks():
	last_breaks = [[2022012101, '21.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2021101502, 15.10.2021, 'TK-PB-DB-FLG', '1-1-2-1'],[2022012102, '21.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2022012401, '24.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2022012501, '25.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2022012502, '25.01.2022', 'TK-PB-FLG', '1-1-1'],[2022012601, '26.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2022012602, '26.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2022012701, '27.01.2022', 'TK-PB-FLG-SHK', '1-1-1-1'],[2022012702, '27.01.2022', 'TK-PB', '1-1'],[2022012703, '27.01.2022', 'FLG-SHK', '1-1']]
