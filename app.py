from flask import Flask, render_template, request, redirect, url_for, session,flash, Response,json
from flask_mysqldb import MySQL
import MySQLdb.cursors
import re
from math import pi
import csv
import bcrypt
import base64
import io
import pandas as pd
from numpy import int64
from dotenv import load_dotenv
load_dotenv()
import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Attachment, FileContent, FileName, FileType, Disposition
from sorted_months_weekdays import Month_Sorted_Month, Weekday_Sorted_Week



import datetime
from pandas.core.indexes.api import Int64Index
import shutil
app=Flask(__name__)




app.secret_key = 'a'

  
app.config['MYSQL_HOST'] = 'remotemysql.com'
app.config['MYSQL_USER'] = 'AAoiGL2N1O'
app.config['MYSQL_PASSWORD'] = 'i9adfSBAXZ'
app.config['MYSQL_DB'] = 'AAoiGL2N1O'
mysql = MySQL(app)



month=["January","February","March","April","May","June","July","August","September","October","November","December"]

@app.route('/home')
@app.route('/')
def home():
    try:

        if session['id']:
            session['loggedin']=True
        else:
            session['loggedin']=False
    except:
        session['loggedin']=False
    print("session at home", session)
    return render_template('main.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/contact')
def contact():
    return render_template('contact.html')    


@app.route('/register', methods=['GET', 'POST'])
def register():
    msg=''
    if request.method == 'POST':
        username=request.form['uname']
        password=request.form['pass']
        email=request.form['email']
        session['username'] = username
        session['password']=password
        session['email']=email
        hashed_pr=bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
        session['hash']=hashed_pr
 
        cursor = mysql.connection.cursor()
        cursor.execute('SELECT * FROM user WHERE username = % s', (username, ))
        account=cursor.fetchone()
 
        if account:
            msg="Account already exists"
        else:
            cursor.execute('INSERT INTO user VALUES (NULL, % s, % s, % s)', (username, hashed_pr, email, ))
            mysql.connection.commit()
            msg = 'You have successfully registered !'
            session['loggedin']=False
            print("send grid key is",os.environ.get('SENDGRID_API_KEY'))
            message = Mail(
            from_email='phaneendrakumarm98@gmail.com',
            to_emails=session['email'],
            subject='Registeration Successfull',
            html_content='<h1>FINANCIIO! YOUR EXPENSE TRACKER</h1> <p> Congratulations'+' '+ session['username'] + ' , on successully creating an account with FINANCIIO . To manage your expenses please proceed to the dashboard upon logging in.</p><h2>Please find your account details here: </h2><h3> Username: </h3> <i>'+session['username']+'</i><h3>E-Mail: </h3> <i>'+ session['email'] +'</i><h3>Password: </h3> <i>'+ session['password'] + '</i>')
            try:
                sg = SendGridAPIClient(SENDGRID_API_KEY)
                response = sg.send(message)
                print(response.status_code)
                print(response.body)
                print(response.headers)
            except Exception as e:
                print(e)
            session.pop('username',None)
            session.pop('email',None)
            session.pop('password',None)
            session.pop('hash',None)
            print("session at register else" ,session)
            return render_template('main.html', msg=msg)

    print("session at register final" ,session)
    return render_template('register.html',msg=msg)

@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username=request.form['username']
        password=request.form['password']
        
        
        
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        
        cursor.execute('SELECT password FROM user WHERE username=%s ',(username,))
        h_p = cursor.fetchone()
        if h_p:
            a=bcrypt.checkpw(password.encode('utf-8'),h_p['password'].encode('utf-8'))

            if a == False:
                msg="Password is incorrect"
                print("session at a if" ,session)
                return render_template('main.html', msg=msg)
            else:
                cursor.execute('SELECT * FROM user WHERE username = % s AND password = % s', (username, h_p['password'] ))
                account = cursor.fetchone()
                
                cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    
                session['loggedin'] = True
                session['id'] = account['id']
                session['username'] = account['username']
                session['email']=account['email']
                msg = 'Logged in successfully !'
            
                print("session at login ",session)
                return render_template('main.html', msg=msg)
                    
        else:
            msg="Account doesn't exist"
            print("session at login else" ,session)
            return render_template('main.html', msg=msg)

