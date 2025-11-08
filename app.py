from flask import Flask, render_template, request, redirect, url_for, session
import bcrypt
from flask_mysqldb import MySQL, MySQLdb
from secrets import token_hex

# ==========================
# APP CONFIGURATION
# ==========================
app = Flask(__name__)
app.secret_key = token_hex(16)

app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = ''
app.config['MYSQL_DB'] = 'id_pemilu_osis'

mysql = MySQL(app)


# ==========================
# ROUTES
# ==========================
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/verification')
def verification():
    return render_template('verification.html')


# ==========================
# LOGIN ADMIN
# ==========================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
        cursor.execute('SELECT * FROM admin WHERE username = %s', [username])
        admin = cursor.fetchone()
        cursor.close()

        if admin:
            storedpassword = admin['password']  # Ambil dari database
            if bcrypt.checkpw(password.encode('utf-8'), storedpassword.encode('utf-8')):
                session['id_admin'] = admin['id_admin']
                session['nama'] = admin['nama']
                session['username'] = admin['username']
                return redirect(url_for('pemilu'))
            else:
                return render_template('login.html',error='Password kamu salah king')
        else:
            return "Username tidak ditemukan"

    return render_template('login.html')


# ==========================
# LOGOUT ADMIN
# ==========================

@app.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('index'))



# ==========================
# SEEDER ADMIN (untuk buat akun admin)
# ==========================
@app.route('/seeder')
def seeder():
    username = "Nauval"
    password = "Nauval123"
    nama = "Nauval baik hati"

    bytespassword = password.encode('utf-8')
    hashed = bcrypt.hashpw(bytespassword, bcrypt.gensalt())
    hashed_str = hashed.decode('utf-8')  # Simpan sebagai string

    cursor = mysql.connection.cursor()
    cursor.execute(
        'INSERT IGNORE INTO admin (username, password, nama) VALUES (%s, %s, %s)',
        (username, hashed_str, nama)
    )
    mysql.connection.commit()
    cursor.close()

    return f"Akun admin berhasil dibuat: {username}"


# ==========================
# DASHBOARD PEMILU
# ==========================
@app.route('/pemilu')
def pemilu():
    if 'id_admin' not in session:
        return redirect (url_for ('login'))

    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM pemilu')
    pemilu=cursor.fetchall()
    cursor.close()
    return render_template('pemilu/index.html', data=pemilu)

@app.route('/tambah_pemilu', methods=['GET', 'POST'])
def tambah_pemilu():
    if 'id_admin' not in session:
        return redirect (url_for ('login'))
    
    if request.method=='POST':
        nama_pemilu = request.form['nama_pemilu']
        tanggal_mulai = request.form['tanggal_mulai']
        tanggal_selesai = request.form['tanggal_selesai']
        status = request.form['status'].strip().lower()
        if status not in ['Aktif', 'Non-Aktif']:
            status='Aktif'
            status='Non-Aktif'

        cursor=mysql.connection.cursor()
        cursor.execute("INSERT INTO pemilu (nama_pemilu, tanggal_mulai, tanggal_selesai, status, id_admin) VALUES (%s, %s, %s, %s, %s)", [nama_pemilu, tanggal_mulai, tanggal_selesai, status, session['id_admin']])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('pemilu'))

    return render_template('pemilu/create.html')

# @app.route('/hapus_pemilu/<int:id>', methods=['GET','POST'])
# def edit_pemilu(id):
#     if 'id_admin' not in session:
#         return redirect(url_for('login'))
    
#     if request.method=='POST':
#         nama_pemilu = request.form['nama_pemilu']
#         tanggal_mulai = request.form['tanggal_mulai']
#         tanggal_selesai = request.form['tanggal_selesai']
#         status = request.form['status'].strip().lower()
#         if status not in ['aktif', 'non-aktif']:
#             status='non-aktif'

#         cursor=mysql.connection.cursor()
#         cursor.execute("UPDATE pemilu SET nama_pemilu=%s tanggal_mulai=%s tanggal_selesai=%s status=%a id_admin=%s WHERE id_pemilu=%s", (nama_pemilu, tanggal_mulai, tanggal_selesai, status, session['id_admin'],id,))
#         mysql.connection.commit()
#         cursor.close()
#         return redirect(url_for('pemilu'))

#     cursor=mysql.connection.cursor()
#     cursor.execute('SELECT * FROM pemilu WHERE id_pemilu=%s', [id])
#     pemilu=cursor.fetchone()
#     return render_template('pemilu/edit.html', data=pemilu)

