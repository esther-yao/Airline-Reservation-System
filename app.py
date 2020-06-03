#Import Flask Library
from flask import Flask, flash, render_template, request, session, url_for, redirect
import pymysql.cursors
import random
import time
import sys
import datetime
import pandas as pd
import numpy as np
from datetime import date, timedelta
from hashlib import md5

#Initialize the app from Flask
app = Flask(__name__)

#Configure MySQL
conn = pymysql.connect(host='localhost',
                       user='root',
                       password='root',
                       port = 8889,
                       db='project',
                       charset='utf8mb4',
                       cursorclass=pymysql.cursors.DictCursor)



#Define a route to the main page
@app.route('/', methods = ['Get'])
def home_page_get():
    return render_template('index.html')

#Define a route to the main page
@app.route('/', methods = ['POST'])
def home_page_post():
    source_airport = request.form['source_airport']
    dest_airport = request.form['dest_airport'] 
    airport_time = request.form['airport_time'] 

    flight_num = request.form['flight_num'] 
    dep_time = request.form['dep_time'] 
    arri_time = request.form['arri_time'] 
    airline_name = request.form['airline_name']
    # search by airport
    if source_airport and dest_airport and airport_time:
        cursor = conn.cursor()
        query = 'SELECT * FROM flight WHERE departure_airport = %s \
            AND arrival_airport = %s AND DATE(departure_time) = %s\
            AND status = "upcoming"'
        cursor.execute(query, (source_airport, dest_airport, airport_time))
        data = cursor.fetchall()
        cursor.close()
        if data:
            return render_template('index.html', search_results = data)
        else:
            flash('There is no such flight.')
            return render_template('index.html')
#    else:
#        flash('Please fill all required information.')
#        return render_template('index.html')
            
    # check flight status
    if flight_num and dep_time and arri_time:
        cursor = conn.cursor()
        query = 'SELECT * FROM flight WHERE flight_num = %s \
            AND airline_name = %s\
            AND DATE(arrival_time) = %s AND DATE(departure_time) = %s'
        cursor.execute(query, (flight_num, airline_name, arri_time, dep_time))
        data = cursor.fetchall()
        cursor.close() 
        if data:
            return render_template('index.html', check_results = data)
        else:
            flash('There is no such flight.')
            return render_template('index.html')
#    else:
#        flash('Please fill out all required information.')
#        return render_template('index.html')
    return render_template('index.html')

#Define route for login
@app.route('/login', methods = ['GET','POST']) 
def login():
	return render_template('login.html')

@app.route('/loginAuth', methods=['GET', 'POST'])
def loginAuth():
     #grabs information from the forms
    try:
        if request.form["radio"] == "customer":
            username = request.form['username']
            password = request.form['password']
            password = md5(password.encode('utf-8')).hexdigest()

            cursor = conn.cursor()
            query = 'SELECT * FROM customer WHERE email = %s and password = %s'
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
            cursor.close()
            if(data):
                #creates a session for the the user
                #session is a built in
                session['email'] = username
                session['username'] = data['name']
                session['usertype'] = 'customer'
                return redirect(url_for('customer_home'))
            else:
                #returns an error message to the html page
                flash('Username does not exist or wrong password')
                return render_template('login.html')
        if request.form["radio"] == "agent":
            username = request.form['username']
            password = request.form['password']
            password = md5(password.encode('utf-8')).hexdigest()
            cursor = conn.cursor()
            query = 'SELECT * FROM booking_agent WHERE email = %s and password = %s'
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
            cursor.close()
            if(data):
                session['email'] = username
                session['username'] = data['booking_agent_id']
                session['usertype'] = 'agent'
                return redirect(url_for('agent_home'))
            else:
                flash('Username does not exist or wrong password')
                return render_template('login.html')
        if request.form["radio"] == "staff":
            username = request.form['username']
            password = request.form['password']
            password = md5(password.encode('utf-8')).hexdigest()
            cursor = conn.cursor()
            query = 'SELECT * FROM airline_staff WHERE username = %s and password = %s'
            cursor.execute(query, (username, password))
            data = cursor.fetchone()
            cursor.close()
            if(data):
                session['email'] = username
                session['airline'] = data['airline_name']
                session['username'] = data['last_name']
                session['usertype'] = 'staff'
                return redirect(url_for('staff_home'))
            else:
                flash('Username does not exist or wrong password')
                return render_template('login.html')
    except Exception as error:
        flash(str(error))
        return render_template('login.html')

#Define route for register
@app.route('/register')
def register():
	return render_template('register.html')

#Authenticates the register of customers 
@app.route('/register-customer', methods=['GET', 'POST'])
def registerCust():
    try:
        if True:
            email = request.form['email']
            name = request.form['name']
            password = request.form['password']
            password = md5(password.encode('utf-8')).hexdigest()
            building_num = request.form['building_number']
            street = request.form['street']
            city = request.form['city']
            state = request.form['state']
            phone_num = request.form['phone_number']
            passport_num = request.form['passport_number']
            passport_exp = request.form['passport_expiration']
            passport_country = request.form['passport_country']
            dob = request.form['date_of_birth']
            # test to see if the user already exist
            cursor = conn.cursor()
            query = 'SELECT * FROM customer WHERE email = %s'
            cursor.execute(query,(email))
            exist = cursor.fetchone()
            if exist is not None:
                flash('You have already registered.')
                cursor.close()
                return render_template('register-customer.html')
            else:
                query = 'INSERT INTO customer VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(query, (email,name,password,building_num,street,city,\
                                       state,phone_num,passport_num,passport_exp,passport_country,\
                                       dob))
                conn.commit()
                cursor.close()
                session['email'] = email
                session['username'] = name
                session['usertype'] = 'customer'
                return redirect(url_for('customer_home'))
    except Exception as error:
        return render_template('register-customer.html')

