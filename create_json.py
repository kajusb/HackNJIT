import pandas as pd
import json

# Load the CSV files
transactions_df = pd.read_csv('Transactions.csv')
items_df = pd.read_csv('Items.csv')

# Merge the DataFrames on 'orderID'
merged_df = pd.merge(transactions_df, items_df, on='OrderID')

# Group by 'orderID' and aggregate the items
grouped = merged_df.groupby(['OrderID', 'Amount_x', 'Tax', 'Currency_x', 'Date', 'Time', 'FileName']).apply(
    lambda x: x[['Name', 'Quantity', 'Amount_y', 'VAT', 'VAT%', 'Currency_y']].to_dict('records')
).reset_index(name='Items')

# Rename columns to match the desired output format
grouped.rename(columns={
    'Amount_x': 'Amount',
    'Currency_x': 'Currency',
    'Amount_y': 'Amount',
    'Currency_y': 'Currency'
}, inplace=True)


# Convert VAT and VAT% to nested dictionary
for item in grouped['Items']:
    for i in item:
        i['VAT'] = {
            'Amount': i.pop('VAT'),
            'Percentage': i.pop('VAT%')
        }

# Convert the grouped DataFrame to JSON
grouped_json = grouped.to_json(orient='records', indent=4)

# Save the grouped JSON to a file
with open('grouped_data.json', 'w') as grouped_file:
    grouped_file.write(grouped_json)

print("The grouped data has been saved to grouped_data.json")
