# Create Database
CREATE DATABASE IF NOT EXISTS quantra_db;

# Use the database
USE quantra_db;

# Table -> audit_logs / user_logs
CREATE TABLE IF NOT EXISTS user_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    action VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Table -> system_logs
CREATE TABLE IF NOT EXISTS system_logs (
    id INT AUTO_INCREMENT PRIMARY KEY,
    level VARCHAR(20) NOT NULL,        -- DEBUG, INFO, WARNING, ERROR, CRITICAL
    message TEXT NOT NULL,
    context VARCHAR(100) DEFAULT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Table -> users
CREATE TABLE IF NOT EXISTS users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(30) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    role ENUM('User', 'Manager', 'Admin') DEFAULT 'User',
    locked BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

# Table -> settings
CREATE TABLE IF NOT EXISTS settings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    setting_key VARCHAR(100) UNIQUE NOT NULL,
    setting_value TEXT, # Can store large plain text
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);
    

# Table -> insurance
CREATE TABLE IF NOT EXISTS insurance (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    status ENUM('active', 'expired', 'cancelled') DEFAULT 'active',
    policy_type VARCHAR(100) NOT NULL,
    policy_type ENUM('health', 'life', 'property') NOT NULL,
    coverage_amount DECIMAL(10, 2) NOT NULL,
    premium_amount DECIMAL(10, 2) NOT NULL DEFAULT 0.00,       
    premium_frequency ENUM('monthly', 'quarterly', 'yearly') DEFAULT 'monthly',  
    next_premium_due DATE NOT NULL,                            
    last_paid_date DATE DEFAULT NULL, 
    start_date DATE NOT NULL,
    end_date DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

# Table -> accounts
CREATE TABLE IF NOT EXISTS accounts (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_type ENUM('savings', 'current', 'loan') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id)
);

# Table -> savings_accounts
CREATE TABLE IF NOT EXISTS savings_accounts (
    account_id INT PRIMARY KEY,
    balance DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

# Table -> current_accounts
CREATE TABLE IF NOT EXISTS current_accounts (
    account_id INT PRIMARY KEY,
    balance DECIMAL(15,2) NOT NULL,
    overdraft_limit DECIMAL(15,2) DEFAULT 0.00,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

# Table -> loan_accounts
CREATE TABLE IF NOT EXISTS loan_accounts (
    account_id INT PRIMARY KEY,
    loan_amount DECIMAL(15,2) NOT NULL,
    interest_rate DECIMAL(5,2) NOT NULL,
    due_date DATE NOT NULL,
    FOREIGN KEY (account_id) REFERENCES accounts(id) ON DELETE CASCADE
);

# Table -> transactions
CREATE TABLE IF NOT EXISTS transactions (          
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    account_id INT NOT NULL,
    amount DECIMAL(10, 2) NOT NULL,
    transaction_type ENUM('credit', 'debit') NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id),
    FOREIGN KEY (account_id) REFERENCES accounts(id)      
);

# Table -> notifications
CREATE TABLE IF NOT EXISTS notifications (
    id INT AUTO_INCREMENT PRIMARY KEY,
    user_id INT NOT NULL,
    message VARCHAR(255) NOT NULL,
    category VARCHAR(50),
    is_read BOOLEAN DEFAULT FALSE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