#Authenticates the register of agents 
@app.route('/register-agent', methods=['GET', 'POST'])
def registerAgent(): 
    try:
        if True:
            email = request.form['email']
            password = request.form['password']
            password = md5(password.encode('utf-8')).hexdigest()
            agent_ID = request.form['agent_ID']
            # test to see if the user already exist
            cursor = conn.cursor()
            query = 'SELECT * FROM booking_agent WHERE email = %s'
            cursor.execute(query,(email))
            exist = cursor.fetchone()
            if exist is not None:
                flash('You have already registered.')
                cursor.close()
                return render_template('register-agent.html')
            else:
                query = 'INSERT INTO booking_agent VALUES(%s,%s,%s)'
                cursor.execute(query, (email,password,agent_ID))
                conn.commit()
                cursor.close()
                session['email'] = email
                session['username'] = agent_ID
                session['usertype'] = 'agent'
            return redirect(url_for('agent_home'))
    except Exception as error:
        return render_template('register-agent.html')

#Authenticates the register of staff 
@app.route('/register-staff', methods=['GET', 'POST'])
def registerStaff(): 
    try:
        if True:
            username = request.form['username']
            password = request.form['password']
            password = md5(password.encode('utf-8')).hexdigest()
            first_name = request.form['first_name']
            last_name = request.form['last_name']
            dob = request.form['date_of_birth']
            airline_name = request.form['airline_name']            
            # test to see if the user already exist
            cursor = conn.cursor()
            query = 'SELECT * FROM airline_staff WHERE username = %s'
            cursor.execute(query,(username))
            exist = cursor.fetchone()
            cursor.close()           
            if exist is not None:
                flash('You have already registered.')
                return render_template('register-staff.html')
            else:           
                cursor2 = conn.cursor()
                query2 = 'SELECT * FROM airline WHERE airline_name = %s'
                cursor2.execute(query2,(airline_name))
                valid_airline = cursor2.fetchall()
                cursor2.close()
                # if airline_name does not exsist, foreign key constraints are violated.
                # and thus no value will be inserted into the database
                if valid_airline:
                    query = 'INSERT INTO airline_staff VALUES(%s,%s,%s,%s,%s,%s)'
                    cursor = conn.cursor()
                    cursor.execute(query, (username,password,first_name,last_name,dob,airline_name))
                    conn.commit()
                    cursor.close()
                    session['email'] = username
                    session['airline'] = airline_name
                    session['username'] = last_name
                    session['usertype'] = 'staff'
                    return redirect(url_for('staff_home'))
                else:
                    flash('The airline you input does not exist.')
            return render_template('register-staff.html')
    except Exception as error:
        return render_template('register-staff.html')
    
# the home of customer
@app.route('/customer-home', methods=['GET', 'POST'])
def customer_home():
    user_email = session['email']
    user_name = session['username'] 
    start_date = request.form.get('start_date', '')
    end_date = request.form.get('end_date', '')
    if user_email:
        cursor = conn.cursor()
        query = 'SELECT * FROM customer, purchases, ticket NATURAL JOIN flight\
        WHERE customer.email = %s AND customer.email = purchases.customer_email\
        AND purchases.ticket_id = ticket.ticket_id'
        cursor.execute(query, user_email)
        data = cursor.fetchall()
        query2 = 'SELECT customer_email, SUM(price) AS total_spending\
        FROM (purchases NATURAL JOIN ticket) NATURAL JOIN flight WHERE customer_email = %s\
        AND purchase_date BETWEEN %s AND %s GROUP BY customer_email;'
        cursor.execute(query2, (user_email, start_date, end_date))
        spending = cursor.fetchone()
        query3 = 'select customer_email, year(purchase_date) AS year,\
        month(purchase_date) AS month, SUM(price) AS monthly_spending\
        from (purchases NATURAL JOIN ticket) NATURAL JOIN flight\
        WHERE customer_email = %s AND purchase_date BETWEEN %s AND %s\
        group by year(purchase_date), month(purchase_date), customer_email;'
        cursor.execute(query3, (user_email, start_date, end_date))
        mon_spending = cursor.fetchall()
        cursor.close()
        if data:
            return render_template('customer-home.html', search_results = data, \
                                   user_name = user_name, spending = spending, \
                                   start_date = start_date, end_date = end_date, \
                                   mon_spending = mon_spending)
        else:
            flash('You haven\'t booked a ticket yet')
            return render_template('customer-home.html', user_name = user_name)
    return render_template('customer-home.html')

    

