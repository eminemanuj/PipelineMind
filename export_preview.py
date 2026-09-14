import duckdb

conn = duckdb.connect('data/raw/warehouse.duckdb')
conn.execute("COPY raw_customers TO 'data/raw/customers_preview.csv' (HEADER, DELIMITER ',')")
conn.execute("COPY raw_orders TO 'data/raw/orders_preview.csv' (HEADER, DELIMITER ',')")
print("Exported both tables to CSV")