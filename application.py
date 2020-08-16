from flask import Flask, render_template, request
import time
import pyodbc
from flask_caching import Cache
import geopy
import geocoder
import json
import geopy.distance
from werkzeug.exceptions import NotFound, Unauthorized, Forbidden, RequestTimeout, HTTPException
import redis
import random


app = Flask(__name__, template_folder="templates")
myHostname = ""
myPassword = ""
r = redis.StrictRedis(host=myHostname, port=6380, password=myPassword, ssl=True)


server = ''
database = ''
username = ''
password = ''
 
@app.route("/")
def hello():
     print("Hello There.....")
     return render_template('home.html')

@app.route("/select")
def select():
     return render_template('select.html')

@app.route("/selectdata")
def selectdata():
     mag =float(request.args.get('mag'))
     count = int(request.args.get('count'))
     start = time.time()
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     r = redis.StrictRedis(host=myHostname, port=6380, password=myPassword, ssl=True)
     if conn:
          for i in range(count):
               stmt = "Select mag, place from Earthquake where mag >= ?"
               cur = conn.cursor()
               cur.execute(stmt,(mag))
               rows = cur.fetchall()
               r.set('key','Hello!, The cache is working with Python!')
               #print("Query Executed Successfully")
               conn.commit()
          
          cur.close()
         

     end = time.time()
     timediff = end - start
     return render_template('select.html', elapsetime=timediff, rows=rows)

@app.route("/sc")
def sc():
     return render_template('selectcached.html')

@app.route("/selectcached")
def selectcached():
     mag =float(request.args.get('mag'))
     count = int(request.args.get('count'))
     start = time.time()
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
            for i in range(count):
              data = r.get('key')
     end = time.time()
     timediff = end - start
     return render_template('selectcached.html', elapsetime=timediff,rows=data)

@app.route("/givendistance")
def givendistance():
    return render_template('quakes_within_distance.html')

@app.route('/quakes_within_distance',methods=['GET'])
def quakes_within_distance():
    distance = request.args.get('distance', 500, type=float)
    city = request.args.get('city', 'arlington')
    g = geocoder.osm(city).json
    target_coordinates = (g['lat'], g['lng'])
    start = time.time()
    conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
    if conn:
        stmt = "SELECT latitude,longitude FROM Earthquake"
        cur = conn.cursor()
        cur.execute(stmt)
        rows = cur.fetchall()
        conn.commit()
        count = 0
        cols = []
        for result in rows:
            current_coordinates = (result[0], result[1])
            if geopy.distance.geodesic(current_coordinates, target_coordinates).km < distance:
                stmt1 = "SELECT * FROM Earthquake where latitude = ? and longitude = ?"
                cur1 = conn.cursor()
                cur1.execute(stmt1,(result[0], result[1]))
                que = cur1.fetchone()
                cols.append(que)
                conn.commit()
                count += 1
        cur.close()
        cur1.close()
        

        end = time.time()
        timediff = end - start
    return render_template('quakes_within_distance.html',count=count, cols=cols,elapsetime=timediff)


@app.route("/nstrange")
def nstrange():
     
     range1 = int(request.args.get('range1'))
     range2 = int(request.args.get('range2'))
     start = time.time()
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          stmt = "Select * from EQ1,EQ2 where EQ1.id=EQ2.id and EQ2.nst>=? and EQ2.nst<=?"
          cur = conn.cursor()
          cur.execute(stmt,(range1,range2))
          rows = cur.fetchall()
          conn.commit()
          cur.close()
          conn.close()
         
     end = time.time()
     timediff = end - start
     return render_template('home.html', elapsetime=timediff, rows=rows)

@app.route("/rn")
def rn():
    return render_template('randomnst.html')

@app.route("/randomnst")
def randomnst():
     
     range1 = int(request.args.get('range1'))
     range2 = int(request.args.get('range2'))
     nstnumber = random.randint(range1, range2)
     start = time.time()
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          stmt = "Select * from EQ1,EQ2 where EQ1.id=EQ2.id and EQ2.nst=?"
          cur = conn.cursor()
          cur.execute(stmt,(nstnumber))
          rows = cur.fetchall()
          conn.commit()
          cur.close()
          conn.close()
         
     end = time.time()
     timediff = end - start
     return render_template('randomnst.html', elapsetime=timediff, rows=rows, nstnumber=nstnumber)