@app.route('/purchase', methods=['GET', 'POST'])
def purchase():
    user_email = session['email']
    user_name = session['username']
    user_type = session['usertype']
    if user_type not in ('customer', 'agent'):
        flash('You are NOT authorized to do this operation')
        return render_template('index.html') 
    if request.method == "POST" and 'search' in request.form:
        source_airport = request.form['source_airport']
        dest_airport = request.form['dest_airport'] 
        airport_time = request.form['airport_time']
        if source_airport and dest_airport and airport_time and user_type == 'customer':
            cursor1 = conn.cursor()
            query1 = 'SELECT * FROM flight WHERE departure_airport = %s \
                AND arrival_airport = %s AND DATE(departure_time) = %s\
                AND status = "upcoming"'
            cursor1.execute(query1, (source_airport, dest_airport, airport_time))
            global data1
            data1 = cursor1.fetchall()
            cursor1.close()
            if user_email:
                if data1:
                    return render_template('purchase.html', search_upcoming = data1, user_name = user_name, user_type = user_type)
                else:
                    flash('There is no such flight. Please check for another time.')
                    return render_template('purchase.html',user_name = user_name, user_type = user_type)
        elif source_airport and dest_airport and airport_time and user_type == 'agent':
            global cust_email 
            cust_email = request.form['cust_email']
            cursor2 = conn.cursor()
            query2 = 'SELECT * FROM flight WHERE departure_airport = %s \
                AND arrival_airport = %s AND DATE(departure_time) = %s\
                AND status = "upcoming"'
            cursor2.execute(query2, (source_airport, dest_airport, airport_time))
            global data2
            data2 = cursor2.fetchall()
            cursor2.close()
            if user_email:
                if data2:
                    return render_template('purchase.html', search_upcoming = data2, cus_email = cust_email, user_name = user_name, user_type = user_type)
                else:
                    flash('There is no such flight.')
                    return render_template('purchase.html',user_name = user_name,cus_email = cust_email, user_type = user_type)
        else:
            flash('Please fill out all required information.')
            return render_template('purchase.html',user_name = user_name, user_type = user_type)
    elif request.method == 'POST' and 'purchase' in request.form:
        chosen_ticket = request.form.getlist('checkbox')
        for chosen in chosen_ticket:
            purchase_airline = chosen.split(":")[0]
            purchase_flight_num = chosen.split(":")[1]
            if purchase_airline and purchase_flight_num:
                cursor = conn.cursor()
                # check that this input airline and flight do exist and status is upcoming
                query = 'SELECT * FROM flight WHERE airline_name = %s AND\
                        flight_num = %s AND status="upcoming"'
                cursor.execute(query, (purchase_airline, purchase_flight_num))
                res = cursor.fetchall()
                if len(res) == 0:
                    cursor.close()
                    flash('There is no such upcoming flight. Please check for other time.')
                    return render_template('purchase.html',user_name = user_name, user_type = user_type) 
                # check that the tickets are not already sold out & the flight is not completed yet
                query = "SELECT flight_num, COUNT(ticket_ID)\
                          FROM ticket as T\
                          WHERE airline_name = %s \
                          Group BY airline_name, flight_num\
                          HAVING flight_num = %s \
                          AND COUNT(ticket_id) < (SELECT DISTINCT seats\
                                                  FROM flight NATURAL JOIN airplane\
                                                  WHERE flight.flight_num = T.flight_num\
                                                  AND flight.airline_name = T.airline_name)"
                # two senarios when this query returns empty: 1. all tickets are sold 
                #                                       2. there is no such flight in ticket table yet
                cursor.execute(query, (purchase_airline, purchase_flight_num))
                ticket_left = cursor.fetchall()
                query =  "SELECT *\
                          FROM ticket\
                          WHERE airline_name = %s \
                          AND flight_num = %s "
                cursor.execute(query,(purchase_airline, purchase_flight_num))
                res0 = cursor.fetchall()
                if len(res0) == 0:
                    no_flight_in_ticket = True
                else:
                    no_flight_in_ticket = False
                if ticket_left or no_flight_in_ticket:
                    # make sure the randomly-generated ticket number does not already exist
                    invalid_ticket = True 
                    while invalid_ticket:                
                        ticket_ID = random.randint(1, 99999999)
                        query0 = 'SELECT * FROM ticket WHERE ticket_id = %s AND airline_name = %s AND flight_num = %s'
                        cursor.execute(query0, (ticket_ID, purchase_airline, purchase_flight_num))
                        res = cursor.fetchall()
                        if len(res) == 0:
                            invalid_ticket = False
                    query1 = 'INSERT INTO ticket VALUES(%s,%s,%s)'
                    cursor.execute(query1, (ticket_ID,purchase_airline,purchase_flight_num))
                    conn.commit()
                    if user_type == 'customer':
                        query2 = 'INSERT INTO purchases(ticket_id, customer_email, purchase_date) VALUES(%s,%s,%s)'
                        cursor.execute(query2, (ticket_ID, user_email, time.strftime("%Y-%m-%d")))
                        conn.commit()
                        cursor.close()
                    if user_type == 'agent':
                        query2 = 'SELECT * FROM customer WHERE email = %s'
                        cursor.execute(query2, cust_email)
                        cust_exist = cursor.fetchall()
                        if cust_exist:
                            query3 = 'INSERT INTO purchases VALUES(%s,%s,%s,%s)'
                            cursor.execute(query3,(ticket_ID, cust_email, user_name, time.strftime("%Y-%m-%d")) )
                            conn.commit()
                            cursor.close()
                        else:
                            cursor.close()
                            flash('This customer does not exist. Please Double Check!')
                            return render_template('purchase.html',search_upcoming = data1, user_name = user_name, user_type = user_type)
                else:
                    cursor.close()
                    flash('All tickets for ' + purchase_airline + ' : ' + purchase_flight_num + ' are sold out. Please check for other flights.')              
                    return render_template('purchase.html',search_upcoming = data1, user_name = user_name, user_type = user_type)
            else:
                flash('Please fill out all required information.')
                return render_template('purchase.html',user_name = user_name, user_type = user_type)
        if user_type == 'customer':
            flash('Purchase successful!')
            return redirect(url_for('customer_home'))
        if user_type == 'agent':
            flash('Purchase successful!')
            return redirect(url_for('agent_home'))
    else:    
        return render_template('purchase.html', user_name = user_name, user_type = user_type)


    
