from flask import Flask, render_template, request, jsonify, redirect, url_for
from flaskext.mysql import MySQL

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Jirayu1001'
app.config['MYSQL_DATABASE_DB'] = 'sensor_data'
app.config['MYSQL_DATABASE_HOST'] = '35.193.167.78'
mysql.init_app(app)

@app.route('/', methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':
        if request.form['add_button'] == 'Add':
            return redirect(url_for('addsensors'))
    data = []
    cur = mysql.connect().cursor()
    cur.execute("select name, sensorID, sensorAPI, projectID from userdata where username = %s", 'pigboss1')
    data = [dict((cur.description[i][0], value)
              for i, value in enumerate(row)) for row in cur.fetchall()]
    return render_template("home.html", data = data)

@app.route('/add', methods = ['POST', 'GET'])
def addsensors():
    data = []
    if request.method == 'POST':
        post_data = request.form
        con = mysql.connect()
        cur = con.cursor()
        cur.execute("select sensorID, sensorAPI from userdata where sensorID = %s or sensorAPI = %s", (post_data["sensorID"], post_data["sensorAPI"]))
        data = [dict((cur.description[i][0], value)
            for i, value in enumerate(row)) for row in cur.fetchall()]
        if len(data) == 0:
            cur.execute("insert into userdata(username, name, sensorID, sensorAPI, projectID) values(%s, %s, %s, %s, %s)", ('pigboss1', post_data["Name"], post_data["sensorID"], post_data["sensorAPI"], request.form.get('project')))
            con.commit()
            return redirect(url_for('home'))
        elif len(post_data["Name"]) == 0 or len(post_data["sensorID"]) == 0 or len(post_data["sensorAPI"]) == 0:
            return render_template("addSensor.html", data = "Please fill in all components.")
        else:
            return render_template("addSensor.html", data = "This Sensor ID or Sensor API has been used.")

    return render_template("addSensor.html", data = " ")

if __name__ == '__main__':
    app.run(host='0.0.0.0' ,port=8080, debug=True)
