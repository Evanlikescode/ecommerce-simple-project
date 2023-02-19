from flask import Flask
from flaskext.mysql import MySQL
import os
application = Flask(__name__)

# connection
application.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
application.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
application.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
application.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
mysql = MySQL()
mysql.init_app(application)

@application.route('/')
def login():
    cur = mysql.get_db().cursor()
    cur.execute("SELECT * FROM tb_user")
    row = cur.fetchall()
    print(row)
    return ''
    

if __name__ == "__main__":
    application.run(debug=True)