# the home of agent
@app.route('/agent-home', methods=['GET', 'POST'])
def agent_home():
    user_email = session['email']
    user_name = session['username']
    start_date = request.form.get('start_date', str(date.today() - timedelta(30)))
    end_date = request.form.get('end_date', str(date.today()))
    if user_email:
        cursor = conn.cursor()
        query = 'SELECT *, booking_agent.email AS agent_email,\
        customer.email AS cus_email FROM booking_agent, customer, purchases, ticket\
        NATURAL JOIN flight WHERE booking_agent.email = %s AND\
        customer.email = purchases.customer_email AND\
        booking_agent.booking_agent_id = purchases.booking_agent_id AND\
        purchases.ticket_id = ticket.ticket_id AND status = "upcoming"'
        cursor.execute(query, user_email)
        data = cursor.fetchall()
        query2 = 'SELECT DISTINCT name, customer_email FROM (booking_agent NATURAL JOIN\
        purchases), customer WHERE customer_email = customer.email AND booking_agent.email = %s'
        cursor.execute(query2, user_email)
        cus_list = cursor.fetchall()
        today = datetime.date.today()
        last_year = today - timedelta(days=365)
        query3 = 'SELECT customer.name, SUM(flight.price)*0.05 AS commission\
        FROM (purchases NATURAL JOIN ticket) NATURAL JOIN flight, customer \
        WHERE purchases.booking_agent_id = %s AND customer.email = purchases.customer_email \
        AND purchases.purchase_date BETWEEN %s AND %s\
        GROUP BY purchases.customer_email ORDER BY commission DESC LIMIT 5'
        cursor.execute(query3, (user_name, last_year, today))
        commission = cursor.fetchall()
        today = datetime.date.today()
        last_6month = today - timedelta(days=180)
        query4 = 'SELECT customer.name, COUNT(purchases.ticket_id) AS num_purchased \
        FROM purchases,customer WHERE purchases.booking_agent_id = %s AND \
        purchases.customer_email = customer.email AND purchases.purchase_date BETWEEN %s\
        AND %s GROUP BY \
        customer.name ORDER BY num_purchased DESC LIMIT 5'
        cursor.execute(query4, (user_name, last_6month, today))
        num_pur = cursor.fetchall()
        query5 = 'SELECT booking_agent_id, SUM(price)*0.05 AS total_com, \
        SUM(price)*0.05/COUNT(purchases.ticket_id) AS avg_com, COUNT(purchases.ticket_id) \
        AS ticket_sales FROM (purchases NATURAL JOIN ticket) NATURAL JOIN flight \
        WHERE booking_agent_id = %s AND purchases.purchase_date BETWEEN %s AND %s \
        GROUP BY booking_agent_id'
        cursor.execute(query5, (user_name, start_date, end_date))
        output = cursor.fetchone()
        cursor.close()
        if data and cus_list:
                return render_template('agent-home.html', cus_list = cus_list,\
                                       search_results = data, user_name = user_name,\
                                       commission = commission, num_pur = num_pur,\
                                       output = output, start_date = start_date, end_date = end_date)
        else:
            flash('You have no booking requests')
            return render_template('agent-home.html', user_name = user_name, commission = commission, num_pur = num_pur)
    return render_template('agent-home.html')

