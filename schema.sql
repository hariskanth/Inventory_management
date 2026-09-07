-- ============================================================
-- STOCKPRO INVENTORY MANAGEMENT SYSTEM
-- Database: INVENTORY_DB
-- ============================================================

-- Create the database
DROP DATABASE IF EXISTS INVENTORY_DB;
CREATE DATABASE IF NOT EXISTS INVENTORY_DB;
USE INVENTORY_DB;

-- ============================================================
-- TABLE: USERS
-- ============================================================
CREATE TABLE IF NOT EXISTS USERS (
    USER_ID INT PRIMARY KEY AUTO_INCREMENT,
    USERNAME VARCHAR(50) NOT NULL UNIQUE,
    PASSWORD VARCHAR(255) NOT NULL,
    FULL_NAME VARCHAR(100) NOT NULL,
    ROLE ENUM('ADMIN', 'MANAGER', 'STAFF') NOT NULL DEFAULT 'STAFF',
    STATUS ENUM('ACTIVE', 'INACTIVE') NOT NULL DEFAULT 'ACTIVE'
);

-- ============================================================
-- TABLE: WAREHOUSE
-- ============================================================
CREATE TABLE IF NOT EXISTS WAREHOUSE (
    WAREHOUSE_ID INT PRIMARY KEY AUTO_INCREMENT,
    WAREHOUSE_NAME VARCHAR(100) NOT NULL,
    LOCATION VARCHAR(200),
    CAPACITY INT DEFAULT 0
);

-- ============================================================
-- TABLE: BIN_LOCATION
-- ============================================================
CREATE TABLE IF NOT EXISTS BIN_LOCATION (
    BIN_ID INT PRIMARY KEY AUTO_INCREMENT,
    WAREHOUSE_ID INT NOT NULL,
    BIN_NAME VARCHAR(100) NOT NULL,
    CAPACITY INT DEFAULT 0,
    DESCRIPTION VARCHAR(255),
    FOREIGN KEY (WAREHOUSE_ID) REFERENCES WAREHOUSE(WAREHOUSE_ID) ON DELETE CASCADE,
    UNIQUE KEY unique_bin_name_per_warehouse (WAREHOUSE_ID, BIN_NAME)
);

-- ============================================================
-- TABLE: PRODUCTS
-- ============================================================
CREATE TABLE IF NOT EXISTS PRODUCTS (
    PRODUCT_ID INT PRIMARY KEY AUTO_INCREMENT,
    PRODUCT_NAME VARCHAR(200) NOT NULL,
    CATEGORY VARCHAR(100) NOT NULL,
    UNIT VARCHAR(50) NOT NULL,
    UNIT_PRICE DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    MIN_STOCK INT NOT NULL DEFAULT 0,
    INDEX idx_category (CATEGORY)
);

-- ============================================================
-- TABLE: PRODUCT_WAREHOUSE_STOCK
-- ============================================================
CREATE TABLE IF NOT EXISTS PRODUCT_WAREHOUSE_STOCK (
    PRODUCT_ID INT NOT NULL,
    WAREHOUSE_ID INT NOT NULL,
    BIN_ID INT NOT NULL,
    STOCK_QTY INT NOT NULL DEFAULT 0,
    PRIMARY KEY (PRODUCT_ID, WAREHOUSE_ID, BIN_ID),
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID) ON DELETE CASCADE,
    FOREIGN KEY (WAREHOUSE_ID) REFERENCES WAREHOUSE(WAREHOUSE_ID) ON DELETE CASCADE,
    FOREIGN KEY (BIN_ID) REFERENCES BIN_LOCATION(BIN_ID) ON DELETE CASCADE,
    INDEX idx_warehouse (WAREHOUSE_ID),
    INDEX idx_bin (BIN_ID)
);

-- ============================================================
-- TABLE: SUPPLIER
-- ============================================================
CREATE TABLE IF NOT EXISTS SUPPLIER (
    SUPPLIER_ID INT PRIMARY KEY AUTO_INCREMENT,
    SUPPLIER_NAME VARCHAR(200) NOT NULL,
    ADDRESS TEXT,
    LOCATION VARCHAR(100) NOT NULL,
    PRODUCT_ID INT,
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID) ON DELETE SET NULL,
    INDEX idx_product (PRODUCT_ID)
);

