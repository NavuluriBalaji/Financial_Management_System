from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Transactions(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.String(80), nullable=False)
    type = db.Column(db.String(10), nullable=False)  # 'Income' or 'Expense'
    category = db.Column(db.String(100), nullable=False)
    amount = db.Column(db.Float, nullable=False)
    description = db.Column(db.String(200), nullable=True)

    def __repr__(self):
        return f'<Transactions {self.category} - {self.amount}>'

class User(db.Model):
    __tablename__ = 'users_new'  # Update the table name to 'users_new'

    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(80), nullable=False)
    last_name = db.Column(db.String(80), nullable=False)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(15), nullable=True)
    company = db.Column(db.String(120), nullable=True)
    dob = db.Column(db.String(80), nullable=True)  # Store as text if needed
    password = db.Column(db.String(200), nullable=False)


    def __repr__(self):
        return f'<User {self.username}>'