# the home of staff
@app.route('/staff-home', methods=['GET', 'POST'])
def staff_home():
    user_id = session['email']
    user_name = session['username']
    airlinename = session['airline']
    
    # show the upcoming flights for the next 30 days
    cursor = conn.cursor()
    start_date = datetime.date.today()
    end_date = start_date + timedelta(days=30)
    query = "SELECT * FROM flight WHERE airline_name = %s AND\
           DATE(departure_time) >= %s AND DATE(departure_time) <= %s\
           AND status = 'upcoming'"
    cursor.execute(query,(airlinename, start_date,end_date)) 
    upcoming_flight_data = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        # search for flight info
        flight_num = request.form['flight_num'] 
        dep_time = request.form['dep_time'] 
        arri_time = request.form['arri_time'] 
        start_day = request.form['start_date']
        end_day = request.form['end_date']
        dep_airport = request.form['source_airport']
        arr_airport = request.form['arrival_airport']
        cust_flight_num = request.form['cust_flight_num']
        if user_id and flight_num:
            if flight_num and dep_time and arri_time:
                cursor = conn.cursor()
                query = 'SELECT * FROM flight WHERE flight_num = %s \
                    AND DATE(arrival_time) = %s AND DATE(departure_time) = %s'
                cursor.execute(query, (flight_num, arri_time, dep_time))
                data = cursor.fetchall()
                cursor.close() 
                if data:
                    return render_template('staff-home.html', check_results = data, upcoming_flights = upcoming_flight_data,user_name = user_name)
                else:
                    flash('There is no such flight.')
                    return render_template('staff-home.html', upcoming_flights = upcoming_flight_data, user_name = user_name)
        if start_day and end_day and dep_airport and arr_airport:
            cursor = conn.cursor()
            query = 'SELECT * FROM flight WHERE airline_name = %s AND\
            DATE(departure_time) >= %s AND DATE(departure_time) <= %s AND\
            departure_airport = %s AND arrival_airport = %s'
            cursor.execute(query, (airlinename,start_day,end_day,dep_airport,arr_airport))
            all_flights_res = cursor.fetchall()
            cursor.close()
            if all_flights_res:
                return render_template('staff-home.html', all_flights = all_flights_res, upcoming_flights = upcoming_flight_data,user_name = user_name)
            else:
                flash('There is no such flight.')
                return render_template('staff-home.html', upcoming_flights = upcoming_flight_data, user_name = user_name)
        if cust_flight_num:
            # check that the flight exsist
            cursor = conn.cursor()
            query = "SELECT * FROM flight\
                     WHERE airline_name = %s AND flight_num = %s"
            cursor.execute(query, (airlinename,cust_flight_num))
            flight_exist = cursor.fetchall()
            cursor.close()
            if flight_exist:
                cursor = conn.cursor()
                query = "SELECT DISTINCT customer_email, purchase_date\
                         FROM flight NATURAL JOIN ticket, purchases\
                         WHERE airline_name = %s AND flight_num = %s\
                         AND purchases.ticket_id = ticket.ticket_id"
                cursor.execute(query, (airlinename,cust_flight_num))
                cust_list = cursor.fetchall()
                cursor.close()
                if cust_list:
                    return render_template('staff-home.html',cust_lists = cust_list, upcoming_flights = upcoming_flight_data, user_name = user_name)
                else:
                    flash('No customer has booked for this flight yet :(')
                    return render_template('staff-home.html', upcoming_flights = upcoming_flight_data, user_name = user_name)
            else:
                flash('There is no such flight.')
                return render_template('staff-home.html', upcoming_flights = upcoming_flight_data, user_name = user_name)
        return render_template('staff-home.html', upcoming_flights = upcoming_flight_data, user_name = user_name)
    else:
        return render_template('staff-home.html',upcoming_flights = upcoming_flight_data, user_name = user_name)

@app.route('/top-destination', methods=['GET', 'POST'])
def top_destination():
    user_id = session['email']
    user_name = session['username']
    airlinename = session['airline']
    user_type = session['usertype']
    if user_type != 'staff':
        flash('You are NOT authorized to do this operation')
        return render_template('index.html') 

    # show the top desinations
    cursor = conn.cursor()
    start_date = datetime.date.today()
    last_3month = start_date - timedelta(days=90)
    query_dest = "SELECT airport_city, COUNT(customer_email) AS ticket_sold\
    FROM flight, purchases NATURAL JOIN ticket NATURAL JOIN airport\
    WHERE ticket.airline_name = %s AND flight.arrival_airport = airport.airport_name\
    AND flight.airline_name = ticket.airline_name AND ticket.flight_num  = flight.flight_num\
    AND purchase_date >= %s AND purchase_date <= %s \
    GROUP BY airport_city ORDER BY COUNT(airport_city)  DESC LIMIT 3"
    cursor.execute(query_dest, (airlinename, last_3month, start_date))
    dest_mon = cursor.fetchall()
    last_year = start_date - timedelta(days=365)
    cursor.execute(query_dest,(airlinename, last_year,start_date))
    dest_year = cursor.fetchall()
    
    subquery_select = "(SELECT year(departure_time) AS year, month(departure_time) AS month, airport_city, COUNT(customer_email) AS ticket_sold\
    FROM flight, purchases NATURAL JOIN ticket NATURAL JOIN airport\
    WHERE ticket.airline_name = %s AND flight.arrival_airport = airport.airport_name\
    AND flight.airline_name = ticket.airline_name AND ticket.flight_num  = flight.flight_num AND MONTH(departure_time) = %s\
    GROUP BY airport_city, year, month ORDER BY COUNT(airport_city) DESC LIMIT 3)"
    query_select = ''
    for i in range(11):
        query_select += subquery_select+'union all' 
    query_select += subquery_select
    cursor.execute(query_select,(airlinename,'1', airlinename,'2', airlinename,'3',\
                                 airlinename,'4', airlinename,'5', airlinename,'6',\
                                 airlinename,'7', airlinename,'8', airlinename,'9',\
                                 airlinename,'10',airlinename,'11',airlinename,'12'))
    selection = cursor.fetchall()
    cursor.close()
    if request.method == 'POST':
        dest_start = request.form['dest_start']
        dest_end = request.form['dest_end']
        if dest_start and dest_end:
            cursor = conn.cursor()
            cursor.execute(query_dest,(airlinename,dest_start,dest_end))
            dest_default = cursor.fetchall()
            if dest_default:
                    return render_template('top-destination.html', dest_mon = dest_mon,\
                                       dest_year = dest_year,dest_default=dest_default,\
                                           start_date = dest_start, end_date = dest_end,\
                                        result = selection)
            else:
                flash('No tickets sold during this period. Top destinations cannot be found.')
                return render_template('top-destination.html', dest_mon = dest_mon,dest_year = dest_year, result = selection)
        return render_template('top-destination.html', dest_mon = dest_mon,dest_year = dest_year, result = selection)
    else:
        return render_template('top-destination.html', dest_mon = dest_mon,dest_year = dest_year, result = selection)

