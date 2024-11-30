from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from flask import flash
from models import db, Transaction, User
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/balaj/Downloads/Best/PersonalBudgetTracker-main/instance/budget_tracker.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
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
        try:
            # Get and convert the form data to float
            monthly_salary = float(request.form.get('monthly_salary', 0))
            food_budget = float(request.form.get('food_budget', 0))
            transport_budget = float(request.form.get('transport_budget', 0))
            entertainment_budget = float(request.form.get('entertainment_budget', 0))
            bills_budget = float(request.form.get('bills_budget', 0))
            other_budget = float(request.form.get('other_budget', 0))

            # Validate the input to ensure no negative values
            if monthly_salary < 0 or food_budget < 0 or transport_budget < 0 or entertainment_budget < 0 or bills_budget < 0 or other_budget < 0:
                return "Budget values cannot be negative.", 400

            # Store the data in session
            session['monthly_salary'] = monthly_salary
            session['user_budgets'] = {
                'food': food_budget,
                'transport': transport_budget,
                'entertainment': entertainment_budget,
                'bills': bills_budget,
                'other': other_budget
            }

            # Calculate remaining budget
            total_budget = food_budget + transport_budget + entertainment_budget + bills_budget + other_budget
            remaining_budget = monthly_salary - total_budget
            session['remaining_budget'] = remaining_budget  # Store in session

            # Redirect to the desired page after saving the budget
            return redirect(url_for('index'))

        except ValueError:
            # Handle invalid input
            return "Invalid input. Please ensure all fields contain valid numbers.", 400




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
    # transactions = get_all_transactions()  # Fetch all transactions
    return render_template('index.html')

# Add Transaction
@app.route('/add', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        try:
            # Retrieve form data
            date = request.form.get('date')
            type_ = request.form.get('type')
            category = request.form.get('category')
            amount = request.form.get('amount')
            description = request.form.get('description')

            # Validate required fields
            if not (date and type_ and category and amount):
                return 'All fields are required', 400

            # Ensure the amount is a valid float
            try:
                amount = float(amount)
            except ValueError:
                return 'Amount must be a number', 400

            # Ensure the user is logged in
            if 'user_id' not in session:
                return redirect(url_for('login'))

            # Get the logged-in user's ID
            user_id = session['user_id']

            # Create a new transaction object
            new_transaction = Transaction(
                # user_id=user_id,  # Associate with the logged-in user
                date=date,
                type=type_,
                category=category,
                amount=amount,
                description=description
            )

            # Add and commit the transaction to the database
            db.session.add(new_transaction)
            db.session.commit()

            # Redirect to the index page after success
            return redirect(url_for('index'))

        except Exception as e:
            print(f"Error while adding transaction: {e}")
            return 'An error occurred while adding the transaction', 500

    # Render the form if the request method is GET
    return render_template('add.html')



# Summary route
@app.route('/summary')
def summary():
    total_income = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Income').scalar() or 0
    total_expenses = db.session.query(db.func.sum(Transaction.amount)).filter_by(type='Expense').scalar() or 0
    balance = total_income - total_expenses
    return render_template('summary.html', total_income=total_income, total_expenses=total_expenses, balance=balance)

@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    try:
        # Find the transaction by ID
        transaction = Transaction.query.get(transaction_id)
        if transaction:
            db.session.delete(transaction)
            db.session.commit()
            flash("Transaction deleted successfully.")
        else:
            flash("Transaction not found.")
    except Exception as e:
        print(f"Error deleting transaction: {e}")
        flash("An error occurred while deleting the transaction.")
    return redirect(url_for('index'))

@app.route('/edit/<int:transaction_id>', methods=['GET', 'POST'])
def edit_transaction(transaction_id):
    # Find the transaction
    transaction = Transaction.query.get(transaction_id)
    if not transaction:
        flash("Transaction not found.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
            # Update transaction details
            transaction.date = request.form['date']
            transaction.type = request.form['type']
            transaction.category = request.form['category']
            transaction.amount = float(request.form['amount'])
            transaction.description = request.form['description']
            db.session.commit()
            flash("Transaction updated successfully.")
            return redirect(url_for('index'))
        except Exception as e:
            print(f"Error updating transaction: {e}")
            flash("An error occurred while updating the transaction.")
    return render_template('edit_transaction.html', transaction=transaction)

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