-- ============================================================
-- TABLE: STOCK_TRANSACTIONS
-- ============================================================
CREATE TABLE IF NOT EXISTS STOCK_TRANSACTIONS (
    TRANSACTION_ID INT PRIMARY KEY AUTO_INCREMENT,
    PRODUCT_ID INT NOT NULL,
    USER_ID INT NOT NULL,
    TRANSACTION_TYPE ENUM('STOCK IN', 'STOCK OUT') NOT NULL,
    QUANTITY INT NOT NULL,
    UNIT_PRICE DECIMAL(12,2) NOT NULL DEFAULT 0.00,
    TOTAL_VALUE DECIMAL(14,2) NOT NULL DEFAULT 0.00,
    SOURCE_TYPE ENUM('SUPPLIER', 'WAREHOUSE', 'CUSTOMER') NOT NULL,
    SOURCE_SUPPLIER_ID INT NULL,
    SOURCE_WAREHOUSE_ID INT NULL,
    DESTINATION_TYPE ENUM('SUPPLIER', 'WAREHOUSE', 'CUSTOMER') NOT NULL,
    DESTINATION_WAREHOUSE_ID INT NULL,
    FOREIGN KEY (PRODUCT_ID) REFERENCES PRODUCTS(PRODUCT_ID) ON DELETE CASCADE,
    FOREIGN KEY (USER_ID) REFERENCES USERS(USER_ID),
    FOREIGN KEY (SOURCE_SUPPLIER_ID) REFERENCES SUPPLIER(SUPPLIER_ID) ON DELETE SET NULL,
    FOREIGN KEY (SOURCE_WAREHOUSE_ID) REFERENCES WAREHOUSE(WAREHOUSE_ID) ON DELETE SET NULL,
    FOREIGN KEY (DESTINATION_WAREHOUSE_ID) REFERENCES WAREHOUSE(WAREHOUSE_ID) ON DELETE SET NULL,
    INDEX idx_transaction_type (TRANSACTION_TYPE),
    INDEX idx_product (PRODUCT_ID)
);

-- ============================================================
-- SAMPLE DATA
-- ============================================================

-- Users
INSERT INTO USERS (USERNAME, PASSWORD, FULL_NAME, ROLE, STATUS) VALUES
('Haris', '1234', 'System Administrator', 'ADMIN', 'ACTIVE'),
('John', '1234', 'Stock Manager', 'MANAGER', 'ACTIVE'),
('Alex', '1234', 'Staff', 'STAFF', 'ACTIVE');

-- ============================================================
-- 8 WAREHOUSES
-- ============================================================
INSERT INTO WAREHOUSE (WAREHOUSE_NAME, LOCATION, CAPACITY) VALUES
('Warehouse 1', 'Mumbai - Andheri East', 4000),
('Warehouse 2', 'Mumbai - Navi Mumbai', 4000),
('Warehouse 3', 'Pune - Hinjewadi', 4000),
('Warehouse 4', 'Delhi - Okhla', 4000),
('Warehouse 5', 'Bangalore - Whitefield', 4000),
('Warehouse 6', 'Chennai - Guindy', 4000),
('Warehouse 7', 'Hyderabad - Gachibowli', 4000),
('Warehouse 8', 'Kolkata - Salt Lake', 4000);

-- ============================================================
-- BIN LOCATIONS with different names and category assignments
-- ============================================================

-- Warehouse 1
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(1, 'Electronic Shelf A1', 1000, 'Electronics'),
(1, 'Garment Rack B1', 1000, 'Garments'),
(1, 'Food Storage C1', 1000, 'Food Items'),
(1, 'Perishable Cold D1', 1000, 'Perishable');

-- Warehouse 2
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(2, 'Perishable Zone A2', 1000, 'Perishable'),
(2, 'Electronics Bay B2', 1000, 'Electronics'),
(2, 'Food Section C2', 1000, 'Food Items'),
(2, 'Garment Area D2', 1000, 'Garments');

-- Warehouse 3
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(3, 'Food Warehouse E3', 1000, 'Food Items'),
(3, 'Electronics Storage F3', 1000, 'Electronics'),
(3, 'Perishable Cooler G3', 1000, 'Perishable'),
(3, 'Garment Hall H3', 1000, 'Garments');

-- Warehouse 4
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(4, 'Garment Floor I4', 1000, 'Garments'),
(4, 'Food Pantry J4', 1000, 'Food Items'),
(4, 'Electronics Tower K4', 1000, 'Electronics'),
(4, 'Perishable Fridge L4', 1000, 'Perishable');

-- Warehouse 5
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(5, 'Electronics Wing M5', 1000, 'Electronics'),
(5, 'Perishable Unit N5', 1000, 'Perishable'),
(5, 'Garment Section O5', 1000, 'Garments'),
(5, 'Food Depot P5', 1000, 'Food Items');