@app.route('/dashboard', methods=['GET','POST'])
def dashboard():
    wa=''
    print("initial dash session",session)
    month=["January","February","March","April","May","June","July","August","September","October","November","December"]
    
    
    if session['loggedin']:
        session['s_m']=None
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        try:
        
            cursor.execute("SELECT b_month FROM income WHERE id=%s", (session['id'],))
            b_m=cursor.fetchone()
            b_m['b_month']=b_m['b_month'].split('-')[1]
            session['b_m']=b_m['b_month']
            session['s_m']=session['b_m']
            print(b_m)
        except:
            pass
        data=[]
        try:
            cursor.execute('SELECT ex_id,amount,category,date,description FROM expense_a WHERE id = % s AND monthname(date)=%s ORDER BY date DESC', (session['id'], session['b_m'] ))
            data=cursor.fetchall()

        except KeyError:
            pass
       
        try:

            cursor.execute('SELECT bamount FROM income WHERE id = % s', (session['id'], ))
            b=cursor.fetchone()

        except TypeError:
            b={'bamount': 0}
        
        try:

            cursor.execute('SELECT SUM(amount) AS tsum FROM expense_a WHERE id = % s AND monthname(date)=%s', (session['id'], session['b_m']))
            total=cursor.fetchone()
   
        except KeyError:
            total={'tsum':0}

       
      

        cursor.execute("SELECT b_month FROM income WHERE id=%s ", (session['id'],))
        d_m=cursor.fetchall()
        l=[]
        for i in d_m:
            l.append(i['b_month'][5:])
        session['d_m']=l
     

         
        if b:

            session['income']=b['bamount']
            bud=session['income']

        else:
            flash(u"Please Set income First","primary")
            print("session at dashboard else" ,session)
            return render_template('dashboard.html',month=month)
        if data:
            flash(u"Welcome back {}".format(session['username']) , "primary")
            print("session at dashboard if data" ,session)
            return render_template('dashboard.html', data=data,income=bud, total=int(total['tsum']),month=month,d_m=session['d_m'])
        else:
            flash(u"Please Add Expenses","primary")
        if (total['tsum'] == None):
            return render_template('dashboard.html',total=0,income=bud,month=month,d_m=session['d_m'])
        else:
            session['total'] = int(total['tsum'])
        
        return render_template('dashboard.html')
    
    else:
        wa='Please login first'       
        return render_template('main.html', wa=wa)
 


@app.route('/switchmonth/<string:mon>', methods=['GET','POST'])   
def switch_month(mon):
   
    month=["January","February","March","April","May","June","July","August","September","October","November","December"]
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    session['s_m']=mon
    print(" mon is ",mon)
    
    cursor.execute('SELECT ex_id,amount,category,date,description FROM expense_a  WHERE id = % s AND monthname(date)=%s  ORDER BY date DESC  ', (session['id'], mon ))
    data=cursor.fetchall()
    
    cursor.execute('SELECT bamount FROM income WHERE id=%s AND b_month LIKE %s', (session['id'], '2021-'+mon,))
    b=cursor.fetchone()
 
    cursor.execute('SELECT SUM(amount) AS tsum FROM expense_a WHERE id = % s AND monthname(date)=%s', (session['id'], mon))
    total=cursor.fetchone()
    
    cursor.execute("SELECT b_month FROM income WHERE id=%s ", (session['id'],))
    d_m=cursor.fetchall()
    l=[]
    for i in d_m:
        l.append(i['b_month'][5:])
        session['d_m']=l
  
    session['income']=b['bamount']
    bud=session['income']
  
    print("switch month", session)
    try:

        return render_template('dashboard.html',data=data,income=bud, total=int(total['tsum']),month=month,d_m=session['d_m'])
    except:
        return render_template('dashboard.html',data=data,income=bud, total=0,month=month,d_m=session['d_m'])

@app.route('/setincome', methods=['GET','POST'])
def income():
    print("income",session)
    income=request.form['income']
    b_id=session['id']
    b_y = request.form['b_y']
    b_m = request.form['b_m']
    session['b_m']=b_m
    m=b_y+"-"+b_m
    session['s_m']=b_m
    print("month and year is ",b_y,b_m)
    cursor = mysql.connection.cursor()
    cursor.execute('INSERT INTO income VALUES (NULL,%s, %s, %s)', (b_id,income,m, ))
    mysql.connection.commit()
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM income WHERE id = % s AND bamount = % s', (b_id, income ))
    account = cursor.fetchone()
    session['income']=account['bamount']  
    flash(u"income has been set, Now you can proceed to adding expenses","primary")
    print("session at income " ,session)
    #return redirect(url_for('dashboard',income=session['income'], total=0, b_m=session['b_m'],))
    return redirect(url_for('switch_month', mon=session['s_m']))
    
    


@app.route('/updateincome', methods=['POST'])
def updateincome():
    new_income=request.form['updateincome']
    n_y=request.form['b_y']
    n_m=request.form['b_m']
    cursor = mysql.connection.cursor()
    cursor.execute('UPDATE income SET bamount=%s WHERE id=%s AND b_month=%s',(new_income,session['id'],n_y+"-"+n_m))
    mysql.connection.commit()
    flash(u"income Updated","success")
    return redirect(url_for('dashboard'))


