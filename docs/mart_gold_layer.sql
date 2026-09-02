-- ============================================================
-- Mart layer DDL for ERD generation (Lucidchart / dbdiagram.io)
-- Reflects main_marts.dim_customers, dim_products, fct_orders
-- ============================================================

CREATE TABLE dim_customers (
    CUSTOMER_ID             VARCHAR(10)     PRIMARY KEY,
    NAME                    VARCHAR(100),
    EMAIL                   VARCHAR(150),
    COUNTRY_CODE            VARCHAR(2),
    SEGMENT                 VARCHAR(20),
    CREATED_AT              DATE,
    TOTAL_ORDERS            INTEGER,
    CUSTOMER_LIFETIME_VALUE NUMERIC(12,2),
    FIRST_ORDER_DATE        DATE,
    LAST_ORDER_DATE         DATE
);

CREATE TABLE dim_products (
    PRODUCT_ID    VARCHAR(10)     PRIMARY KEY,
    PRODUCT_NAME  VARCHAR(150),
    CATEGORY      VARCHAR(50),
    BRAND_NAME    VARCHAR(50),
    BASE_PRICE    NUMERIC(10,2)
);

CREATE TABLE fct_orders (
    ORDER_ID          VARCHAR(10)     PRIMARY KEY,
    CUSTOMER_ID       VARCHAR(10)     NOT NULL,
    PRODUCT_ID        VARCHAR(10)     NOT NULL,
    ORDER_DATE        DATE,
    QUANTITY          INTEGER,
    UNIT_PRICE        NUMERIC(10,2),
    REVENUE           NUMERIC(12,2),
    ORDER_STATUS      VARCHAR(20),
    CUSTOMER_NAME     VARCHAR(100),
    CUSTOMER_SEGMENT  VARCHAR(20),
    COUNTRY_CODE      VARCHAR(2),
    PRODUCT_NAME      VARCHAR(150),
    CATEGORY          VARCHAR(50),
    BRAND_NAME        VARCHAR(50),

    CONSTRAINT fk_orders_customer
        FOREIGN KEY (CUSTOMER_ID) REFERENCES dim_customers (CUSTOMER_ID),
    CONSTRAINT fk_orders_product
        FOREIGN KEY (PRODUCT_ID) REFERENCES dim_products (PRODUCT_ID)
);