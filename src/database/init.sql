DROP DATABASE IF EXISTS ats_db;

CREATE DATABASE IF NOT EXISTS ats_db;

CREATE USER IF NOT EXISTS 'asepjajang'@'%' IDENTIFIED BY 'asepjajang123';
CREATE USER IF NOT EXISTS 'asepjajang'@'localhost' IDENTIFIED BY 'asepjajang123';

GRANT ALL PRIVILEGES ON ats_db.* TO 'asepjajang'@'%';
GRANT ALL PRIVILEGES ON ats_db.* TO 'asepjajang'@'localhost';

FLUSH PRIVILEGES;

USE ats_db;

CREATE TABLE IF NOT EXISTS ApplicantProfile (
    applicant_id INT AUTO_INCREMENT PRIMARY KEY,
    first_name VARCHAR(50) DEFAULT NULL,
    last_name VARCHAR(50) DEFAULT NULL,
    address VARCHAR(50) DEFAULT NULL,
    date_of_birth DATE DEFAULT NULL,
    phone_number VARCHAR(20) DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS ApplicationDetail (
    application_id INT AUTO_INCREMENT PRIMARY KEY,
    applicant_id INT NOT NULL,
    cv_path TEXT,
    application_role VARCHAR(100) DEFAULT NULL,
    FOREIGN KEY (applicant_id) REFERENCES ApplicantProfile(applicant_id) 
        ON DELETE SET NULL
);