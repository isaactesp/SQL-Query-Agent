-- this file contains a sequence of transformation to clean the order table as follows: (could be seen as a Directed Acyclic Graph)
-- 0. cast the quantity and unit_price to their proper data-types
-- 1. standarize dates
-- 2. remove records with null customer_id
-- 3. remove duplicates in order_id

with source as (
    SELECT
        order_id AS ORDER_ID,
        customer_id AS CUSTOMER_ID,
        product_id AS PRODUCT_ID,
        order_date AS ORDER_DATE,
        try_cast(quantity AS INTEGER) AS QUANTITY,              -- tries to cast the quantity to a integer, in case of not being possible (e.g. quantity = abc), it returns null
        try_cast(unit_price AS NUMERIC(10,2)) AS UNIT_PRICE,    -- same to a numeric value with two decimals
        status as ORDER_STATUS
    FROM {{ source('raw', 'orders') }}
), -- naming this query as source

-- Fix 1: Standardize mixed date formats (MM/DD/YYYY and YYYY-MM-DD)
-- cast ORDER_DATE to date
date_fixed as (
    select
        ORDER_ID,
        CUSTOMER_ID,
        PRODUCT_ID,
        case
            when ORDER_DATE like '__/__/____'
                then strptime(ORDER_DATE, '%m/%d/%Y')::date
            else cast(ORDER_DATE as date)                       -- no need to try, we already know it's valid data to build a date-sql
        end as ORDER_DATE,
        QUANTITY,
        UNIT_PRICE,
        ORDER_STATUS
    from source
),

-- Fix 2: Remove rows with NULL customer_id
no_nulls as (
    SELECT
        *
    FROM date_fixed
    WHERE CUSTOMER_ID IS NOT NULL
),                                              -- we could think another solution for records with null customer_id but now just deleting 

-- Fix 3: Deduplicate rows based on order_id

deduplicated as (
    SELECT
        *,
        ROW_NUMBER() OVER (PARTITION BY ORDER_ID ORDER BY ORDER_DATE DESC) AS rn    -- group by ORDER_ID -mostly unique-, and order by desc date, so the first order will have rn = 1, while
    FROM no_nulls                                                                   -- the second one will have rn = 2
),

cleaned_data as(
    SELECT
        ORDER_ID,
        CUSTOMER_ID,
        PRODUCT_ID,
        ORDER_DATE,
        QUANTITY,
        UNIT_PRICE,
        ORDER_STATUS
    FROM deduplicated
    WHERE rn = 1
    AND quantity > 0
)

SELECT * FROM cleaned_data