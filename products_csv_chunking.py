import pandas as pd
import numpy as np
import os

# Define the file names
input_file = 'products-10000.csv'
output_file = 'cleaned_products.csv'

# Define the chunk size
chunk_size = 1000

# Initialize an empty list to store processed chunks
cleaned_chunks = []

# Create a TextFileReader object for chunking
try:
    chunk_iterator = pd.read_csv(input_file, chunksize=chunk_size)
    print(f"Reading '{input_file}' in chunks of {chunk_size} rows...")
except FileNotFoundError:
    print(f"Error: The file '{input_file}' was not found.")
    chunk_iterator = []

# Iterate over each chunk
for i, chunk in enumerate(chunk_iterator):
    print(f"Processing chunk {i+1}...")

    # --- Data Cleaning and Modifications for each chunk ---
    
    # 1. Renaming Columns for Clarity
    chunk.rename(columns={
        'Internal ID': 'Internal_ID',
        'Name': 'Product_Name',
        'Stock': 'Stock_Quantity'
    }, inplace=True)

    # 2. Handling Missing Values

    chunk['Description'] = chunk['Description'].fillna('No Description Provided', inpalce =True)

    # Dropping rows with missing EAN is not a chained assignment, so inplace is fine
    chunk.dropna(subset=['EAN'], inplace=True)

    # 3. Removing Duplicates (within the chunk)
    # This is also not a chained assignment
    chunk.drop_duplicates(subset='EAN', inplace=True)

    # 4. Correcting Data Types
    # The to_numeric and astype methods are also safe
    chunk['Price'] = pd.to_numeric(chunk['Price'], errors='coerce')
    chunk['EAN'] = chunk['EAN'].astype(str)
    
    # 5. Creating a New Column
    chunk['Final_Price'] = chunk['Price'] * 0.9

    # 6. Cleaning Text Data
    chunk['Category'] = chunk['Category'].str.lower()
    
    # Append the cleaned chunk to the list
    cleaned_chunks.append(chunk)

# --- Combining Chunks and Finalizing Data ---

if cleaned_chunks:
    print("\nAll chunks processed. Concatenating into a single DataFrame...")
    final_df = pd.concat(cleaned_chunks, ignore_index=True)
    
    # Perform a final check for duplicates across the entire dataset.
    initial_rows = len(final_df)
    # Corrected line to avoid the FutureWarning
    final_df = final_df.drop_duplicates(subset='EAN')
    final_rows = len(final_df)
    print(f"Final duplicate check: Dropped {initial_rows - final_rows} rows.")

    # --- Saving the Cleaned DataFrame to a new file ---
    print(f"\nSaving the cleaned data to '{output_file}'...")
    final_df.to_csv(output_file, index=False)
    print("Data saved successfully!")
else:
    print("\nNo data was processed. The output file was not created.")

# To verify the saved file, you can load it and check its info
if os.path.exists(output_file):
    print("\n--- Verifying the output file ---")
    verified_df = pd.read_csv(output_file)
    print(verified_df.info())