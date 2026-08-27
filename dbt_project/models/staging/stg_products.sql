select 
    product_id AS PRODUCT_ID,
    name AS NAME,
    category as CATEGORY,
    brand AS BRAND,
    base_price::numeric(10,2) AS BASE_PRICE     -- converts string price into a numeric-type price with 2 decimals
from {{source('raw', 'products')}} 