@app.route('/edit_pemilu/<int:id>',methods=['GET','POST'])
def edit_pemilu(id):
    if 'id_admin' not in session:
        return redirect(url_for('login'))
    
    if request.method=='POST':
        nama_pemilu=request.form['nama_pemilu']
        tanggal_mulai=request.form['tanggal_mulai']
        tanggal_selesai=request.form['tanggal_selesai']
        status=request.form['status'].strip().lower()

        
        cursor=mysql.connection.cursor()
        cursor.execute("UPDATE pemilu SET nama_pemilu=%s, tanggal_mulai=%s, tanggal_selesai=%s, status=%s, id_admin=%s WHERE id_pemilu=%s", [nama_pemilu,tanggal_mulai,tanggal_selesai,status,session['id_admin'],id,])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('pemilu'))
    
    #pilih data dari database
    cursor=mysql.connection.cursor(MySQLdb.cursors.DictCursor) 
    cursor.execute('SELECT * FROM pemilu where id_pemilu=%s',[id])
    pemilu=cursor.fetchone()
    return render_template('pemilu/edit.html',data=pemilu)


# ==========================
# KELOLA KELAS
# ==========================
@app.route('/kelas')
def kelas():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM kelas')
    data = cursor.fetchall()
    cursor.close()
    return render_template('kelas/index.html', data=data)


@app.route('/tambah_kelas', methods=['GET', 'POST'])
def tambah_kelas():
    if request.method == 'POST':
        kode = request.form['kode_kelas']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO kelas (kode_kelas) VALUES (%s)', (kode,))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('kelas'))

    return render_template('kelas/create.html')


@app.route('/edit_kelas/<int:id>', methods=['GET', 'POST'])
def edit_kelas(id):
    if request.method == 'POST':
        kode = request.form['kode_kelas']
        cursor = mysql.connection.cursor()
        cursor.execute('UPDATE kelas SET kode_kelas = %s WHERE id_kelas = %s', (kode, id))
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('kelas'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM kelas WHERE id_kelas = %s', [id])
    kelas = cursor.fetchone()
    cursor.close()
    return render_template('kelas/edit.html', data=kelas)


# ==========================
# KELOLA PEMILIH (VOTERS)
# ==========================
@app.route('/voters')
def voters():
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT voters.id_voter, voters.nama, kelas.kode_kelas
        FROM voters
        JOIN kelas ON voters.id_kelas = kelas.id_kelas
    ''')
    data = cursor.fetchall()
    cursor.close()
    return render_template('voters/index.html', data=data)


@app.route('/tambah_pemilih', methods=['GET', 'POST'])
def tambah_voters():
    if request.method == 'POST':
        nama = request.form['nama']
        id_kelas = request.form['id_kelas']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO voters (nama, id_kelas) VALUES (%s, %s)', [nama, id_kelas])
        mysql.connection.commit() 
        cursor.close()
        return redirect(url_for('voters'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM kelas')
    kelas = cursor.fetchall()
    cursor.close()
    return render_template('voters/create.html', data_kelas=kelas)

@app.route('/edit_pemilih/<int:id>', methods=['GET', 'POST'])
def edit_voters(id):
    if request.method == 'POST':
        nama = request.form['nama']
        id_kelas = request.form['id_kelas']
        cursor = mysql.connection.cursor()
        cursor.execute(
            'UPDATE voters SET nama = %s, id_kelas = %s WHERE id_voter = %s',
            [nama, id_kelas, id]
        )
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('voters'))

    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM voters WHERE id_voter = %s', (id,))
    voter = cursor.fetchone()
    cursor.execute('SELECT * FROM kelas')
    kelas = cursor.fetchall()
    cursor.close()
    return render_template('voters/edit.html', data=voter, data_kelas=kelas)


@app.route('/tambah_kandidat', methods=['GET', 'POST'])
def tambah_kandidat():
    if request.method == 'POST':
        nama = request.form['nama']
        id_kelas = request.form['id_kelas']
        cursor = mysql.connection.cursor()
        cursor.execute('INSERT INTO voters (nama, id_kelas) VALUES (%s, %s)', [nama, id_kelas])
        mysql.connection.commit()
        cursor.close()
        return redirect(url_for('voters'))


    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('SELECT * FROM kelas')
    kelas = cursor.fetchall()
    cursor.close()
    return render_template('voters/create.html', data_kelas=kelas)


@app.route('/hapus_pemilih/<int:id>', methods=['POST'])
def hapus_voters(id):
    cursor = mysql.connection.cursor()
    cursor.execute('DELETE FROM voters WHERE id_voter = %s', [id])
    mysql.connection.commit()
    cursor.close()
    return redirect(url_for('voters'))


@app.route('/lihat_pemilih/<int:id>', methods=['GET', 'POST'])
def lihat_pemilih(id):
    cursor = mysql.connection.cursor(MySQLdb.cursors.DictCursor)
    cursor.execute('''
        SELECT voters.id_voter, voters.nama, kelas.kode_kelas
        FROM voters
        JOIN kelas ON voters.id_kelas = kelas.id_kelas
        WHERE voters.id_kelas = %s
    ''', [id])
    data_pemilih = cursor.fetchall()
    cursor.execute('SELECT * FROM kelas WHERE id_kelas = %s', [id])
    data_kelas = cursor.fetchone()
    cursor.close()
    return render_template('voters/lihat_pemilih.html', data_pemilih=data_pemilih, data_kelas=data_kelas)


# ==========================
# MAIN ENTRY POINT
# ==========================
if __name__ == '__main__':
    app.run(debug=True)
