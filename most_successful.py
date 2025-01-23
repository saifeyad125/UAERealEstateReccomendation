#we will find the top 5 most successful projects
#unfortunately, we don't have the costs, so I will use sqft as a cost, 1 sqft = 1500 AED
#obviously, each sqft is different depending on the area, but all this could be changed in the input of the function if we have more accurate costs
from setup import load_data, show_dataframe_popup, pd, np, plt, tk, ttk

# Load the dataset
df = load_data()
DEFAULT_COST_PER_SQFT = 1500
DEFAULT_COST_PER_ROOM = 5000
DEFAULT_COST_PER_BATHROOM = 10000



#firstly, we will change minSize to numeric and remove the sqft
def convert_to_numeric(df):
    # sizeMin's format is like 123 sqft, we will remove the sqft and convert it to numeric
    df['sizeMin'] = df['sizeMin'].str.replace('sqft', '').astype(float)
    # bathrooms and bedrooms have a '+' sign at the end, we will remove it and convert to numeric
    df['bathrooms'] = df['bathrooms'].str.replace('+', '', regex=False).str.strip()
    df['bedrooms'] = df['bedrooms'].str.replace('+', '', regex=False).str.strip()
    df['bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
    df['bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df['price'] = pd.to_numeric(df['price'], errors='coerce')
    df['sizeMin'] = pd.to_numeric(df['sizeMin'], errors='coerce')
    df = df.dropna()

    return df

df = convert_to_numeric(df)

#now we will make a new colum called profit where we would do price - sizeMin * DEFAULT_COST_PER_SQFT
df['profit'] = df['price'] - (df['sizeMin'] * DEFAULT_COST_PER_SQFT + df['bedrooms'] * DEFAULT_COST_PER_ROOM + df['bathrooms'] * DEFAULT_COST_PER_BATHROOM)

#address format is like this: Aurum Villas, Aster, Damac Hills 2, Dubai, we will extract the project name (first part only)
df['project'] = df['displayAddress'].str.split(',').str[0]

#now we will group by project and sum the profit
grouped = df.groupby('project').sum().sort_values('profit', ascending=False).reset_index()
top5 = grouped.head(5)
print(top5)