-- =========================================================
-- PART 1: NORMALIZED SCHEMA (3NF) — typical OLTP design
-- =========================================================

CREATE TABLE department (
    department_id   INTEGER PRIMARY KEY,
    department_name TEXT NOT NULL
);

CREATE TABLE category (
    category_id     INTEGER PRIMARY KEY,
    category_name   TEXT NOT NULL,
    department_id   INTEGER NOT NULL REFERENCES department(department_id)
);

CREATE TABLE product (
    product_id      INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category_id     INTEGER NOT NULL REFERENCES category(category_id),
    unit_price      NUMERIC(10,2) NOT NULL
);

CREATE TABLE city (
    city_id         INTEGER PRIMARY KEY,
    city_name       TEXT NOT NULL,
    region          TEXT NOT NULL
);

CREATE TABLE customer (
    customer_id     INTEGER PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    city_id         INTEGER NOT NULL REFERENCES city(city_id)
);

CREATE TABLE orders (
    order_id        INTEGER PRIMARY KEY,
    customer_id     INTEGER NOT NULL REFERENCES customer(customer_id),
    order_date      DATE NOT NULL
);

CREATE TABLE order_line (
    order_id        INTEGER NOT NULL REFERENCES orders(order_id),
    product_id      INTEGER NOT NULL REFERENCES product(product_id),
    quantity        INTEGER NOT NULL,
    PRIMARY KEY (order_id, product_id)
);

-- Getting "total sales by department" here needs 5 joins:
-- order_line -> product -> category -> department
--            -> orders  -> customer  -> city

SELECT d.department_name,
       SUM(ol.quantity * p.unit_price) AS total_sales
FROM order_line ol
JOIN product    p ON p.product_id = ol.product_id
JOIN category   c ON c.category_id = p.category_id
JOIN department d ON d.department_id = c.department_id
GROUP BY d.department_name;


-- =========================================================
-- PART 2: STAR SCHEMA — typical OLAP / warehouse design
-- =========================================================

CREATE TABLE dim_product (
    product_key     INTEGER PRIMARY KEY,
    product_name    TEXT NOT NULL,
    category_name   TEXT NOT NULL,   -- denormalized (no separate category table)
    department_name TEXT NOT NULL,   -- denormalized (no separate department table)
    unit_price      NUMERIC(10,2) NOT NULL
);

CREATE TABLE dim_customer (
    customer_key    INTEGER PRIMARY KEY,
    customer_name   TEXT NOT NULL,
    city_name       TEXT NOT NULL,   -- denormalized (no separate city table)
    region          TEXT NOT NULL    -- denormalized (no separate region table)
);

CREATE TABLE dim_date (
    date_key        INTEGER PRIMARY KEY,   -- e.g. 20260831
    full_date       DATE NOT NULL,
    day             INTEGER NOT NULL,
    month           INTEGER NOT NULL,
    year            INTEGER NOT NULL
);

CREATE TABLE fact_sales (
    order_id        INTEGER NOT NULL,
    product_key     INTEGER NOT NULL REFERENCES dim_product(product_key),
    customer_key    INTEGER NOT NULL REFERENCES dim_customer(customer_key),
    date_key        INTEGER NOT NULL REFERENCES dim_date(date_key),
    quantity        INTEGER NOT NULL,
    line_amount     NUMERIC(10,2) NOT NULL,
    PRIMARY KEY (order_id, product_key)
);

-- Same question, "total sales by department", now needs 1 join:

SELECT dp.department_name,
       SUM(f.line_amount) AS total_sales
FROM fact_sales f
JOIN dim_product dp ON dp.product_key = f.product_key
GROUP BY dp.department_name;
