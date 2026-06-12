INSERT INTO airlines (
    airline_code,
    airline_name
)
VALUES (%s, %s)
ON CONFLICT (airline_code) DO NOTHING;