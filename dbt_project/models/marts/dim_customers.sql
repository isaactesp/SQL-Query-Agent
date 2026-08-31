with customers as (
    select * from {{ ref('stg_customers') }}
),

orders as (
    select * from {{ ref('stg_orders') }}
),

customer_orders as (
    select
        CUSTOMER_ID,
        count(ORDER_ID)                        as TOTAL_ORDERS,
        round(sum(QUANTITY * UNIT_PRICE), 2)   as CUSTOMER_LIFETIME_VALUE,
        min(ORDER_DATE)                        as FIRST_ORDER_DATE,
        max(ORDER_DATE)                        as LAST_ORDER_DATE
    from orders
    group by CUSTOMER_ID
),

final as (
    select
        c.CUSTOMER_ID,
        c.NAME,
        c.EMAIL,
        c.COUNTRY_CODE,
        c.SEGMENT,
        c.CREATED_AT,
        coalesce(co.TOTAL_ORDERS, 0)              as TOTAL_ORDERS,
        coalesce(co.CUSTOMER_LIFETIME_VALUE, 0)   as CUSTOMER_LIFETIME_VALUE,
        co.FIRST_ORDER_DATE,
        co.LAST_ORDER_DATE
    from customers c
    left join customer_orders co on c.CUSTOMER_ID = co.CUSTOMER_ID      -- to still consider the customers with no orders
)

select * from final