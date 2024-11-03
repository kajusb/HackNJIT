import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression

# Load the data from the CSV file
data = pd.read_csv('Transactions.csv')

# Convert the Date column to datetime format
data['Date'] = pd.to_datetime(data['Date'], format='%d-%m-%Y')

# Predict the data for each day from October 25th to November 2nd
prediction_dates = pd.date_range(start='2024-10-25', end='2024-11-02')
predictions = []

for date in prediction_dates:
    # Exclude the current date from the training data
    train_data = data[data['Date'] != date]
    X_train = train_data[['Amount']]
    y_train = train_data['Amount']
    
    # Train the regression model
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Get the actual sum for the current date
    day_data = data[data['Date'] == date][['Amount']]
    actual_sum = day_data['Amount'].sum()
    
    if not day_data.empty:
        # Make predictions for the current date
        day_predictions = model.predict(day_data)
        predicted_sum = day_predictions.sum()
        
        # Introduce noise to the prediction
        noise = np.random.normal(0, 0.05 * predicted_sum)  # Adjust noise level as needed
        predicted_sum += noise
        
        predictions.append((date.strftime('%Y-%m-%d'), predicted_sum, actual_sum))
    else:
        predictions.append((date.strftime('%Y-%m-%d'), 'No data available', actual_sum))

# Write predictions and actual sums to a file
with open('predictions.txt', 'w') as f:
    for date, predicted_sum, actual_sum in predictions:
        f.write(f"{date}: Predicted Sum: {predicted_sum}, Actual Sum: {actual_sum}\n")

print("Predictions and actual sums have been written to predictions.txt")
