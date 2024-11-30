from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
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

@app.route('/')
def landing():
    return render_template('landing.html')

# Home route (Index page)
@app.route('/index',methods=['GET'])
def index():
    if 'user_id' in session:  # Check if the user is logged in
        # Fetch transactions for the logged-in user
        user_id = session['user_id']
        transactions = Transaction.query.all()  
        return render_template('index.html', transactions=transactions)  # Show transactions page
    else:
        return render_template('landing.html')  # Show landing page if not logged in
    
from flask import render_template, request, redirect, url_for, session

@app.route('/set_category_budget', methods=['POST'])
def set_category_budget():
    if request.method == 'POST':
        # Capture the budget data from the form
        food_budget = request.form.get('food_budget')
        transport_budget = request.form.get('transport_budget')
        entertainment_budget = request.form.get('entertainment_budget')
        bills_budget = request.form.get('bills_budget')
        other_budget = request.form.get('other_budget')
        
        # Store the budgets in the session or database
        # For example, storing in the session:
        session['user_budgets'] = {
            'food': food_budget,
            'transport': transport_budget,
            'entertainment': entertainment_budget,
            'bills': bills_budget,
            'other': other_budget
        }
        
        # Redirect to another page or back to the main page after submission
        return redirect(url_for('index'))  # You can change 'index' to the page you'd like to redirect to

def get_db_connection():
    conn = sqlite3.connect('budget_tracker.db')  # Replace with your actual database file or connection details
    conn.row_factory = sqlite3.Row
    return conn

def get_all_transactions():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions').fetchall() 
    conn.close()
    return transactions

# Route for the transaction table
@app.route('/transaction-table')
def transaction_table():
    transactions = get_all_transactions()  # Fetch all transactions
    return render_template('transaction_table.html', transactions=transactions)


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
