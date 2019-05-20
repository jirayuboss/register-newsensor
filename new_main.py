import datetime
import logging
import os
from flask import Flask, render_template, request, jsonify, redirect, url_for
from flaskext.mysql import MySQL
from flask import Flask, render_template, request, Response
import sqlalchemy

app = Flask(__name__)
mysql = MySQL()

# MySQL configurations
app.config['MYSQL_DATABASE_USER'] = 'root'
app.config['MYSQL_DATABASE_PASSWORD'] = 'Jirayu1001'
app.config['MYSQL_DATABASE_DB'] = 'sensor_data'
app.config['MYSQL_DATABASE_HOST'] = '35.193.167.78'
mysql.init_app(app)

# Remember - storing secrets in plaintext is potentially unsafe. Consider using
# something like https://cloud.google.com/kms/ to help keep secrets secret.
db_user = os.environ.get("DB_USER")
db_pass = os.environ.get("DB_PASS")
db_name = os.environ.get("DB_NAME")
cloud_sql_connection_name = os.environ.get("CLOUD_SQL_CONNECTION_NAME")

logger = logging.getLogger()

# [START cloud_sql_mysql_sqlalchemy_create]
# The SQLAlchemy engine will help manage interactions, including automatically
# managing a pool of connections to your database
db = sqlalchemy.create_engine(
    # Equivalent URL:
    # mysql+pymysql://<db_user>:<db_pass>@/<db_name>?unix_socket=/cloudsql/<cloud_sql_instance_name>
    sqlalchemy.engine.url.URL(
        drivername='mysql+pymysql',
        username=db_user,
        password=db_pass,
        database=db_name,
        query={
            'unix_socket': '/cloudsql/{}'.format(cloud_sql_connection_name)
        }
    ),
    # ... Specify additional properties here.
    # [START_EXCLUDE]

    # [START cloud_sql_mysql_sqlalchemy_limit]
    # Pool size is the maximum number of permanent connections to keep.
    pool_size=5,
    # Temporarily exceeds the set pool_size if no connections are available.
    max_overflow=2,
    # The total number of concurrent connections for your application will be
    # a total of pool_size and max_overflow.
    # [END cloud_sql_mysql_sqlalchemy_limit]

    # [START cloud_sql_mysql_sqlalchemy_backoff]
    # SQLAlchemy automatically uses delays between failed connection attempts,
    # but provides no arguments for configuration.
    # [END cloud_sql_mysql_sqlalchemy_backoff]

    # [START cloud_sql_mysql_sqlalchemy_timeout]
    # 'pool_timeout' is the maximum number of seconds to wait when retrieving a
    # new connection from the pool. After the specified amount of time, an
    # exception will be thrown.
    pool_timeout=30,  # 30 seconds
    # [END cloud_sql_mysql_sqlalchemy_timeout]

    # [START cloud_sql_mysql_sqlalchemy_lifetime]
    # 'pool_recycle' is the maximum number of seconds a connection can persist.
    # Connections that live longer than the specified amount of time will be
    # reestablished
    pool_recycle=1800,  # 30 minutes
    # [END cloud_sql_mysql_sqlalchemy_lifetime]

    # [END_EXCLUDE]
)
# [END cloud_sql_mysql_sqlalchemy_create]

@app.route('/', methods = ['POST', 'GET'])
def home():
    if request.method == 'POST':
        if request.form['add_button'] == 'Add':
            return redirect(url_for('addsensors'))
    data = []
    with db.connect() as conn:
        data = cur.execute("select name, sensorID, sensorAPI, projectID from userdata where username = %s", 'pigboss1').fetchall()
        print(data)
    return render_template("home.html", data = data)

@app.route('/add', methods = ['POST', 'GET'])
def addsensors():
    data = []
    if request.method == 'POST':
        post_data = request.form
        with db.connect() as conn:
            data = cur.execute("select sensorID, sensorAPI from userdata where sensorID = %s or sensorAPI = %s", (post_data["sensorID"], post_data["sensorAPI"])).fetchall()
            if len(data) == 0:
                with db.connect() as conn:
                    cur.execute("insert into userdata(username, name, sensorID, sensorAPI, projectID) values(:username,:name,:sensorID,:sensorAPI,:projectID)", username = 'pigboss1', name = post_data["Name"], sensorID = post_data["sensorID"], sensorAPI = post_data["sensorAPI"], projectID = request.form.get('project'))
                return redirect(url_for('home'))
            elif len(post_data["Name"]) == 0 or len(post_data["sensorID"]) == 0 or len(post_data["sensorAPI"]) == 0:
                return render_template("addSensor.html", data = "Please fill in all components.")
            else:
                return render_template("addSensor.html", data = "This Sensor ID or Sensor API has been used.")

    return render_template("addSensor.html", data = " ")

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8080, debug=True)