-- Warehouse 6
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(6, 'Food Center Q6', 1000, 'Food Items'),
(6, 'Garment Store R6', 1000, 'Garments'),
(6, 'Perishable Chamber S6', 1000, 'Perishable'),
(6, 'Electronics Hub T6', 1000, 'Electronics');

-- Warehouse 7
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(7, 'Perishable Vault U7', 1000, 'Perishable'),
(7, 'Food Warehouse V7', 1000, 'Food Items'),
(7, 'Electronics Center W7', 1000, 'Electronics'),
(7, 'Garment Zone X7', 1000, 'Garments');

-- Warehouse 8
INSERT INTO BIN_LOCATION (WAREHOUSE_ID, BIN_NAME, CAPACITY, DESCRIPTION) VALUES
(8, 'Garment Plaza Y8', 1000, 'Garments'),
(8, 'Electronics Plaza Z8', 1000, 'Electronics'),
(8, 'Food Plaza A8', 1000, 'Food Items'),
(8, 'Perishable Plaza B8', 1000, 'Perishable');

-- ============================================================
-- 10 PRODUCTS across 4 categories
-- ============================================================
INSERT INTO PRODUCTS (PRODUCT_NAME, CATEGORY, UNIT, UNIT_PRICE, MIN_STOCK) VALUES
('Smartphone X', 'Electronics', 'Piece', 499.99, 20),
('Laptop Pro', 'Electronics', 'Piece', 899.99, 10),
('Wireless Earbuds', 'Electronics', 'Piece', 59.99, 25),
('T-Shirt Cotton', 'Garments', 'Piece', 19.99, 50),
('Jeans Blue', 'Garments', 'Piece', 49.99, 30),
('Winter Jacket', 'Garments', 'Piece', 79.99, 15),
('Rice 5kg Pack', 'Food Items', 'Packet', 12.99, 100),
('Wheat Flour 5kg', 'Food Items', 'Packet', 9.99, 80),
('Milk 1L', 'Perishable', 'Packet', 3.99, 50),
('Butter 500g', 'Perishable', 'Packet', 5.99, 30);

-- ============================================================
-- 20 SUPPLIERS (2 per product)
-- ============================================================
INSERT INTO SUPPLIER (SUPPLIER_NAME, ADDRESS, LOCATION, PRODUCT_ID) VALUES
('Tech Distributors Inc', '123 Tech Park, Mumbai', 'Mumbai', 1),
('Mobile World Supply', '456 Mobile Road, Pune', 'Pune', 1),
('Global Electronics Ltd', '456 Digital Road, Pune', 'Pune', 2),
('Computer Hub Corp', '789 IT Street, Bangalore', 'Bangalore', 2),
('Audio World Ltd', '159 Sound Street, Bangalore', 'Bangalore', 3),
('SoundTech Solutions', '753 Audio Lane, Chennai', 'Chennai', 3),
('Fashion Hub', '789 Style Street, Delhi', 'Delhi', 4),
('Cotton World Ltd', '321 Fabric Lane, Bangalore', 'Bangalore', 4),
('Denim World', '321 Fabric Lane, Bangalore', 'Bangalore', 5),
('Jeans Factory Co', '654 Denim Road, Mumbai', 'Mumbai', 5),
('Winter Wear Co', '753 Wool Road, Shimla', 'Shimla', 6),
('Jacket Masters Ltd', '987 Outerwear Avenue, Delhi', 'Delhi', 6),
('Agro Foods Ltd', '654 Farm Road, Nagpur', 'Nagpur', 7),
('Rice Exporters Corp', '321 Grain Street, Kolkata', 'Kolkata', 7),
('Flour Mills Corp', '987 Grain Avenue, Indore', 'Indore', 8),
('Wheat Products Ltd', '456 Flour Road, Bhopal', 'Bhopal', 8),
('Dairy Products Co', '741 Milk Street, Surat', 'Surat', 9),
('Milk Fresh Ltd', '852 Dairy Road, Jaipur', 'Jaipur', 9),
('Fresh Dairy Ltd', '852 Cream Road, Jaipur', 'Jaipur', 10),
('Butter World Corp', '369 Creamy Lane, Delhi', 'Delhi', 10);

-- ============================================================
-- STOCK ALLOCATION - Each INSERT statement separated by semicolon
-- ============================================================

-- Product 1: Smartphone X (Electronics)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(1, 1, 1, 100),
(1, 2, 6, 50),
(1, 3, 10, 75),
(1, 4, 15, 60),
(1, 5, 17, 80),
(1, 6, 24, 40),
(1, 7, 27, 55),
(1, 8, 30, 45);

-- Product 2: Laptop Pro (Electronics)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(2, 1, 1, 75),
(2, 3, 10, 40),
(2, 5, 17, 60),
(2, 8, 30, 50);

