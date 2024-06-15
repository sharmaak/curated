import csv
import requests
import json

"""
This file takes curated_stocks.csv as input and loads all stock symbols from 
the first column. Then it fetches details for each from moneycontrol.com and 
updates it in the same sheet. 
"""

def read_curated_stocks(file_path):
    stocks = []
    with open(file_path, mode='r', newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip the header
        for row in reader:
            if row and row[0]:  # Skip empty lines or lines with only commas
                nse_symbol = row[0].strip()
                if nse_symbol:
                    stocks.append({
                        'nse_symbol': nse_symbol
                    })
    return stocks

def fetch_stock_info(nse_symbol):
    url = f'https://www.moneycontrol.com/mccode/common/autosuggestion_solr.php?classic=true&type=1&format=json&callback=&query={nse_symbol}'
    response = requests.get(url)
    if response.status_code == 200:
        return response.json()
    else:
        return None

def parse_pdt_dis_nm(pdt_dis_nm):
    import re
    match = re.search(r'([^<]+)&nbsp;<span>([^,]+), ([^,]+), ([^<]+)</span>', pdt_dis_nm)
    if match:
        name, isin, nse_symbol, bse_id = match.groups()
        return {
            'name': name.strip(),
            'isin': isin.strip(),
            'nse_symbol': nse_symbol.strip(),
            'bse_id': bse_id.strip()
        }
    return None

def update_csv(file_path, stock_data):
    with open(file_path, mode='w', newline='') as csvfile:
        fieldnames = ['nse_symbol', 'isin',  'bse_id', 'name', 'sector']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        writer.writeheader()
        for data in stock_data:
            writer.writerow(data)

def main():
    input_file = 'curated_stocks.csv'
    stocks = read_curated_stocks(input_file)
    updated_stocks = []
    
    for stock in stocks:
        print(f'Processing {stock["nse_symbol"]} ... ')
        response = fetch_stock_info(stock['nse_symbol'])
        if response:
            for item in response:
                parsed_info = parse_pdt_dis_nm(item['pdt_dis_nm'])
                if parsed_info is not None and parsed_info['nse_symbol'] == stock['nse_symbol']:
                    parsed_info['sector'] = item['sc_sector']
                    updated_stocks.append(parsed_info)


    if updated_stocks:
        update_csv(input_file, updated_stocks)

if __name__ == "__main__":
    main()
