import pandas as pd

def create_sample_excel():
    data = {
        'Metric': ['Q1 Sales', 'Q2 Sales', 'Q3 Sales', 'Q4 Sales'],
        'Value': ['$10,000', '$15,000', '$20,000', '$25,000'],
        'Notes': ['Strong start', 'Summer growth', 'Back to school boost', 'Holiday season peak']
    }
    
    df = pd.DataFrame(data)
    with pd.ExcelWriter('test_data.xlsx') as writer:
        df.to_excel(writer, sheet_name='Sales Data', index=False)
        
    print("Created test_data.xlsx")

if __name__ == "__main__":
    create_sample_excel()
