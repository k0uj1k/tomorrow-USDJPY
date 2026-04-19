FROM python:3.11-slim

WORKDIR /app

RUN pip install --no-cache-dir yfinance pandas

COPY fetch_forex.py .

RUN mkdir -p /app/output

CMD ["python", "fetch_forex.py"]
