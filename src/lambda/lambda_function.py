import json
import os
import boto3
import requests
from bs4 import BeautifulSoup
import yfinance as yf

s3_client = boto3.client('s3')
RAW_BUCKET = os.environ.get('RAW_BUCKET_NAME')

def scrape_tesla_revenue():
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/revenue.htm"
    html_data = requests.get(url).text
    soup = BeautifulSoup(html_data, 'html.parser')
    
    records = []
    tables = soup.find_all("table")
    for table in tables:
        if "Tesla Quarterly Revenue" in str(table):
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    records.append({
                        "Date": cols[0].text.strip(),
                        "Revenue": cols[1].text.strip()
                    })
            break
    return records

def scrape_gme_revenue():
    url = "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBMDeveloperSkillsNetwork-PY0220EN-SkillsNetwork/labs/project/stock.html"
    html_data = requests.get(url).text
    soup = BeautifulSoup(html_data, 'html.parser')
    
    records = []
    tables = soup.find_all("table")
    for table in tables:
        if "GameStop Quarterly Revenue" in str(table):
            rows = table.find("tbody").find_all("tr")
            for row in rows:
                cols = row.find_all("td")
                if len(cols) >= 2:
                    records.append({
                        "Date": cols[0].text.strip(),
                        "Revenue": cols[1].text.strip()
                    })
            break
    return records

def extract_stock_data(ticker_symbol):
    ticker = yf.Ticker(ticker_symbol)
    df = ticker.history(period="max")
    df.reset_index(inplace=True)
    

    df['Date'] = df['Date'].dt.strftime('%Y-%m-%d')
    return df[['Date', 'Open', 'High', 'Low', 'Close', 'Volume']].to_dict(orient='records')

def upload_to_s3(data, filename):
    s3_client.put_object(
        Bucket=RAW_BUCKET,
        Key=f"raw/{filename}",
        Body=json.dumps(data),
        ContentType='application/json'
    )

def lambda_handler(event, context):
    try:
        print("Starting Data Extraction...")
        
        
        tesla_stock = extract_stock_data("TSLA")  #stock extraction
        gme_stock = extract_stock_data("GME")
        
      
        tesla_rev = scrape_tesla_revenue() # revenue extraction
        gme_rev = scrape_gme_revenue()
        
        
        upload_to_s3(tesla_stock, "tesla_stock.json")      # upload to raw S3 bucket
        upload_to_s3(gme_stock, "gme_stock.json")
        upload_to_s3(tesla_rev, "tesla_revenue.json")
        upload_to_s3(gme_rev, "gme_revenue.json")
        
        return {
            'statusCode': 200,
            'body': json.dumps('Data successfully ingested to Raw S3 bucket!')
        }
    except Exception as e:
        print(f"Error: {str(e)}")
        return {
            'statusCode': 500,
            'body': json.dumps(f"Pipeline Execution Failed: {str(e)}")
        }