@app.route("/loop")
def loop():
    return render_template('loopN.html')

@app.route("/loopN")
def loopN():
     
     range1 = int(request.args.get('range1'))
     range2 = int(request.args.get('range2'))
     loopcount = int(request.args.get('lcount'))
     diff_arr = []
     random_arr = []
     result = []
     start = time.time()
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          for k in range(loopcount):
               starteach = time.time()
               nstnumber = random.randint(range1, range2)
               random_arr.append(nstnumber)
               stmt = "Select EQ2.nst, EQ1.latitude, EQ1.longitude, EQ1.place, EQ2.mag, EQ2.id from EQ1,EQ2 where EQ1.id=EQ2.id and EQ2.nst=?"
               cur = conn.cursor()
               cur.execute(stmt,(nstnumber))
               rows = cur.fetchall()
               result.append(rows)
               conn.commit()
               endeach = time.time()
               diff = endeach - starteach
               diff_arr.append(diff)
          cur.close()
          conn.close()
         
     end = time.time()
     timediff = end - start
     return render_template('loopN.html', elapsetime=timediff, result=result, nstnumber=nstnumber, diff_arr=diff_arr, random_arr=random_arr)

@app.route("/pie")
def pie():
    return render_template('piehighchart.html')

@app.route("/piechart")
def piechart():
     
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          count01=0
          count12=0
          count23=0
          count34=0
          count45=0
          rows = []
          stmt = "select mag from Earthquake order by mag desc"
          cur = conn.cursor()
          cur.execute(stmt)
          rows = cur.fetchall()
          conn.commit()
          for result in rows:
                if(result[0]):
                     mag = float(result[0])
                     #print(mag)
                     if 0<=mag<=1:
                         count01 += 1
                     if 1<=mag<=2:
                         count12 += 1
                     if 2<=mag<=3:
                         count23 += 1
                     if 3<=mag<=4:
                         count34 += 1
                     if 4<=mag<=5:
                         count45 += 1
          print(count01)
          print(count12)
          print(count23)
          print(count34)
          print(count45)
          cur.close()
          conn.close()
     return render_template('piehighchart.html', count01=count01, count12=count12, count23=count23, count34=count34, count45=count45)

@app.route("/sp")
def sp():
    return render_template('scatterplot.html')

@app.route("/scatterplot")
def scatterplot():
     
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          rows = []
          mag = []
          depth = []
          stmt = "select top 100 mag,depth from Earthquake order by time desc"
          cur = conn.cursor()
          cur.execute(stmt)
          rows = cur.fetchall()
          conn.commit()
          for result in rows:
               if(result[0] and result[1]):
                    mag.append(result[0])
                    depth.append(result[1])
          cur.close()
          conn.close()
     return render_template('scatterplot.html', rows=rows, mag=mag, depth=depth)

@app.route("/pq")
def pq():
    return render_template('pieQ.html')

@app.route("/pieQ")
def pieQ():
     range1 = int(request.args.get('range1'))
     range2 = int(request.args.get('range2'))
     year = (request.args.get('year'))
     print(year)
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          rows = []
          st=[]
          yr=[]
          st.append(0)
          yr.append(0)
          stmt = "Select state, \"" + str(year) +"\" from sample where \"" + str(year) + "\" > \'" + str(range1) + "\' and \"" + str(year) + "\" < \'" + str(range2) + "\'"
          cur = conn.cursor()
          cur.execute(stmt)
          rows = cur.fetchall()
          conn.commit()
          for result in rows:
               if(result[0] and result[1]):
                    st.append(result[0])
                    yr.append(result[1])
          
          cur.close()
          conn.close()
     return render_template('pieQ.html',rows=rows,st=st,yr=yr)

@app.route("/sq")
def sq():
    return render_template('scatterQ.html')

