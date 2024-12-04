from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from flask import flash
from models import db, Transactions, User
from werkzeug.security import generate_password_hash, check_password_hash


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///D:/Financial_Management_System/instance/finance_tracker.db'
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
        transactions = Transactions.query.all()  
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
            new_transaction = Transactions(
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
from flask import render_template
from models import db, Transactions

@app.route('/summary')
def summary():
    # Fetch the sum of income and expenses by category
    category_expenses = db.session.query(Transactions.category, db.func.sum(Transactions.amount).label('total_amount'))\
        .filter(Transactions.type == 'Expense')\
        .group_by(Transactions.category).all()

    # Fetch the total income
    total_income_transactions = db.session.query(db.func.sum(Transactions.amount).label('total_income'))\
        .filter(Transactions.type == 'Income').scalar() or 0  # If no income, set it to 0

    # Fetch the monthly salary from the session
    monthly_salary = session.get('monthly_salary', 0)  # Default to 0 if not set

    # Add monthly salary to the total income from transactions
    total_income = monthly_salary + total_income_transactions

    # Prepare the data for categories and their corresponding totals
    categories = [expense.category for expense in category_expenses]
    amounts = [expense.total_amount for expense in category_expenses]

    # Prepare the data for Pie and Bar charts (or any other chart)
    chart_data = {
        'pie': {
            'labels': categories,
            'datasets': [{
                'label': 'Expenses',
                'data': amounts,
                'backgroundColor': ['#27ae60', '#3498db', '#f39c12', '#e74c3c', '#9b59b6'],
                'borderColor': '#2c3e50',
                'borderWidth': 1
            }]
        },
        'bar': {
            'labels': categories,
            'datasets': [{
                'label': 'Expenses',
                'data': amounts,
                'backgroundColor': '#1abc9c',
                'borderColor': '#16a085',
                'borderWidth': 1
            }]
        }
    }

    # Prepare the data for remaining budget and other calculations
    total_expenses = sum(amounts)
    remaining_budget = total_income - total_expenses

    # Render the template with the data
    return render_template('summary.html', 
                           category_expenses=category_expenses,
                           chart_data=chart_data,
                           total_income=total_income,
                           total_expenses=total_expenses,
                           remaining_budget=remaining_budget)




@app.route('/delete/<int:transaction_id>', methods=['POST'])
def delete_transaction(transaction_id):
    try:
        # Find the transaction by ID
        transaction = Transactions.query.get(transaction_id)
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
    transaction = Transactions.query.get(transaction_id)
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

        # Query the user by username from the 'users_new' table
        user = User.query.filter_by(username=username).first()

        if user and check_password_hash(user.password, password):  # Verify hashed password
            session['user_id'] = user.id  # Store user ID in session
            flash("Login successful!")
            return redirect(url_for('index'))  # Redirect to home page after login
        else:
            flash("Invalid username or password.")
            return render_template('login.html')  # Show login page again if credentials are incorrect

    return render_template('login.html')


from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from models import db, User  # Assuming you have a User model defined

@app.route('/sign_up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        # Get form data
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        username = request.form['username']
        email = request.form['email']
        phone = request.form['phone']
        company = request.form['company']
        dob = request.form['dob']  # Directly get the text input
        password = request.form['password']

        # Hash the password
        hashed_password = generate_password_hash(password)

        # Create a new user object
        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            company=company,
            dob=dob,  # Store as plain text
            password=hashed_password
        )

        try:
            # Add the user to the database
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully. Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error while inserting user: {e}")
            flash("An error occurred while creating your account.")
            return render_template('sign_up.html')

    return render_template('sign_up.html')




# Logout route
@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user ID from session
    return redirect(url_for('login'))

if __name__ == '__main__':
    app.run(debug=True)
