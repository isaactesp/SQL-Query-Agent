select 
    customer_id as CUSTOMER_ID,
    name as NAME,
    email as EMAIL,
    country as COUNTRY_CODE,
    segment as SEGMENT,
    created_at::date AS created_at      -- converts the string date into a sql date
FROM {{ source('raw', 'customers')}}