from flask import Flask
import os

application = Flask(__name__)

# connection
application.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
application.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
application.config['MYSQL_USER'] = os.environ.get("MYSQL_USER")
application.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")


@application.route('/')
def test():
    return 'test'

if __name__ == "__main__":
    application.run(debug=True)
