import pandas as pd
import numpy as np

# Read CSV with skiprows to skip header metadata
df = pd.read_csv('usdjpy_data.csv', skiprows=2)

# After skiprows=2, columns are: Date, Unnamed:1 (Close), Unnamed:2 (High), Unnamed:3 (Low), Unnamed:4 (Open), Unnamed:5 (Volume)
df.columns = ['Date', 'Close', 'High', 'Low', 'Open', 'Volume']
df['Date'] = pd.to_datetime(df['Date'])

# Select and convert OHLC columns
df = df[['Date', 'Open', 'High', 'Low', 'Close']].copy()
df = df.astype({'Open': float, 'High': float, 'Low': float, 'Close': float})
df = df.sort_values('Date').reset_index(drop=True)

print(f"Total data points: {len(df)}")
print(f"Date range: {df['Date'].min()} to {df['Date'].max()}\n")

def normalize_candlestick(open_p, high, low, close):
    """Normalize candlestick to shape ratios (body size, upper shadow, lower shadow)"""
    body = abs(close - open_p)
    upper_shadow = high - max(open_p, close)
    lower_shadow = min(open_p, close) - low
    total_range = high - low
    
    if total_range == 0:
        return (0, 0, 0)
    
    return (body / total_range, upper_shadow / total_range, lower_shadow / total_range)

def pattern_similarity(pattern1, pattern2, tolerance=0.25):
    """Check if two patterns are similar within tolerance"""
    return all(abs(p1 - p2) < tolerance for p1, p2 in zip(pattern1, pattern2))

def is_bullish(open_p, close):
    """Check if candle is bullish (陽線)"""
    return close > open_p

# Extract recent 3-day pattern
recent_pattern = []
print("=== Most Recent 3-Day Pattern ===")
for i in range(len(df) - 3, len(df)):
    row = df.iloc[i]
    shape = normalize_candlestick(row['Open'], row['High'], row['Low'], row['Close'])
    recent_pattern.append(shape)
    candle_type = "陽線" if is_bullish(row['Open'], row['Close']) else "陰線"
    print(f"Day {i - (len(df) - 3) + 1}: {row['Date'].date()} | O:{row['Open']:.2f} H:{row['High']:.2f} L:{row['Low']:.2f} C:{row['Close']:.2f} | {candle_type}")

print(f"\nSearching for matching 3-day patterns in historical data (tolerance=0.25)...\n")

matches = []
for i in range(len(df) - 4):  # Need at least 4 days (3 for pattern + 1 for next day)
    historical_pattern = []
    for j in range(i, i + 3):
        row = df.iloc[j]
        shape = normalize_candlestick(row['Open'], row['High'], row['Low'], row['Close'])
        historical_pattern.append(shape)
    
    # Check if all 3 days match
    if all(pattern_similarity(recent_pattern[k], historical_pattern[k], 0.25) for k in range(3)):
        # Get the next day
        next_row = df.iloc[i + 3]
        next_bullish = is_bullish(next_row['Open'], next_row['Close'])
        next_candle = "陽線" if next_bullish else "陰線"
        
        matches.append({
            'start_date': df.iloc[i]['Date'],
            'end_date': df.iloc[i + 2]['Date'],
            'next_date': next_row['Date'],
            'next_candle': next_candle,
            'next_open': next_row['Open'],
            'next_close': next_row['Close'],
            'next_change_pct': ((next_row['Close'] - next_row['Open']) / next_row['Open'] * 100)
        })

if matches:
    print(f"=== Found {len(matches)} matching pattern(s) ===\n")
    bullish_count = sum(1 for m in matches if m['next_candle'] == '陽線')
    bearish_count = sum(1 for m in matches if m['next_candle'] == '陰線')
    print(f"Summary: {bullish_count} bullish (陽線), {bearish_count} bearish (陰線)\n")
    
    for idx, match in enumerate(matches, 1):
        print(f"Match {idx}:")
        print(f"  Pattern period: {match['start_date'].date()} to {match['end_date'].date()}")
        print(f"  Next day: {match['next_date'].date()}")
        print(f"  Next day candle: {match['next_candle']}")
        print(f"  Next day O:{match['next_open']:.2f} C:{match['next_close']:.2f}")
        print(f"  Price change: {match['next_change_pct']:+.3f}%\n")
else:
    print("No matching patterns found with tolerance 0.25.")
    print("Increasing tolerance to 0.35...\n")
    
    matches = []
    for i in range(len(df) - 4):
        historical_pattern = []
        for j in range(i, i + 3):
            row = df.iloc[j]
            shape = normalize_candlestick(row['Open'], row['High'], row['Low'], row['Close'])
            historical_pattern.append(shape)
        
        if all(pattern_similarity(recent_pattern[k], historical_pattern[k], 0.35) for k in range(3)):
            next_row = df.iloc[i + 3]
            next_bullish = is_bullish(next_row['Open'], next_row['Close'])
            next_candle = "陽線" if next_bullish else "陰線"
            
            matches.append({
                'start_date': df.iloc[i]['Date'],
                'end_date': df.iloc[i + 2]['Date'],
                'next_date': next_row['Date'],
                'next_candle': next_candle,
                'next_open': next_row['Open'],
                'next_close': next_row['Close'],
                'next_change_pct': ((next_row['Close'] - next_row['Open']) / next_row['Open'] * 100)
            })
    
    if matches:
        print(f"=== Found {len(matches)} matching pattern(s) with tolerance 0.35 ===\n")
        bullish_count = sum(1 for m in matches if m['next_candle'] == '陽線')
        bearish_count = sum(1 for m in matches if m['next_candle'] == '陰線')
        print(f"Summary: {bullish_count} bullish (陽線), {bearish_count} bearish (陰線)\n")
        
        for idx, match in enumerate(matches, 1):
            print(f"Match {idx}:")
            print(f"  Pattern period: {match['start_date'].date()} to {match['end_date'].date()}")
            print(f"  Next day: {match['next_date'].date()}")
            print(f"  Next day candle: {match['next_candle']}")
            print(f"  Next day O:{match['next_open']:.2f} C:{match['next_close']:.2f}")
            print(f"  Price change: {match['next_change_pct']:+.3f}%\n")
    else:
        print("Still no matches. The recent pattern is quite unique.")
