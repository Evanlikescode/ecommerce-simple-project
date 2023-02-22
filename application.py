from flask import Flask, render_template, request, session, redirect, url_for
from flask_mysqldb import MySQL
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




@application.route('/register', methods=['POST', 'GET'])
def register():
    if session.get('is_login') == False: # menunjukkan bahwa user belum memiliki akses login

        if request.method == "POST": # menunjukkan bahwa method HTTP yang digunakan adalah POST / untuk membuat data
            cur = mysql.connection.cursor() # deklarasi penggunaan method mysql di awal
            req_data = {
                "username": request.form['username'],
                "fullname": request.form['fullname'],
                "email": request.form['email'],
                "password": request.form['password'],
                "role": 1
            } # deklarasi data2 request dari form html dengan dictionary agar mudah diakses dan diubah

            cur.execute('SELECT * FROM tb_user WHERE username = %s OR email = %s OR fullname = %s', 
            (req_data.get('username'), req_data.get('email'), req_data.get('fullname'))) # query mysql (select) yang bertujuan untuk mendapatkan data dari database 
            row = cur.fetchone() # method flask_mysqldb untuk mendapatkan data satuan sesuai id
            if row != None: # ketika data satuan tidak sama dengan kosong, maka sistem akan return message false dan akan diambil html untuk mengetahui bahwa html harus menampilkan pesan yang menunjukkan bahwa input data akun tersebut sudah tersedia
                message = "false"
                return render_template('register/register.html', message=message)
            else:
                cur.execute('INSERT INTO tb_user (uuid_user, username, fullname, email, passwords, id_role) VALUES (%s,%s,%s,%s,%s,%s)', # ini merupakan query iNSERT untuk memasukkan data user baru ke database
                ('abcd1', req_data.get('username'), req_data.get('fullname'), req_data.get('email'), req_data.get('password'), req_data.get('role')))
                mysql.connection.commit()
                cur.execute('SELECT * FROM tb_user WHERE email = %s AND fullname = %s', (req_data.get('email'), req_data.get('fullname'))) # mendapatkan data yang telah berhasil di input di database
                rows = cur.fetchone()
                print(rows)
                data = {
                    'id': rows[0]
                }
                session['is_login'] = True # setup session yang berada di browser sehingga dapat digunakan di halaman lainnya
                session['id'] = data.get('id')
                session['username'] = req_data.get('username')
                session['email'] = req_data.get('email')
                session['fullname'] = req_data.get('fullname')
                session['role'] = req_data.get('role')
                return redirect(url_for('home')) # redirect atau melanjutkan ke halaman berikutnya ketika semua perintah telah terjalani
        return render_template('register/register.html', message="")
    else:
        return redirect(url_for('home'))
@application.route('/login', methods=['GET','POST'])
def login():
    if session.get('is_login') == False:

        if request.method == "POST":
            cur = mysql.connection.cursor()
            req_data = {
                "email": request.form['email'],
                "password": request.form['password']
            }

            cur.execute('SELECT * FROM tb_user WHERE email = %s AND passwords = %s', (req_data.get('email'), req_data.get('password')))
            row = cur.fetchone()
            if row == None:
                message = "false"
                return render_template('login/login.html', message=message)
            else:
                session['is_login'] = True
                session['username'] = row[2]
                session['fullname'] = row[3]
                session['email'] = row[4]
                session['role'] = row[6]
                session['id'] = row[0]
                return redirect(url_for('home'))
            
                
                
        return render_template('login/login.html', message="")
    else:
        return redirect(url_for('home'))

@application.route('/logout')
def logout():
    if session.get('is_login') == True:
        if session['is_login'] != False:
            session['is_login'] = False
            session.pop('username', None) # session.pop merupakan method untuk menghapus session yang kita setup di browser. Hal ini dimulai dengan deklarasi kunSci session yang kita buat sebelumnya
            session.pop('fullname', None)
            session.pop('email', None)
            session.pop('role', None)
            session.pop('id', None)
        return redirect(url_for('home'))
    else:
        return redirect(url_for('login'))
@application.route('/')
def home():
    cur = mysql.connection.cursor()
    cur.execute("SELECT * FROM tb_product WHERE id_slot != 0") # select data dari tb_product yang memiliki ketersediaan barang
    row = cur.fetchall() # fetchall merupakan method get keseluruhan data yang sesuai dengan apa yang kita minta
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

@application.route('/cart/<id>') # <id> menunjukkan bahwa halaman ini memerlukan parameter id untuk menjalankan perintah selanjutnya
def add_to_cart(id): # terdapat parameter id dalam function ini sebagai deklarasi untuk id pada parameter / url browser
    if session.get('is_login') == True:
            
        req_data = {
            "product": id,
            "product_slot": 1,
            "id_user": session.get('id'),
            "status": "ongoing"
        }
        cur = mysql.connection.cursor()
        cur.execute("INSERT INTO tb_cart (id_product, id_slot, id_user, status) VALUES (%s,%s,%s, %s)", (req_data.get('product'), req_data.get('product_slot'), req_data.get('id_user'), req_data.get('status')))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('payment'))
    return redirect(url_for('login'))

@application.route('/delete-cart/<id>')
def cancel_cart(id):
    if session.get('is_login') == True:
        req_data = {
            "product": id,
            "id_user": session.get('id'),
            "status": "ongoing"
        }
        cur = mysql.connection.cursor()
        cur.execute("DELETE FROM tb_cart WHERE id = %s and id_user = %s and status = %s", (req_data.get('product'), req_data.get('id_user'), req_data.get('status')))
        mysql.connection.commit()
        cur.close()
        return redirect(url_for('payment'))
    else:
        return redirect(url_for('login'))



@application.route('/payment-dash')
def payment():
    if session.get('is_login') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT *, tb_product.product_name FROM tb_cart JOIN tb_product ON tb_cart.id_product = tb_product.id WHERE tb_cart.id_user = %s AND tb_cart.status = 'ongoing' ", (session.get('id'),))
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
    else:
        return redirect(url_for('login'))

@application.route('/payment-success/<id>/<id_product>')
def payment_success(id, id_product):
    if session.get('is_login') == True:
        req_data = {
            "cart_id": id,
            "product": id_product,
            "product_slot": 1,
            "id_user": session.get('id'),
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
    else:
        return redirect(url_for('login'))

@application.route('/completed-cart')
def completed_cart():
    if session.get('is_login') == True:
        cur = mysql.connection.cursor()
        cur.execute("SELECT *, tb_product.product_name FROM tb_cart JOIN tb_product ON tb_cart.id_product = tb_product.id WHERE tb_cart.id_user = %s AND tb_cart.status = 'completed' ", (session.get('id'),))
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
        return render_template('store/done.html', data=data)
    else:
        return redirect(url_for('login'))


if __name__ == "__main__":
    application.run(debug=True)