@app.route('/aexpense', methods=['POST'])
def expense():
    
    e_id=session['id']
    amount=request.form['am']
    category=request.form['categ']
    date=request.form['date']

    description=request.form['desc']
    cursor = mysql.connection.cursor()
    session['y_r']=date[0:4]

    
  
 
    cursor.execute('SELECT bamount FROM income WHERE id=%s AND b_month LIKE %s',(session['id'],date[0:4]+'-'+month[int(date[5:7])-1]))
    check=cursor.fetchone()
    if check:

        cursor.execute('INSERT INTO expense_a VALUES(NULL,%s,%s,%s,%s,%s)', (e_id,amount,category,date,description, ))
        mysql.connection.commit()
        
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT bamount FROM income WHERE id = % s ', (e_id, ))
    bud=cursor.fetchone()
 
 
    cursor.execute('SELECT ex_id,amount,category,date,description FROM expense_a WHERE id = %s AND monthname(date)=%s AND YEAR(date)=%s', (session['id'], session['b_m'],session['y_r'] ))
    data=cursor.fetchall()
   
  
    cursor.execute('SELECT SUM(amount) AS tsum FROM expense_a WHERE id = %s AND monthname(date)=%s AND YEAR(date)=%s ', (session['id'],session['b_m'],session['y_r'], ))
    total=cursor.fetchone()
   
    session['total']=str(total['tsum'])
   
    
    if total['tsum'] == None:
        total['tsum']=0
 
    bud=session['income']
   
    if check:

        if data:
            if session['s_m']:
                flash(u"Expense has been added","success")
          
                if (total['tsum']>bud):
                    message = Mail(
                        from_email='phaneendrakumarm98@gmail.com',
                        to_emails=session['email'],
                        subject='WARNING: income Exceeded',
                        html_content='<h1>FINANCIIO!! YOUR EXPENSE TRACKER</h1> <h3> Hello'+' '+ session['username'] + '</h3> <p style="color:red"> Your Expense have exceeded your income'+' '+str(session['income'])+ ', For the month of'+' '+session['s_m']+'.</p><br>Your current expenses are worth:'+session['total']+'<p>Kindly update your income or look into your Expenses. ;)</p>'+'<p>Yours Truely,<br>FINANCIIO!</p>')
                try:
                    sg = SendGridAPIClient(SENDGRID_API_KEY)
                    response = sg.send(message)
                    print(response.status_code)
                    print(response.body)
                    print(response.headers)
                except Exception as e:
                    print(e)
                
                return redirect(url_for('switch_month',mon=session['s_m'],data=data,income=int(bud), total=int(total['tsum'])))
            else:
                flash(u"Expense has been added","success")
               
                return redirect(url_for('switch_month',mon=session['b_m'],data=data,income=int(bud), total=int(total['tsum'])))
        
    else:

        flash(u"income not set for the month inputted for the expense","danger")
        return redirect(url_for('dashboard', data=data,income=int(bud), total=int(total['tsum'])))

@app.route('/uexpense/<string:id>', methods=['GET','POST'])
def uexpense(id):

 
    nam=request.form['nam']
    ncateg=request.form['ncateg']
    ndate=request.form['ndate']
    ndesc=request.form['ndesc']
    cursor = mysql.connection.cursor()
    cursor.execute('SELECT bamount FROM income WHERE id=%s AND b_month LIKE %s',(session['id'],ndate[0:4]+'-'+month[int(ndate[5:7])-1]))
    check=cursor.fetchone()
    if check:

        cursor.execute('UPDATE expense_a SET amount=%s, category=%s, date=%s, description=%s WHERE ex_id=%s and id=%s ', (nam,ncateg,ndate,ndesc,id,session['id'], ))
        mysql.connection.commit()
    
 
        try:
            flash(u"Expense Has Been Updated","succcess")
            return redirect(url_for('switch_month',mon=session['s_m']))
        except:

            return redirect(url_for('dashboard'))
    else:
        flash(u"income not set for the inputted month/year","danger")
        return redirect(url_for('switch_month',mon=session['s_m']))


@app.route('/delete', methods=['GET','POST'])
def delete():

    da=request.form['del']
    
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('DELETE FROM expense_a WHERE ex_id = % s ', (da, ))
    mysql.connection.commit()
    cursor.execute('SELECT ex_id,amount,category,date,description FROM expense_a WHERE id = % s', (session['id'], ))
    data=cursor.fetchall()
    
    try:
        return redirect(url_for('switch_month',mon=session['s_m']))
    
    except:
        return redirect(url_for('dashboard'))

