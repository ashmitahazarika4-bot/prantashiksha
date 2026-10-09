from datetime import datetime
from flask import Flask, redirect, render_template, request, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tuition.db'
db = SQLAlchemy(app)


class Student(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(100), nullable=False)
  student_class = db.Column(db.String(50), nullable=False)
  subject = db.Column(db.String(100), nullable=False)
  total_fee = db.Column(db.Float, default=0.0)
  paid_fee = db.Column(db.Float, default=0.0)
  attendance_records = db.relationship(
      'Attendance', backref='student', cascade='all, delete-orphan'
  )
  fee_records = db.relationship(
      'FeeRecord', backref='student', cascade='all, delete-orphan'
  )


class Attendance(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.String(50), nullable=False)
  status = db.Column(db.String(10), nullable=False)
  student_id = db.Column(
      db.Integer, db.ForeignKey('student.id'), nullable=False
  )


class FeeRecord(db.Model):
  id = db.Column(db.Integer, primary_key=True)
  date = db.Column(db.String(50), nullable=False)
  amount = db.Column(db.Float, nullable=False)
  status = db.Column(db.String(20), nullable=False)
  remarks = db.Column(db.String(200))
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
    total_fee = float(request.form.get('total_fee') or 0)
    paid_fee = float(request.form.get('paid_fee') or 0)

    new_student = Student(
        name=name,
        student_class=student_class,
        subject=subject,
        total_fee=total_fee,
        paid_fee=paid_fee,
    )
    db.session.add(new_student)
    db.session.commit()
    return redirect(url_for('index'))
  return render_template('add_student.html')


@app.route('/student/<int:id>', methods=['GET', 'POST'])
def student_detail(id):
  student = Student.query.get_or_404(id)
  if request.method == 'POST':
    if 'status' in request.form and 'amount' not in request.form:
      date = request.form.get('date') or datetime.now().strftime('%Y-%m-%d')
      status = request.form.get('status')
      if status:
        att = Attendance(date=date, status=status, student_id=student.id)
        db.session.add(att)
        db.session.commit()
    elif 'amount' in request.form:
      date = request.form.get('fee_date') or datetime.now().strftime('%Y-%m-%d')
      amount = float(request.form.get('amount') or 0)
      status = request.form.get('fee_status', 'Paid')
      remarks = request.form.get('remarks', '')

      fee_rec = FeeRecord(
          date=date,
          amount=amount,
          status=status,
          remarks=remarks,
          student_id=student.id,
      )
      db.session.add(fee_rec)
      student.paid_fee += amount
      db.session.commit()

    return redirect(url_for('student_detail', id=student.id))

  total_classes = len(student.attendance_records)
  present_count = sum(
      1 for a in student.attendance_records if a.status == 'Present'
  )
  absent_count = sum(
      1 for a in student.attendance_records if a.status == 'Absent'
  )
  due_fee = student.total_fee - student.paid_fee

  return render_template(
      'detail.html',
      student=student,
      total_classes=total_classes,
      present_count=present_count,
      absent_count=absent_count,
      due_fee=due_fee,
  )


@app.route('/delete/<int:id>')
def delete_student(id):
  student = Student.query.get_or_404(id)
  db.session.delete(student)
  db.session.commit()
  return redirect(url_for('index'))


if __name__ == '__main__':
  app.run(debug=True)