from flask import Flask, render_template, request, redirect, url_for
import pymysql

app = Flask(__name__)

def get_connection():
    return pymysql.connect(
        host='srms-db.czcuckqmq54p.ap-south-1.rds.amazonaws.com',
        user='admin',
        password='deepika0506',
        database='student_db',
        cursorclass=pymysql.cursors.DictCursor
    )

@app.route('/')
def index():
    page = int(request.args.get('page', 1))
    search = request.args.get('search', '').strip()
    per_page = 20
    offset = (page - 1) * per_page

    conn = get_connection()
    with conn.cursor() as cur:
        if search:
            like_query = f"%{search}%"
            cur.execute("""SELECT COUNT(*) as total FROM students
                           WHERE name LIKE %s OR email LIKE %s OR course LIKE %s""",
                        (like_query, like_query, like_query))
            total = cur.fetchone()['total']
            cur.execute("""SELECT * FROM students
                           WHERE name LIKE %s OR email LIKE %s OR course LIKE %s
                           ORDER BY id LIMIT %s OFFSET %s""",
                        (like_query, like_query, like_query, per_page, offset))
            students = cur.fetchall()
        else:
            cur.execute("SELECT COUNT(*) as total FROM students")
            total = cur.fetchone()['total']
            cur.execute("SELECT * FROM students ORDER BY id LIMIT %s OFFSET %s", (per_page, offset))
            students = cur.fetchall()
    conn.close()

    total_pages = (total + per_page - 1) // per_page if total > 0 else 1
    return render_template('index.html', students=students, page=page,
                            total_pages=total_pages, total=total, search=search)

@app.route('/add', methods=['GET', 'POST'])
def add():
    if request.method == 'POST':
        data = (request.form['name'], request.form['email'], request.form['course'],
                request.form['year_of_study'], request.form['phone'], request.form['address'])
        conn = get_connection()
        with conn.cursor() as cur:
            cur.execute("""INSERT INTO students (name, email, course, year_of_study, phone, address)
                           VALUES (%s, %s, %s, %s, %s, %s)""", data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    return render_template('add.html')

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit(id):
    conn = get_connection()
    if request.method == 'POST':
        data = (request.form['name'], request.form['email'], request.form['course'],
                request.form['year_of_study'], request.form['phone'], request.form['address'], id)
        with conn.cursor() as cur:
            cur.execute("""UPDATE students SET name=%s, email=%s, course=%s,
                           year_of_study=%s, phone=%s, address=%s WHERE id=%s""", data)
        conn.commit()
        conn.close()
        return redirect(url_for('index'))
    else:
        with conn.cursor() as cur:
            cur.execute("SELECT * FROM students WHERE id=%s", (id,))
            student = cur.fetchone()
        conn.close()
        return render_template('edit.html', student=student)

@app.route('/delete/<int:id>')
def delete(id):
    conn = get_connection()
    with conn.cursor() as cur:
        cur.execute("DELETE FROM students WHERE id=%s", (id,))
    conn.commit()
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)
