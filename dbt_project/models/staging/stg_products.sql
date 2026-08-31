select 
    product_id AS PRODUCT_ID,
    name AS PRODUCT_NAME,
    category as CATEGORY,
    brand AS BRAND_NAME,
    base_price::numeric(10,2) AS BASE_PRICE     -- converts string price into a numeric-type price with 2 decimals
from {{source('raw', 'products')}} 