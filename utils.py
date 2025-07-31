import pandas as pd

CSV_FILE_PATH = 'Project_Management_Dataset.csv'  # update the filename if yours is different

def load_data():
    return pd.read_csv(CSV_FILE_PATH)

def save_data(df):
    df.to_csv(CSV_FILE_PATH, index=False)