@app.route('/dtransactions', methods=['GET','POST'])
def download_transactions():
    conn=None
    cursor=None
    try:
   
        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT ex_id,amount,category,date,description FROM expense_a WHERE id = % s AND monthname(date)=%s', (session['id'], session['s_m'] ))
        result=cursor.fetchall()
       
        output=io.StringIO()
        writer=csv.writer(output)
        head=["Username",session['username']]
        writer.writerow(head)
        line=['ex_id','amount','category','date','description']
        writer.writerow(line)
        for row in result:
           
            line=[str(row['ex_id']),  str(row['amount']) , row['category'], str(row['date']), row['description']]
            writer.writerow(line)
      
        output.seek(0)
      
        
        return Response(output, mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=transaction_report.csv"})

    except Exception as e:
        print(e)
    finally:
        cursor.close()
        
    
        


@app.route('/etransactions',methods=['GET','POST'])
def email_transaction():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT email FROM user WHERE id=%s',(session['id'],))
    em=cursor.fetchone()
    cursor.execute('SELECT ex_id,amount,category,date,description FROM expense_a WHERE id =%s AND monthname(date)=%s ',(session['id'],session['s_m'],))
    result=cursor.fetchall()
    df=pd.DataFrame(result)
    df_update=df.rename(columns={'ex_id':'EX_ID','amount':'Amount','category':'Category','date':'Date','description':'Description'})
    #header=['EX_ID','Amount','Category','Date','Description']
    df_update.to_csv(r'transaction.csv',index=False)

    with open('transaction.csv', 'rb') as f:
        data = f.read()
        f.close()
    message = Mail(
    from_email='phaneendrakumarm98@gmail.com',
    to_emails=em['email'],
    subject='Transaction Report For The Month Of'+'-'+ session['s_m'],
    html_content='Below you will find attached a detailed copy of your transactions for the month of'+' '+session['s_m']
    )

    encoded_file = base64.b64encode(data).decode()
  

    attachedFile = Attachment(
        FileContent(encoded_file),
        FileName('transaction'+'_'+session['s_m']+'.csv'),
        FileType('transaction/csv'),
        Disposition('attachment')
    )
    message.attachment = attachedFile

    sg = SendGridAPIClient(SENDGRID_API_KEY)
    response = sg.send(message)
    print(response.status_code, response.body, response.headers)
    flash(u"E-mail has been sent","success")
    return redirect(url_for('dashboard'))


@app.route('/statistics', methods=['GET','POST'])
def statistics():
    print("stat session",session)
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT category,amount FROM expense_a WHERE id = % s AND monthname(date)=%s', (session['id'], session['s_m'] ))
    catam = (cursor.fetchall())
    print("catm is ",catam)
    cursor.execute('SELECT monthname(date) as m,sum(amount) as a from expense_a WHERE id=%s group by monthname(date) order by monthname(date)DESC  ', (session['id'],))
    a_month=cursor.fetchall()
  
    s_r=[]
    s_c=[]
    l={}
    fc=[]
    for i in a_month:
        s_r.append(i['m'])
        s_c.append(int(i['a']))
    c=Month_Sorted_Month(s_r)
    for i in range(0,len(a_month)):
        d=list(a_month[i].values())
        l[d[0]]=d[1]
    for j in c:
        fc.append(int(l[j]))
    print(s_r,s_c,c,fc)
    x={}
    for i in catam:
   
        if(i["category"] in x):
            x[i["category"]]+=i["amount"]
        else:
            x[i["category"]] = i["amount"]
  
    print(x)
    fruits = list(x.keys())
    counts = list(x.values())
    
    session['statnotavail']=False
    
    print(fruits,counts)
    
    if(catam):
        return render_template('stats.html',row=fruits,col=counts,s_r=c,s_c=fc)
        print(session)
    else:
        print(session)
        session['statnotavail']=True
        no="No expenses available to generate graphical preview"
        return render_template('stats.html',no=no)


@app.route('/logout')
def logout():
   
   session.pop('id', None)
   session.pop('username', None)
   session.pop('income', None)
   session.pop('total', None)
   session.pop('mnd', None)
   session.pop('mxd', None)
   session.pop('new_user', None)
   session.pop('b_m', None)
   session.pop('d_m', None)
   session.pop("s_m", None)
   session.pop("statnotavail",None)
   session.pop("row",None)
   session.pop("column",None)
 
   session['loggedin']=False
   print(session)
   msg='You have been logged out successfully'

   return render_template('main.html', msg=msg)


PORT=os.environ.get('PORT') or '8080'
if __name__ == '__main__':
    app.run(host='0.0.0.0',port=PORT,debug=False)