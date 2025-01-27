
# Personal Income and Expense Tracker

This is a Python web application built using **Flask**, **SQLAlchemy**, and **SQLite** to track personal income and expenses. The application allows users to add transactions, view income/expense summaries, and provides a responsive user interface using **Bootstrap**. It ensures data validation and error handling for a smooth and robust user experience.

## Table of Contents

- [Features](#features)
- [Technologies](#technologies)
- [Installation](#installation)
- [Usage](#usage)
- [License](#license)
- [Contributors](#contributors)

## Features

- **Add Transactions**: Users can add new transactions, including the amount, type (income/expense), and description.
- **View Summaries**: Displays a summary of income and expenses, with totals for each category.
- **Responsive UI**: The web application uses **Bootstrap** to provide a mobile-friendly and user-friendly interface.
- **Data Validation**: Ensures that only valid data is entered for transactions, preventing errors.
- **Error Handling**: Proper error handling is implemented for smooth performance even in case of invalid input or unexpected errors.

## Technologies

- **Python**: The backend programming language.
- **Flask**: Micro web framework used to build the application.
- **SQLAlchemy**: ORM (Object-Relational Mapping) tool for managing the database.
- **SQLite**: A lightweight database engine for storing transaction data.
- **Bootstrap**: Frontend framework for designing the responsive user interface.
- **Jinja2**: Templating engine used by Flask for rendering HTML pages.

## Installation

To set up the application locally, follow these steps:

### 1. Clone the Repository
```bash
git clone https://github.com/yourusername/personal-income-expense-tracker.git
cd personal-income-expense-tracker
```

### 2. Create a Virtual Environment (Optional but recommended)
```bash
python -m venv venv
```

### 3. Activate the Virtual Environment
- For Windows:
  ```bash
  venv\Scriptsctivate
  ```
- For macOS/Linux:
  ```bash
  source venv/bin/activate
  ```

### 4. Install Dependencies
```bash
pip install -r requirements.txt
```

### 5. Set Up the Database
The application uses **SQLite** to store data. Run the following command to create the necessary database and tables:
```bash
python app.py
```

### 6. Run the Application
To start the Flask web app, run:
```bash
python app.py
```
Visit `http://127.0.0.1:5000` in your web browser to access the application.

## Usage

- **Add Transaction**: Use the "Add Transaction" form to input transaction details (amount, type, description).
- **View Summaries**: Navigate to the "Summary" page to see the breakdown of income and expenses.
- **Responsive UI**: The app adapts to both desktop and mobile screens, providing a smooth experience.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Contributors

- **Your Name** - Navuluri Balaji