-- Product 3: Wireless Earbuds (Electronics)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(3, 2, 6, 120),
(3, 4, 15, 60),
(3, 6, 24, 90),
(3, 7, 27, 45);

-- Product 4: T-Shirt Cotton (Garments)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(4, 1, 2, 300),
(4, 3, 12, 150),
(4, 5, 19, 200),
(4, 7, 28, 100);

-- Product 5: Jeans Blue (Garments)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(5, 2, 8, 200),
(5, 4, 13, 300),
(5, 6, 22, 100),
(5, 8, 29, 150);

-- Product 6: Winter Jacket (Garments)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(6, 1, 2, 90),
(6, 3, 12, 45),
(6, 5, 19, 70),
(6, 7, 28, 35);

-- Product 7: Rice 5kg Pack (Food Items)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(7, 1, 3, 500),
(7, 3, 9, 300),
(7, 5, 20, 400),
(7, 7, 26, 250);

-- Product 8: Wheat Flour 5kg (Food Items)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(8, 2, 7, 400),
(8, 4, 14, 600),
(8, 6, 21, 200),
(8, 8, 31, 300);

-- Product 9: Milk 1L (Perishable)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(9, 1, 4, 150),
(9, 3, 11, 200),
(9, 5, 18, 100),
(9, 7, 25, 120);

-- Product 10: Butter 500g (Perishable)
INSERT INTO PRODUCT_WAREHOUSE_STOCK (PRODUCT_ID, WAREHOUSE_ID, BIN_ID, STOCK_QTY) VALUES
(10, 2, 5, 150),
(10, 4, 16, 75),
(10, 6, 23, 100),
(10, 8, 32, 80);

-- ============================================================
-- SAMPLE STOCK TRANSACTIONS
-- ============================================================
INSERT INTO STOCK_TRANSACTIONS
(PRODUCT_ID, USER_ID, TRANSACTION_TYPE, QUANTITY, UNIT_PRICE, TOTAL_VALUE,
 SOURCE_TYPE, SOURCE_SUPPLIER_ID, DESTINATION_TYPE, DESTINATION_WAREHOUSE_ID)
VALUES
(1, 1, 'STOCK IN', 50, 499.99, 24999.50, 'SUPPLIER', 1, 'WAREHOUSE', 1),
(1, 1, 'STOCK IN', 30, 499.99, 14999.70, 'SUPPLIER', 2, 'WAREHOUSE', 2),
(2, 1, 'STOCK IN', 25, 899.99, 22499.75, 'SUPPLIER', 3, 'WAREHOUSE', 1),
(3, 1, 'STOCK IN', 100, 59.99, 5999.00, 'SUPPLIER', 5, 'WAREHOUSE', 2),
(4, 1, 'STOCK IN', 150, 19.99, 2998.50, 'SUPPLIER', 7, 'WAREHOUSE', 1),
(4, 2, 'STOCK IN', 100, 19.99, 1999.00, 'SUPPLIER', 8, 'WAREHOUSE', 3),
(5, 2, 'STOCK IN', 80, 49.99, 3999.20, 'SUPPLIER', 9, 'WAREHOUSE', 2),
(6, 2, 'STOCK IN', 50, 79.99, 3999.50, 'SUPPLIER', 11, 'WAREHOUSE', 1),
(7, 2, 'STOCK IN', 200, 12.99, 2598.00, 'SUPPLIER', 13, 'WAREHOUSE', 1),
(7, 2, 'STOCK IN', 150, 12.99, 1948.50, 'SUPPLIER', 14, 'WAREHOUSE', 3),
(8, 2, 'STOCK IN', 100, 9.99, 999.00, 'SUPPLIER', 15, 'WAREHOUSE', 2),
(9, 2, 'STOCK IN', 80, 3.99, 319.20, 'SUPPLIER', 17, 'WAREHOUSE', 1),
(9, 2, 'STOCK IN', 50, 3.99, 199.50, 'SUPPLIER', 18, 'WAREHOUSE', 3),
(10, 2, 'STOCK IN', 60, 5.99, 359.40, 'SUPPLIER', 19, 'WAREHOUSE', 2),