@app.route("/scatterQ")
def scatterQ():
     range1 = request.args.get('range1')
     range2 = request.args.get('range2')
     if(range1=='2010'):
          i=1
          print(i)
     if(range1=='2011'):
          i=2
          print(i)
     if(range1=='2012'):
          i=3
          print(i)
     if(range1=='2013'):
          i=4
          print(i)
     if(range1=='2014'):
          i=5
          print(i)
     if(range1=='2015'):
          i=6
          print(i)
     if(range1=='2016'):
          i=7
          print(i)
     if(range1=='2017'):
          i=8
          print(i)

     if(range2=='2011'):
          j=2
          print(j)
     if(range2=='2012'):
          j=3
          print(j)
     if(range2=='2013'):
          j=4
          print(j)
     if(range2=='2014'):
          j=5
          print(j)
     if(range2=='2015'):
          j=6
          print(j)
     if(range2=='2016'):
          j=7
          print(j)
     if(range2=='2017'):
          j=8
          print(j)
     if(range2=='2018'):
          j=9
          print(j)
     state = request.args.get('state')
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          cols = []
          result =[]
          result.append(0)
          year =[]
          year.append(0)
          stmt = "select * from sample where state=?"
          cur = conn.cursor()
          cur.execute(stmt,(state))
          cols = cur.fetchone()
          conn.commit()
          print(cols)
          statename = cols[0]
          k=i
          while k <= j:
               result.append(cols[k])
               k+= 1
         
          while i<=j:
               if i==1:
                    year.append('2010')
               if i==2:
                    year.append('2011')
               if i==3:
                    year.append('2012')
               if i==4:
                    year.append('2013')
               if i==5:
                    year.append('2014')
               if i==6:
                    year.append('2015')
               if i==7:
                    year.append('2016')
               if i==8:
                    year.append('2017')
               if i==9:
                    year.append('2018')
               i+=1

          cur.close()
          conn.close()
     return render_template('scatterQ.html',result=result, range1=range1, range2=range2, statename=statename,year=year)

@app.route("/sv")
def sv():
    return render_template('scattervolcano.html')

@app.route("/scattervol")
def scattervol():
     range1 = int(request.args.get('range1'))
     range2 = int(request.args.get('range2'))
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          rows = []
          elev = []
          number = []
          stmt = "select Elev,Number from volcano where Number >=? and Number <=?"
          cur = conn.cursor()
          cur.execute(stmt,(range1,range2))
          rows = cur.fetchall()
          conn.commit()
          print(rows)
          for result in rows:
               if(result[0] and result[1]):
                    elev.append(result[0])
                    number.append(result[1])
          cur.close()
          conn.close()
     return render_template('scattervolcano.html', rows=rows, elev=elev, number=number)

@app.route("/vb")
def vb():
    return render_template('verticalbar.html')

@app.route("/verticalbar")
def verticalbar():
     country = request.args.get('country')
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          rows = []
          vol = []
          elev = []
          stmt = "select Volcano_Name,Elev from volcano where country=?"
          cur = conn.cursor()
          cur.execute(stmt,(country))
          rows = cur.fetchall()
          conn.commit()
          print(rows)
          for result in rows:
               if(result[0] and result[1]):
                    vol.append(result[0])
                    elev.append(result[1])
          cur.close()
          conn.close()
     return render_template('verticalbar.html', rows=rows, vol=vol, elev=elev)


@app.route("/pv")
def pv():
    return render_template('pievol.html')

@app.route("/pievol")
def pievol():
     range1 = float(request.args.get('range1'))
     range2 = float(request.args.get('range2'))
     slices = float(request.args.get('slices'))
     newrange= float(range2/slices)
     countarr =[]
     i=1
     conn = pyodbc.connect('DRIVER={ODBC Driver 17 for SQL Server};SERVER='+server+';PORT=1443;DATABASE='+database+';UID='+username+';PWD='+ password)
     if conn:
          rows = []
          result=[]
          for i in range(int(slices)):
               count=0
               rng = float(newrange * float(i))
               stmt = "select * from volcano where Elev<=?"
               cur = conn.cursor()
               cur.execute(stmt,(rng))
               rows = cur.fetchall()
               conn.commit()
               for result in rows:
                    count+=1
               countarr.append(count)
          cur.close()
          conn.close()
     return render_template('pievol.html',countarr=countarr)
