import pandas as pd

# Load the CSV files
items_df = pd.read_csv('items.csv')
transactions_df = pd.read_csv('transactions.csv')

# Merge the DataFrames on 'OrderID'
merged_df = pd.merge(items_df, transactions_df, on='OrderID')

# Convert 'Date' to datetime
merged_df['Date'] = pd.to_datetime(merged_df['Date'], format='%d-%m-%Y')

# Extract features like year, month, day
merged_df['Year'] = merged_df['Date'].dt.year
merged_df['Month'] = merged_df['Date'].dt.month
merged_df['Day'] = merged_df['Date'].dt.day

# Function to clean and convert 'Amount_x' values
def clean_amount(amount):
    try:
        return float(amount.replace(' EUR', '').strip())
    except ValueError:
        print(f"Could not convert: {amount}")
        return None

# Apply the cleaning function to 'Amount_x'
merged_df['Amount_x'] = merged_df['Amount_x'].apply(clean_amount)

# Drop rows with invalid 'Amount_x' values
merged_df = merged_df.dropna(subset=['Amount_x'])

# Example: Predicting 'Amount_x' based on 'Year', 'Month', 'Day'
X = merged_df[['Year', 'Month', 'Day']]
y = merged_df['Amount_x']

# Split the data into training and testing sets
from sklearn.model_selection import train_test_split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Train the model
from sklearn.linear_model import LinearRegression
model = LinearRegression()
model.fit(X_train, y_train)

# Evaluate the model
score = model.score(X_test, y_test)
print(f'Model R^2 score: {score}')
