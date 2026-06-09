INSERT INTO import_logs (
    data_range_start,
    data_range_end,
    download_status
)
VALUES (%s, %s, %s)
RETURNING log_id;