@app.route('/view-agent', methods=['GET', 'POST'])
def view_active_agent():
    user_id = session['email']
    user_name = session['username']
    airlinename = session['airline']
    user_type = session['usertype']
    if user_type != 'staff':
        flash('You are NOT authorized to do this operation')
        return render_template('index.html') 
    start_date = datetime.date.today()
    last_month = start_date - timedelta(days=30)
    last_year = start_date - timedelta(days=365)
    
    # top agents based on sales
    cursor = conn.cursor()
    query = "SELECT booking_agent.email AS email, COUNT(distinct ticket_id) AS tickets \
    FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent\
    WHERE purchase_date >= %s AND purchase_date <= %s AND airline_name = %s\
    GROUP BY booking_agent.email ORDER BY tickets DESC LIMIT 5"
    cursor.execute(query,(last_month,start_date,airlinename))
    sales_mon = cursor.fetchall()
    cursor.execute(query,(last_year,start_date,airlinename))
    sales_year = cursor.fetchall()
   
    # top agents based on commission
    query2 = "SELECT booking_agent.email AS email, SUM(price)*0.05 AS commission\
    FROM purchases NATURAL JOIN ticket NATURAL JOIN flight NATURAL JOIN booking_agent\
    WHERE purchase_date >= %s AND purchase_date <= %s\
    AND airline_name = %s\
    GROUP BY booking_agent.email ORDER BY commission DESC LIMIT 5"
    cursor.execute(query2, (last_month, start_date, airlinename))
    com_mon = cursor.fetchall()
    cursor.execute(query2, (last_year, start_date, airlinename))
    com_year = cursor.fetchall()   
    cursor.close() 
    
    return render_template('view-agent.html', sales_mon = sales_mon, sales_year = sales_year,\
                           com_mon=com_mon, com_year=com_year)

@app.route('/view-cust', methods=['GET', 'POST'])
def view_active_customer():
    user_id = session['email']
    user_name = session['username']
    airlinename = session['airline']
    user_type = session['usertype']
    if user_type != 'staff':
        flash('You are NOT authorized to do this operation')
        return render_template('index.html') 
    start_date = datetime.date.today()
    last_year = start_date - timedelta(days=365)
    
    # top customer based on sales
    cursor = conn.cursor()
    query = "SELECT customer_email AS email, name, COUNT(ticket_ID) as ticket\
    FROM purchases NATURAL JOIN ticket NATURAL JOIN customer\
    WHERE purchase_date >= %s AND purchase_date <= %s AND airline_name=%s\
    GROUP BY customer_email, name ORDER BY COUNT(ticket_ID) DESC LIMIT 1"
    cursor.execute(query,(last_year,start_date,airlinename))
    cust_sales_y = cursor.fetchone()
    
    query2 = "SELECT * FROM purchases NATURAL JOIN ticket NATURAL JOIN flight\
    WHERE ticket.airline_name = %s\
    AND purchases.customer_email = ( SELECT customer_email AS email\
                                    FROM purchases NATURAL JOIN ticket\
                                    WHERE purchase_date >= %s AND purchase_date <= %s\
                                    AND airline_name= %s\
                                    GROUP BY customer_email ORDER BY COUNT(ticket_ID) DESC LIMIT 1)"    
    cursor.execute(query2, (airlinename, last_year,start_date, airlinename))
    cust_all_flights = cursor.fetchall()
    cursor.close()
    
    return render_template('view-cust.html',cust_sales_y = cust_sales_y, cust_all_flights = cust_all_flights)
    
@app.route('/add-flights', methods=['GET', 'POST'])
def add_flights():
    airlinename = session['airline']
    user_type = session['usertype']
    if user_type == 'staff':
        if request.method == 'POST':
            flight_num = request.form['flightno']
            dep_airport = request.form['depAirport']
            dep_time = request.form['depTime']
            arri_Airport = request.form['arriAirport']
            arri_Time = request.form['arriTime']
            price = request.form['price']
            status = request.form['status']
            planeid = request.form['planeid']
            cursor = conn.cursor()
            query = 'SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s'
            cursor.execute(query,(airlinename, flight_num))
            exist = cursor.fetchone()
            cursor.close()
            if exist is not None:
                flash('Flight Already Exists, please check your input.')
                return render_template('add-flights.html')
            else:
                cursor = conn.cursor()
                query = 'INSERT INTO flight VALUES(%s,%s,%s,%s,%s,%s,%s,%s,%s)'
                cursor.execute(query, (airlinename, flight_num, dep_airport, dep_time, arri_Airport, arri_Time, price, status, planeid))
                conn.commit()
                cursor.close()
                return render_template('add-flights.html')
        else:
            return render_template('add-flights.html')
    else:
        flash('You are NOT authorized to add flights.')
        return render_template('index.html')

