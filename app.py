from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///prantashiksha.db'
db = SQLAlchemy(app)


class Student(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  student_class = db.Column(db.String(50), nullable=False)
  subject = db.Column(db.String(50), nullable=False)
  attendances = db.relationship(
      'Attendance', backref='student', cascade='all, delete-orphan'
  )
  fees = db.relationship('Fee', backref='student', cascade='all, delete-orphan')


class Attendance(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.String(50), nullable=False)
  status = db.Column(db.String(20), nullable=False)
  student_id = db.Column(
      db.Integer, db.ForeignKey('student.id'), nullable=False
  )


class Fee(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date_paid = db.Column(db.String(50), nullable=False)
  amount = db.Column(db.Float, nullable=False)
  status = db.Column(db.String(20), nullable=False)
  remarks = db.Column(db.String(100), nullable=True)
  student_id = db.Column(
      db.Integer, db.ForeignKey('student.id'), nullable=False
  )


with app.app_context():
  db.create_all()


@app.route('/')
def index():
  students = Student.query.all()
  return render_template('index.html', students=students)


@app.route('/add', methods=['GET', 'POST'])
def add_student():
  if request.method == 'POST':
    name = request.form['name']
    student_class = request.form['student_class']
    subject = request.form['subject']
    new_student = Student(
        name=name, student_class=student_class, subject=subject
    )
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('index'))
  return render_template('add_student.html')


@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_student(id):
  student = Student.query.get_or_404(id)
  if request.method == 'POST':
    student.name = request.form['name']
    student.student_class = request.form['student_class']
    student.subject = request.form['subject']
    db.session.commit()
    return redirect(url_for('index'))
  return render_template('edit_student.html', student=student)


@app.route('/delete/<int:id>')
def delete_student(id):
  student = Student.query.get_or_404(id)
  db.session.delete(student)
  db.session.commit()
  return redirect(url_for('index'))


@app.route('/student/<int:id>')
def student_detail(id):
  student = Student.query.get_or_404(id)
  return render_template('detail.html', student=student)


@app.route('/student/<int:id>/add_attendance', methods=['POST'])
def add_attendance(id):
  date = request.form['date']
  status = request.form['status']
  new_att = Attendance(date=date, status=status, student_id=id)
  db.session.add(new_att)
  db.session.commit()
  return redirect(url_for('student_detail', id=id))


@app.route('/student/<int:id>/add_fee', methods=['POST'])
def add_fee(id):
  date_paid = request.form['date_paid']
  amount = request.form['amount']
  status = request.form['status']
  remarks = request.form['remarks']
  new_fee = Fee(
      date_paid=date_paid,
      amount=amount,
      status=status,
      remarks=remarks,
      student_id=id,
  )
  db.session.add(new_fee)
  db.session.commit()
  return redirect(url_for('student_detail', id=id))


@app.route('/student/<int:id>/receipt')
def student_receipt(id):
  student = Student.query.get_or_404(id)
  return render_template('receipt.html', student=student)


if __name__ == '__main__':
  app.run(debug=True)