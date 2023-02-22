from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
from flask_login import UserMixin, login_user, LoginManager, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import InputRequired, Length, ValidationError
from flask_bcrypt import Bcrypt 
import os
application = Flask(__name__, static_folder='/static')

# connection
application.config['MYSQL_HOST'] = os.environ.get("MYSQL_HOST")
application.config['MYSQL_DB'] = os.environ.get("MYSQL_DB")
application.config['MYSQL_USER'] = "root"
application.config['MYSQL_PASSWORD'] = os.environ.get("MYSQL_PASSWORD")
application.config['SECRET_KEY'] = 'keyforencrpytion'
mysql = MySQL()
mysql.init_app(application)




@application.route('/login')
def login():
    return render_template('login.html')


@application.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_product WHERE id_slot != 0")
    row = cur.fetchall()
    data = []
    for x in row:
        data.append({
            "id": x[0],
            "product_name": x[1],
            "product_desc": x[2],
            "product_price": x[3],
            "product_slot": x[4],
            "product_image": x[5]
        })

    return render_template('store/store.html', data=data)

@application.route('/cart/<id>')
def add_to_cart(id):
    req_data = {
        "product": id,
        "product_slot": 1,
        "id_user": 1, # sementara
        "status": "ongoing"
    }
    cur = mysql.connection.cursor()
    cur.execute("INSERT INTO tb_cart (id_product, id_slot, id_user, status) VALUES (%s,%s,%s, %s)", (req_data.get('product'), req_data.get('product_slot'), req_data.get('id_user'), req_data.get('status')))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('payment'))

@application.route('/delete-cart/<id>')
def cancel_cart(id):
    req_data = {
        "product": id,
        "id_user": 1, # sementara
        "status": "ongoing"
    }
    cur = mysql.connection.cursor()
    cur.execute("DELETE FROM tb_cart WHERE id = %s and id_user = %s and status = %s", (req_data.get('product'), req_data.get('id_user'), req_data.get('status')))
    mysql.connection.commit()
    cur.close()
    return redirect(url_for('payment'))



@application.route('/payment-dash')
def payment():

    cur = mysql.connection.cursor()
    cur.execute("SELECT *, tb_product.product_name FROM tb_cart JOIN tb_product ON tb_cart.id_product = tb_product.id WHERE tb_cart.id_user = 1 AND tb_cart.status = 'ongoing' ")
    row = cur.fetchall()

    data = []
    for x in row:
        data.append({
            "id": x[0],
            "product_id": x[1],
            "product_name": x[6],
            "product_price": x[8],
            "product_slot": x[9],
            "user_slot": x[2],
            'status': x[4]
        })
    return render_template('store/payment.html', data=data)


@application.route('/payment-success/<id>/<id_product>')
def payment_success(id, id_product):
    req_data = {
        "cart_id": id,
        "product": id_product,
        "product_slot": 1,
        "id_user": 1, # sementara
        "status": "completed"
    }
    cur = mysql.connection.cursor()
    cur.execute('SELECT * FROM tb_product WHERE id = %s', (req_data.get('product')))
    row = cur.fetchone()
    post_data = {
        "id_slot": row[4]
    }
    if post_data.get('id_slot') != 0:
        last_item = post_data.get('id_slot') - req_data.get('product_slot')
        cur.execute("UPDATE tb_cart SET status = %s WHERE id = %s AND id_user = %s ", (req_data.get('status'), req_data.get('cart_id'), req_data.get('id_user') ))
        cur.execute('UPDATE tb_product SET id_slot = %s WHERE id = %s', (last_item, req_data.get('product')))
        mysql.connection.commit()
        cur.close()
    return redirect(url_for('home'))


if __name__ == "__main__":
    application.run(debug=True)
