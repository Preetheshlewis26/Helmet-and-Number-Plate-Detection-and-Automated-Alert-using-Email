-- Create a new database
CREATE DATABASE vehicle_db;

-- Use the new database
USE vehicle_db;

-- Create the table for vehicle owners
CREATE TABLE vehicle_owners_list (
    id INT AUTO_INCREMENT PRIMARY KEY,
    vehicle_number VARCHAR(20) NOT NULL UNIQUE,
    owner_name VARCHAR(100),
    email varchar(30),
    phone_number VARCHAR(10)
);

CREATE TABLE vehicles_with_helmet (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vehicle_number VARCHAR(20)
);

CREATE TABLE vehicles_without_helmet (
        id INT AUTO_INCREMENT PRIMARY KEY,
        vehicle_number VARCHAR(20)
);

-- Verify the inserted data
SELECT * FROM vehicle_owners_list;
-- Verify the inserted data /stores without helmet
SELECT * FROM vehicles_without_helmet;
-- Verify the inserted data /stores with helmet
SELECT * FROM vehicles_with_helmet;