(1, 2, 'STOCK OUT', 10, 499.99, 4999.90, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(1, 2, 'STOCK OUT', 15, 499.99, 7499.85, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(2, 2, 'STOCK OUT', 5, 899.99, 4499.95, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(3, 2, 'STOCK OUT', 20, 59.99, 1199.80, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(4, 2, 'STOCK OUT', 30, 19.99, 599.70, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(4, 2, 'STOCK OUT', 20, 19.99, 399.80, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(5, 2, 'STOCK OUT', 15, 49.99, 749.85, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(6, 2, 'STOCK OUT', 10, 79.99, 799.90, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(7, 2, 'STOCK OUT', 50, 12.99, 649.50, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),
(8, 2, 'STOCK OUT', 30, 9.99, 299.70, 'WAREHOUSE', NULL, 'CUSTOMER', NULL),

-- Warehouse Transfer transactions
(1, 1, 'STOCK OUT', 20, 499.99, 9999.80, 'WAREHOUSE', NULL, 'WAREHOUSE', 2),
(1, 1, 'STOCK IN', 20, 499.99, 9999.80, 'WAREHOUSE', 1, 'WAREHOUSE', 2),
(4, 1, 'STOCK OUT', 30, 19.99, 599.70, 'WAREHOUSE', NULL, 'WAREHOUSE', 5),
(4, 1, 'STOCK IN', 30, 19.99, 599.70, 'WAREHOUSE', 3, 'WAREHOUSE', 5),
(7, 1, 'STOCK OUT', 40, 12.99, 519.60, 'WAREHOUSE', NULL, 'WAREHOUSE', 6),
(7, 1, 'STOCK IN', 40, 12.99, 519.60, 'WAREHOUSE', 2, 'WAREHOUSE', 6);

-- ============================================================
-- HELPER VIEWS FOR REPORTS
-- ============================================================

-- View: Warehouse Utilization
CREATE OR REPLACE VIEW V_WAREHOUSE_UTILIZATION AS
SELECT
    W.WAREHOUSE_ID,
    W.WAREHOUSE_NAME,
    W.LOCATION,
    W.CAPACITY AS TOTAL_CAPACITY,
    COALESCE(SUM(PWS.STOCK_QTY), 0) AS CURRENT_STOCK,
    ROUND(COALESCE(SUM(PWS.STOCK_QTY), 0) / NULLIF(W.CAPACITY, 0) * 100, 2) AS UTILIZATION_PERCENTAGE,
    W.CAPACITY - COALESCE(SUM(PWS.STOCK_QTY), 0) AS AVAILABLE_SPACE
FROM WAREHOUSE W
LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.WAREHOUSE_ID = W.WAREHOUSE_ID
GROUP BY W.WAREHOUSE_ID, W.WAREHOUSE_NAME, W.LOCATION, W.CAPACITY;

-- View: Bin Utilization
CREATE OR REPLACE VIEW V_BIN_UTILIZATION AS
SELECT
    B.BIN_ID,
    B.BIN_NAME,
    B.WAREHOUSE_ID,
    B.CAPACITY,
    COALESCE(SUM(PWS.STOCK_QTY), 0) AS CURRENT_STOCK,
    ROUND(COALESCE(SUM(PWS.STOCK_QTY), 0) / NULLIF(B.CAPACITY, 0) * 100, 2) AS UTILIZATION_PERCENTAGE,
    B.DESCRIPTION AS CATEGORY,
    CASE
        WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) = 0 THEN 'Empty'
        WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) < B.CAPACITY * 0.3 THEN 'Low Usage'
        WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) < B.CAPACITY * 0.7 THEN 'Medium Usage'
        ELSE 'High Usage'
    END AS USAGE_STATUS
FROM BIN_LOCATION B
LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.BIN_ID = B.BIN_ID
GROUP BY B.BIN_ID, B.BIN_NAME, B.WAREHOUSE_ID, B.CAPACITY, B.DESCRIPTION;

-- View: Low Stock Products
CREATE OR REPLACE VIEW V_LOW_STOCK_PRODUCTS AS
SELECT
    P.PRODUCT_ID,
    P.PRODUCT_NAME,
    P.CATEGORY,
    P.UNIT,
    COALESCE(SUM(PWS.STOCK_QTY), 0) AS STOCK_QTY,
    P.MIN_STOCK,
    CASE
        WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) = 0 THEN 'OUT OF STOCK'
        WHEN COALESCE(SUM(PWS.STOCK_QTY), 0) <= P.MIN_STOCK THEN 'LOW STOCK'
        ELSE 'IN STOCK'
    END AS STOCK_STATUS
FROM PRODUCTS P
LEFT JOIN PRODUCT_WAREHOUSE_STOCK PWS ON PWS.PRODUCT_ID = P.PRODUCT_ID
GROUP BY P.PRODUCT_ID, P.PRODUCT_NAME, P.CATEGORY, P.UNIT, P.MIN_STOCK
HAVING COALESCE(SUM(PWS.STOCK_QTY), 0) <= P.MIN_STOCK;