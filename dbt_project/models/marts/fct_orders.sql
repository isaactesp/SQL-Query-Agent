with orders as (
    select * from {{ ref('stg_orders') }}
),

customers as (
    select * from {{ ref('stg_customers') }}
),

products as (
    select * from {{ ref('stg_products') }}
),

final as (
    select
        o.ORDER_ID,
        o.CUSTOMER_ID,
        o.PRODUCT_ID,
        o.ORDER_DATE,
        o.QUANTITY,
        o.UNIT_PRICE,
        round(o.QUANTITY * o.UNIT_PRICE, 2) as REVENUE,
        o.ORDER_STATUS,
        c.NAME    as CUSTOMER_NAME,
        c.SEGMENT as CUSTOMER_SEGMENT,
        c.COUNTRY_CODE,
        p.PRODUCT_NAME,
        p.CATEGORY,
        p.BRAND_NAME
    from orders o
    left join customers c on o.CUSTOMER_ID = c.CUSTOMER_ID
    left join products  p on o.PRODUCT_ID  = p.PRODUCT_ID
) -- recall: join/inner join joins only records that match the joining column in both tables, left/right/outer join joins all the columns from the left/right table and let null in the
  -- columns of the records from the other table which joining column doesn't match with any record. Said that: 
  -- orders from products that have been vanished from the catalogue will be logged (REVENUE will be still calculated, while the product name, category, brand will be null).
  -- thanks to the left join from orders with customers, also the orders from customers that are not in the db anymore would be taken into account.  

select * from final