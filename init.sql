CREATE DATABASE IF NOT EXISTS crud_db;
USE crud_db;

CREATE TABLE IF NOT EXISTS tbl_user (
                user_id INT AUTO_INCREMENT PRIMARY KEY,
                user_name VARCHAR(45) NOT NULL,
                user_email VARCHAR(45) NOT NULL);

-- Insert sample data
INSERT INTO tbl_user (name, email) VALUES 
('Pankaj Kumar', 'pankaj@example.com'),
('Jane Doe', 'jane@example.com')
ON DUPLICATE KEY UPDATE name=name;
