CREATE DATABASE crm;
USE crm;

CREATE TABLE quotations (
  id INT AUTO_INCREMENT PRIMARY KEY,
  quotation_no VARCHAR(50),
  company_name VARCHAR(100),
  project VARCHAR(100),
  quoted_price DECIMAL(10,2),
  status VARCHAR(20),
  open_date DATE,
  close_date DATE
);