@app.route('/update-flights', methods=['GET', 'POST'])
def update_flights():
    airlinename = session['airline']
    user_type = session['usertype']
    if user_type == 'staff':
        if request.method == 'POST':
            flight_num = request.form['flight_num'] 
            dep_time = request.form['dep_time'] 
            arri_time = request.form['arri_time']
            updated_status = request.form['updated-status']
            if flight_num:
                cursor = conn.cursor()
                query_1 = 'UPDATE flight SET status = %s WHERE airline_name = %s \
                AND flight_num = %s AND DATE(arrival_time) = %s AND DATE(departure_time) = %s'
                cursor.execute(query_1, (updated_status, airlinename, flight_num, arri_time, dep_time))
                conn.commit()
                query_2 = 'SELECT * FROM flight WHERE airline_name = %s AND flight_num = %s \
                    AND DATE(arrival_time) = %s AND DATE(departure_time) = %s'
                cursor.execute(query_2, (airlinename, flight_num, arri_time, dep_time))
                data = cursor.fetchall()
                cursor.close()
                if data:
                    return render_template('update-flights.html', check_results = data)
                else:
                    flash('There is no such flight.')
                    return render_template('update-flights.html')
        else:
            return render_template('update-flights.html')
    else:
        flash('You are NOT authorized to update flights.')
        return render_template('index.html')

@app.route('/add-airplane', methods=['GET', 'POST'])
def add_airplane():
    airlinename = session['airline']
    user_type = session['usertype']
    if user_type == 'staff':
        if request.method == 'POST':
            airplane_id = request.form['airplane_id']
            seat = request.form['seat']
            if airplane_id and seat:
                cursor = conn.cursor()
                query = 'SELECT * FROM airplane WHERE airline_name = %s AND\
                        airplane_id = %s AND seats = %s'
                cursor.execute(query,(airlinename, airplane_id, seat))
                exist = cursor.fetchone()
                cursor.close()
                if exist is not None:
                    flash('This airplane already exist!')
                    return render_template('add-airplane.html')
                else:
                   cursor = conn.cursor()
                   query = 'INSERT INTO airplane VALUES(%s,%s,%s)'
                   cursor.execute(query,(airlinename, airplane_id, seat))
                   conn.commit()
                   cursor.close()
                   
                   cursor1 = conn.cursor()
                   query1 = 'SELECT * FROM airplane WHERE airline_name = %s'
                   cursor1.execute(query1,(airlinename))
                   data = cursor1.fetchall()
                   cursor.close()
                   flash('The new plane has been added.')
                   return render_template('confirm-add-airplane.html', results = data)
            else:
                 flash('Please fill all required information.')
                 return render_template('add-airplane.html')
        else:
            return render_template('add-airplane.html')
    else:
        flash('You are NOT authorized to add airplanes.')
        return render_template('index.html') 

@app.route('/add-airport', methods=['GET', 'POST'])
def add_airport():
    user_type = session['usertype']
    if user_type == 'staff':
        if request.method == 'POST':
            airport_name = request.form['airport_name']
            airport_city = request.form['airport_city']
            if airport_name and airport_city:
                cursor = conn.cursor()
                query = 'SELECT * FROM airport WHERE airport_name = %s'
                cursor.execute(query,(airport_name))
                data = cursor.fetchall()
                cursor.close()
                if len(data) == 0:
                    cursor = conn.cursor()
                    query = 'INSERT INTO airport VALUES(%s,%s)'
                    cursor.execute(query,(airport_name,airport_city))
                    conn.commit()
                    cursor.close()
                    flash('The new airport has been added.')
                    return render_template('add-airport.html')
                else:
                    flash('The airport already exists.')
                    return render_template('add-airport.html')
            else:
                flash('Please fill all required information.')
                return render_template('add-airport.html')  
        else:
            return render_template('add-airport.html')                
    else:
        flash('You are NOT authorized to add airports.')
        return render_template('index.html') 
    
