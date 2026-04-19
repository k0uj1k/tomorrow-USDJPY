import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta

# Calculate date range: 50 days ago to today
end_date = datetime.now()
start_date = end_date - timedelta(days=50)

# Fetch USD/JPY data
print(f"Fetching USD/JPY data from {start_date.date()} to {end_date.date()}...")
data = yf.download('USDJPY=X', start=start_date, end=end_date, progress=False)

# Save to CSV
output_file = 'usdjpy_data.csv'
data.to_csv(output_file)

print(f"Data saved to {output_file}")
print(f"\nData summary:")
print(f"Total records: {len(data)}")
print(f"Date range: {data.index[0].date()} to {data.index[-1].date()}")
print(f"\nFirst 5 rows:")
print(data.head())
print(f"\nLast 5 rows:")
print(data.tail())
