CREATE DATABASE IF NOT EXISTS ats_db;
USE ats_db;

CREATE TABLE IF NOT EXISTS ApplicantProfile (
    applicant_id INT AUTO_INCREMENT PRIMARY KEY,
    full_name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    phone VARCHAR(20),
    address TEXT,
    date_of_birth DATE,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS ApplicationDetail (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    position VARCHAR(255) NOT NULL,
    company VARCHAR(255),
    cv_path VARCHAR(500) NOT NULL,
    application_date DATE DEFAULT (CURRENT_DATE),
    status ENUM('pending', 'reviewed', 'shortlisted', 'rejected', 'hired') DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
    
    FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) 
        ON DELETE CASCADE ON UPDATE CASCADE,
    
    INDEX idx_applicant_id (applicant_id),
    INDEX idx_position (position),
    INDEX idx_company (company),
    INDEX idx_status (status)
);

CREATE INDEX idx_email ON ApplicantProfile(email);
CREATE INDEX idx_full_name ON ApplicantProfile(full_name);
CREATE INDEX idx_cv_path ON ApplicationDetail(cv_path);