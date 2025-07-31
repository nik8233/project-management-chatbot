from utils import load_data

def test_status_column():
    df = load_data()
    df['Normalized Status'] = df['Status'].str.replace(" ", "").str.lower()
    print(df[['Status', 'Normalized Status']].head(10))
    print("Unique normalized statuses:", df['Normalized Status'].unique())

test_status_column()
