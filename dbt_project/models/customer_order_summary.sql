-- models/customer_order_summary.sql
--
-- Joins raw orders to raw customers and summarizes revenue per customer.
-- This model assumes order_amount is numeric (DOUBLE) — which is exactly
-- the assumption our schema-drift trigger will violate, causing dbt to
-- fail here with a real type-mismatch error.

select
    c.customer_id,
    c.full_name,
    c.email,
    c.country,
    count(o.order_id) as total_orders,
    sum(o.order_amount) as total_revenue,  -- breaks if order_amount becomes text
    avg(o.order_amount) as avg_order_value
from raw_customers c
left join raw_orders o
    on c.customer_id = o.customer_id
where o.order_status = 'completed'
group by 1, 2, 3, 4