// Function to handle user login
function loginUser() {
    const username = document.getElementById('username').value;
    const password = document.getElementById('password').value;

    // Simple login validation (needs backend integration)
    if (username === 'testUser' && password === 'testPassword') {
        alert('Login successful!');
        window.location.href = 'dashboard.html';  // Redirect to a dashboard page
    } else {
        alert('Invalid credentials.');
    }
}

// Function to handle user registration
function registerUser() {
    const username = document.getElementById('new_username').value;
    const password = document.getElementById('new_password').value;

    // Simple registration (needs backend integration)
    alert('Registration successful!');
    window.location.href = 'login.html';  // Redirect to login page after registration
}

// Function to handle adding transactions (expenses/income)
function addTransaction() {
    const category = document.getElementById('category').value;
    const amount = parseFloat(document.getElementById('amount').value);
    const transactionType = document.querySelector('input[name="transaction_type"]:checked').value;

    // Call backend to add the transaction (This is a mock-up, needs integration with the backend)
    console.log(`Transaction: ${transactionType}, Category: ${category}, Amount: ${amount}`);
    alert('Transaction added!');
}

// Function to generate reports
function generateReport() {
    const period = document.getElementById('report_period').value;
    
    // Mock-up for report generation
    alert(`Generating ${period} report...`);
}

