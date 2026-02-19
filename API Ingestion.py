def ingest_api_data(start_date, end_date):
    # Logic to loop through dates and land JSON into Blob Storage
    # Prevents data loss and allows for easy re-runs
    for d in date_range(start_date, end_date):
        data = call_product_api(d)
        upload_to_blob(data, f"raw/usage/{d}.json")