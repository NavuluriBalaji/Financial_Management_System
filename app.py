from flask import Flask, render_template, request, redirect, url_for
from models import db, Transaction

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///budget_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

@app.before_request
def create_tables():
    db.create_all()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        date = request.form['date']
        type_ = request.form['type']
        category = request.form['category']
        amount = request.form['amount']
        description = request.form['description']

        if not (date and type_ and category and amount):
            return 'All fields are required'

        try:
            amount = float(amount)
        except ValueError:
            return 'Amount must be a number'

        new_transaction = Transaction(date=date, type=type_, category=category, amount=amount, description=description)
        db.session.add(new_transaction)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('add.html')

@app.route('/summary')
def summary():
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Income').scalar() or 0
    total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Expense').scalar() or 0
    balance = total_income - total_expenses
    return render_template('summary.html', total_income=total_income, total_expenses=total_expenses, balance=balance)

if __name__ == '__main__':
    app.run(debug=True)
