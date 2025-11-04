import pandas as pd
import numpy as np

# Load the CSV file into a DataFrame
file_name = 'products-10000.csv'
df = pd.read_csv(file_name)

# --- Initial Inspection ---
print("Initial Data Info:")
print(df.info())
print("\nInitial DataFrame Head:")
print(df.head())

# --- 1. Renaming Columns for Clarity ---
# A common practice is to standardize column names.
df = df.rename(columns={
    'Internal ID': 'Internal_ID',
    'Name': 'Product_Name',
    'Stock': 'Stock_Quantity'
})
print("\n--- After Renaming Columns ---")
print(df.head())

# --- 2. Handling Missing Values ---
# Check for null values
print("\nNull Values before cleaning:")
print(df.isnull().sum())

# Drop rows where 'EAN' is missing, as it's a unique identifier
df.dropna(subset=['EAN'], inplace=True)

# Fill missing 'Description' values with a default string
df['Description'].fillna('No Description Provided', inplace=True)

# Re-check for null values
print("\nNull Values after cleaning:")
print(df.isnull().sum())

# --- 3. Removing Duplicates ---
# Check for duplicate rows based on a key column like 'EAN'
print(f"\nNumber of duplicate rows based on 'EAN' before dropping: {df.duplicated(subset='EAN').sum()}")
df.drop_duplicates(subset='EAN', inplace=True)
print(f"Number of duplicate rows after dropping: {df.duplicated(subset='EAN').sum()}")

# --- 4. Correcting Data Types ---
# Check the data types again. 'Price', 'Stock_Quantity' and 'EAN' might be an object
print("\nData types before type conversion:")
print(df.dtypes)

# Convert 'Price' to a numeric type, coercing errors
df['Price'] = pd.to_numeric(df['Price'], errors='coerce')

# Convert 'EAN' to a string type for consistency
df['EAN'] = df['EAN'].astype(str)

# After conversion, let's see the new dtypes
print("\nData types after type conversion:")
print(df.dtypes)

# --- 5. Creating a New Column ---
# Let's create a new column 'Final_Price' by applying a 10% discount to the original price.
df['Final_Price'] = df['Price'] * 0.9

# --- 6. Cleaning and Transforming Text Data ---
# Standardize the 'Category' column to lowercase
df['Category'] = df['Category'].str.lower()
print("\n--- After Standardizing 'Category' to lowercase ---")
print(df['Category'].unique()[:5])

# --- 7. Handling Categorical Data ---
# availability column is a good candidate for one-hot encoding
df_one_hot_encoded = pd.get_dummies(df, columns=['Availability'], prefix='is_available')
print("\n--- After One-Hot Encoding 'Availability' ---")
print(df_one_hot_encoded[['is_available_limited_stock', 'is_available_discontinued']].head())

# --- 8. Handling Outliers (Example with Price) ---
# Check for extreme values in 'Price'
print(f"\nPrice quantiles:\n{df['Price'].quantile([0.01, 0.99])}")

# Let's assume prices above the 99th percentile are outliers and cap them.
# We'll calculate the 99th percentile price
price_99th_percentile = df['Price'].quantile(0.99)
df['Price'] = np.where(df['Price'] > price_99th_percentile, price_99th_percentile, df['Price'])
print("\n--- Price after capping outliers ---")
print(df['Price'].describe())

# --- Final Check of the Modified DataFrame ---
print("\n--- Final Cleaned DataFrame Info ---")
print(df.info())

# To save the cleaned data to a new CSV file
# df.to_csv('cleaned_products.csv', index=False)