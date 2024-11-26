from flask import Flask, render_template, request, redirect, url_for, session
from models import db, Transaction, User
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/balaj/Downloads/Best/PersonalBudgetTracker-main/instance/budget_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = '3cdb21726265fc1194f5e0cc73a529112cc0477f2bc015e3'  # Used for session management

db.init_app(app)

# @app.before_first_request
def create_tables():    
    db.create_all()

# Home route (Index page)
@app.route('/')
def index():
    if 'user_id' in session:
        transactions = Transaction.query.all()  # Fetch all transactions if logged in
        return render_template('index.html', transactions=transactions)
    return redirect(url_for('login'))

# Add Transaction
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

# Summary route
@app.route('/summary')
def summary():
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Income').scalar() or 0
    total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Expense').scalar() or 0
    balance = total_income - total_expenses
    return render_template('summary.html', total_income=total_income, total_expenses=total_expenses, balance=balance)

# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id  # Store user ID in session
            return redirect(url_for('index'))  # Redirect to home page after login
        
        return 'Invalid credentials. Please try again.'
    
    return render_template('login.html')

@app.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        # Hash the password before storing it
        hashed_password = generate_password_hash(password)

        new_user = User(username=username, password=hashed_password)
        db.session.add(new_user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('sign_up.html')

# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