@app.route('/profile', methods=['GET', 'POST'])
def profile():
    user_email = session['email']
    user_name = session['username']
    user_type = session['usertype']
    if user_email and user_type == "customer":
        cursor = conn.cursor()
        query = 'SELECT * FROM customer WHERE email = %s'
        cursor.execute(query, user_email)
        data = cursor.fetchone()
        cursor.close()
        if data and request.method == 'POST':
            bd = request.form['bthd']
            pspt = request.form['pspt1']
            psptexp = request.form['psptexp1']
            psptctr = request.form['psptctr1']
            bno = request.form['bno1']
            strt = request.form['strt1']
            city = request.form['city1']
            state = request.form['state1']
            phone = request.form['phoneno1']
            cursor = conn.cursor()
            query = 'UPDATE customer SET customer.building_number = %s,\
                customer.street= %s, customer.city= %s, customer.state= %s,\
                    customer.phone_number= %s, customer.passport_number= %s,\
                        customer.passport_expiration= %s, customer.passport_country= %s,\
                            customer.date_of_birth=%s WHERE customer.email = %s'
            cursor.execute(query, (bno,strt,city,state,phone,pspt,psptexp,psptctr,bd,user_email))
            conn.commit()
            query = 'SELECT * FROM customer WHERE email = %s'
            cursor.execute(query, user_email)
            data = cursor.fetchone()
            cursor.close()
            return render_template('profile.html', search_results = data, user_name = user_name, user_type = user_type)
        else:
            return render_template('profile.html', search_results = data, user_name = user_name, user_type = user_type)
    if user_email and user_type == "agent":
        cursor = conn.cursor()
        query = 'SELECT * FROM booking_agent WHERE email = %s'
        cursor.execute(query, user_email)
        data = cursor.fetchone()
        cursor.close()
        if data:
            return render_template('profile.html', search_results = data, user_name = user_name, user_type = user_type)
    if user_email and user_type == "staff":
        cursor = conn.cursor()
        query = 'SELECT * FROM airline_staff WHERE username = %s'
        cursor.execute(query, user_email)
        data = cursor.fetchone()
        cursor.close()
        if data:
            return render_template('profile.html', search_results = data, user_name = user_name, user_type = user_type)
    return render_template('profile.html', user_name = user_name, user_type = user_type)
        

@app.route('/report', methods=['GET', 'POST'])
def report():
    user_type = session['usertype']
    if user_type != 'staff':
        flash('You are NOT authorized to do this operation')
        return render_template('index.html') 
    user_email = session['email']
    user_name = session['username']
    airlinename = session['airline']
    start_date = request.form.get('start_date', str(date.today().replace(year=date.today().year-1)))
    end_date = request.form.get('end_date', str(date.today()))
    s_date = request.form.get('s_date', str(date.today().replace(year=date.today().year-1)))
    e_date = request.form.get('e_date', str(date.today()))
    if user_email:
        cursor = conn.cursor()
        query = 'select DATE_FORMAT(concat(concat(year(purchase_date), "-" , month(purchase_date)),"-01"), "%%Y-%%m") AS yearmonth,\
            year(purchase_date) AS year , month(purchase_date) AS month,\
            airline_name, COUNT(ticket.ticket_id) AS ticketsales\
            from ((purchases NATURAL JOIN ticket) NATURAL JOIN flight) NATURAL JOIN airline\
            WHERE purchase_date BETWEEN %s AND %s AND airline_name = %s\
            GROUP BY airline_name, yearmonth, year, month;'
        cursor.execute(query,(start_date, end_date, airlinename))
        data = cursor.fetchall()
        query1 = 'select airline_name, SUM(price) * 0.05 AS indirect_rev\
        from (purchases NATURAL JOIN ticket) NATURAL JOIN flight\
        WHERE purchase_date BETWEEN %s AND %s \
        AND airline_name = %s AND booking_agent_id IS NOT NULL\
        GROUP BY airline_name'
        cursor.execute(query1,(s_date, e_date, airlinename))
        indirect = cursor.fetchone()
        query2 = 'select airline_name, SUM(price) * 0.1 AS direct_rev\
        from (purchases NATURAL JOIN ticket) NATURAL JOIN flight\
        WHERE purchase_date BETWEEN %s AND %s \
        AND airline_name = %s AND booking_agent_id IS NULL\
        GROUP BY airline_name'
        cursor.execute(query2,(s_date, e_date, airlinename))
        direct = cursor.fetchone()
        cursor.close()
        end_date_1 = datetime.datetime.strptime(end_date, '%Y-%m-%d')
        end_date_1 = end_date_1.replace(month=end_date_1.month+1)
        idx = pd.date_range(start_date,end_date_1,freq='M').to_period('m')
        years = np.arange(int(start_date[0:4]),int(end_date[0:4])+1,1)
        df = pd.DataFrame(data)
        df["yearmonth"] = pd.to_datetime(df["yearmonth"])
        df = df.set_index('yearmonth')
        df['year']= df['year'].astype(int)
        df.index = df.index.to_period('m')
        o_d = df.loc[df['year'].isin(years)]
        o_d = o_d.reindex(idx,fill_value=np.nan)
        o_d['ticketsales'] = o_d['ticketsales'].fillna(0)
        o_d = o_d.reset_index()
        sales_result =o_d.to_dict('records')
        return render_template('report.html', user_name = user_name, sales = sales_result,\
                               start_date = start_date, end_date = end_date, direct = direct,\
                               indirect = indirect, s_date = s_date, e_date = e_date)
    return render_template('report.html', user_name = user_name)

# log out and return homepage             
@app.route('/logout')
def logout():
	session.pop('email')
	return redirect('/login')
		
app.secret_key = 'some key that you will never guess'
#Run the app on localhost port 5000
#debug = True -> you don't have to restart flask
#for changes to go through, TURN OFF FOR PRODUCTION
if __name__ == "__main__":
	app.run('127.0.0.1', 5000, debug = True)
