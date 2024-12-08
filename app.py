from flask import Flask, render_template, request, redirect, url_for, session
import sqlite3
from datetime import datetime
from flask import flash
from models import db, Transactions, User
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
from flask import Flask

# app = Flask(
#     __name__,
#     template_folder="../templates",  # Adjust path to the templates folder
#     static_folder="../static"       # Adjust path to the static folder
# )

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
app.config['SQLALCHEMY_DATABASE_URI'] = f"sqlite:///{os.path.join(BASE_DIR, 'instance', 'finance_tracker.db')}"
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
app.config['SECRET_KEY'] = '3cdb21726265fc1194f5e0cc73a529112cc0477f2bc015e3'

db.init_app(app)
# initialize_routes(app)
# @app.before_first_request
def create_tables():    
    db.create_all()

@app.route('/')
def landing():
    return render_template('landing.html')

@app.route('/index', methods=['GET'])
def index():
    if 'user_id' in session:  
        user_id = session['user_id']
        transactions = Transactions.query.filter_by(user_id=user_id).all() 
        return render_template('index.html', transactions=transactions) 
    else:
        return render_template('landing.html') 


    
from flask import render_template, request, redirect, url_for, session

@app.route('/set_category_budget', methods=['POST'])
def set_category_budget():
    if request.method == 'POST':
        try:
            monthly_salary = float(request.form.get('monthly_salary', 0))
            food_budget = float(request.form.get('food_budget', 0))
            transport_budget = float(request.form.get('transport_budget', 0))
            entertainment_budget = float(request.form.get('entertainment_budget', 0))
            bills_budget = float(request.form.get('bills_budget', 0))
            other_budget = float(request.form.get('other_budget', 0))

            if monthly_salary < 0 or food_budget < 0 or transport_budget < 0 or entertainment_budget < 0 or bills_budget < 0 or other_budget < 0:
                return "Budget values cannot be negative.", 400

            session['monthly_salary'] = monthly_salary
            session['user_budgets'] = {
                'food': food_budget,
                'transport': transport_budget,
                'entertainment': entertainment_budget,
                'bills': bills_budget,
                'other': other_budget
            }

            total_budget = food_budget + transport_budget + entertainment_budget + bills_budget + other_budget
            remaining_budget = monthly_salary - total_budget
            session['remaining_budget'] = remaining_budget 

            return redirect(url_for('index'))

        except ValueError:
            return "Invalid input. Please ensure all fields contain valid numbers.", 400




def get_db_connection():
    conn = sqlite3.connect('budget_tracker.db') 
    conn.row_factory = sqlite3.Row
    return conn

def get_all_transactions():
    conn = get_db_connection()
    transactions = conn.execute('SELECT * FROM transactions').fetchall() 
    conn.close()
    return transactions

@app.route('/add_transaction', methods=['GET', 'POST'])
def add_transaction():
    if request.method == 'POST':
        try:
            date = request.form.get('date')
            transaction_type = request.form.get('type')
            category = request.form.get('category')
            amount = request.form.get('amount')
            description = request.form.get('description')

            if not date or not transaction_type or not category or not amount:
                flash('All fields are required!')
                return redirect(url_for('add_transaction'))

            amount = float(amount) 

            user_id = session['user_id'] 

            new_transaction = Transactions(
                user_id=user_id,
                date=date,
                type=transaction_type,
                category=category,
                amount=amount,
                description=description
            )

            db.session.add(new_transaction)
            db.session.commit()

            flash('Transaction added successfully!')
            return redirect(url_for('index')) 

        except Exception as e:
            flash(f'Error adding transaction: {e}')
            return redirect(url_for('add_transaction'))

    return render_template('add.html')

@app.route('/profile', methods=['GET'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    
    user = User.query.get(session['user_id']) 
    
    if not user:
        return redirect(url_for('login'))

    return render_template('profile.html', user=user)

@app.route('/edit_profile', methods=['GET', 'POST'])
def edit_profile():
    if 'user_id' not in session:
        return redirect(url_for('login')) 

    user = User.query.get(session['user_id']) 

    if request.method == 'POST':
        user.first_name = request.form['first_name']
        user.last_name = request.form['last_name']
        user.email = request.form['email']
        user.phone = request.form['phone']
        user.company = request.form['company']
        user.dob = request.form['dob']
        
        try:
            db.session.commit()
            flash("Profile updated successfully!", "success")
            return redirect(url_for('profile')) 
        except Exception as e:
            flash(f"Error updating profile: {e}", "error")
            return redirect(url_for('edit_profile')) 

    return render_template('edit_profile.html', user=user) 


from flask import render_template
from models import db, Transactions

@app.route('/summary')
def summary():
    # Ensure that the user is logged in
    if 'user_id' not in session:
        return redirect(url_for('login'))  # Redirect to login if not logged in

    # Fetch the logged-in user's ID from the session
    user_id = session['user_id']

    # Fetch the sum of income and expenses by category for the logged-in user
    category_expenses = db.session.query(Transactions.category, db.func.sum(Transactions.amount).label('total_amount'))\
        .filter(Transactions.type == 'Expense', Transactions.user_id == user_id)  \
        .group_by(Transactions.category).all()

    # Fetch the total income for the logged-in user
    total_income_transactions = db.session.query(db.func.sum(Transactions.amount).label('total_income'))\
        .filter(Transactions.type == 'Income', Transactions.user_id == user_id).scalar() or 0  

    # Get the user's monthly salary from session
    monthly_salary = session.get('monthly_salary', 0) 

    # Calculate total income (monthly salary + income from transactions)
    total_income = monthly_salary + total_income_transactions

    # Prepare the data for chart (pie and bar chart)
    categories = [expense.category for expense in category_expenses]
    amounts = [expense.total_amount for expense in category_expenses]

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
    transaction = Transactions.query.get(transaction_id)
    if not transaction:
        flash("Transaction not found.")
        return redirect(url_for('index'))

    if request.method == 'POST':
        try:
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

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        
        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            session['user_id'] = user.id 
            return redirect(url_for('index')) 
        
        return 'Invalid credentials. Please try again.'
    
    return render_template('login.html')



from flask import render_template, request, redirect, url_for
from werkzeug.security import generate_password_hash
from models import db, User  

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
        dob = request.form['dob']  
        password = request.form['password']


        hashed_password = generate_password_hash(password)

        new_user = User(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            phone=phone,
            company=company,
            dob=dob, 
            password=hashed_password
        )

        try:
            db.session.add(new_user)
            db.session.commit()
            flash("Account created successfully. Please log in.")
            return redirect(url_for('login'))
        except Exception as e:
            print(f"Error while inserting user: {e}")
            flash("An error occurred while creating your account.")
            return render_template('sign_up.html')

    return render_template('sign_up.html')




@app.route('/logout')
def logout():
    session.pop('user_id', None) 
    return redirect(url_for('login'))

if __name__ == '__main__':
    import init_db
    
    app.run(debug=True)
