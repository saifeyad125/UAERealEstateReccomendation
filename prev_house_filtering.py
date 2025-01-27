from setup import load_data, show_dataframe_popup, pd, np, plt, tk, ttk
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

# Load the dataset
df = load_data()

# Based on the previous houses they own, we will give them top 5 suggestions on houses they might like
# We will use the columns: #bathrooms, #bedrooms, price, sizeMin

# Select relevant columns

newdf = df[['bathrooms', 'bedrooms', 'price', 'sizeMin']]

# Convert all columns to numeric
def convert_to_numeric(df):
    # sizeMin's format is like 123 sqft, we will remove the sqft and convert it to numeric
    df.loc[:, 'sizeMin'] = df['sizeMin'].str.replace('sqft', '').astype(float)
    # bathrooms and bedrooms have a '+' sign at the end, we will remove it and convert to numeric
    df.loc[:, 'bathrooms'] = df['bathrooms'].str.replace('+', '', regex=False).str.strip()
    df.loc[:, 'bedrooms'] = df['bedrooms'].str.replace('+', '', regex=False).str.strip()

    df.loc[:, 'bathrooms'] = pd.to_numeric(df['bathrooms'], errors='coerce')
    df.loc[:, 'bedrooms'] = pd.to_numeric(df['bedrooms'], errors='coerce')
    df.loc[:, 'price'] = pd.to_numeric(df['price'], errors='coerce')
    df.loc[:, 'sizeMin'] = pd.to_numeric(df['sizeMin'], errors='coerce')
    df = df.dropna()

    return df

# We will now add address to the columns we will use to recommend houses
newdf = convert_to_numeric(newdf)
newdf['displayAddress'] = df['displayAddress']

vectorizer = TfidfVectorizer()

def address_to_vector(df):
    # We will first convert displayAddress to a vector using TF-IDF
    # Remove all spaces in the address column and make it lowercase
    df.loc[:, 'displayAddress'] = df['displayAddress'].str.replace(' ', '').str.lower()

    # Fit the vectorizer
    vectorizer.fit(df['displayAddress'])

    # Transform the address column to a vector
    address_vector = vectorizer.transform(df['displayAddress'])

    # Convert the vector to a dataframe
    address_df = pd.DataFrame(address_vector.toarray(), columns=vectorizer.get_feature_names_out())

    # Concatenate the address_df to the newdf
    df = pd.concat([df, address_df], axis=1)

    # Drop the displayAddress column
    df.drop('displayAddress', axis=1, inplace=True)
    return df

newdf = address_to_vector(newdf)

# Step 2: Normalize the data
def normalize_data(df):
    return (df - df.min()) / (df.max() - df.min())

normalized_df = normalize_data(newdf)

#i want to apply weights to each column:
normalized_df['bathrooms'] *= 1.0  
normalized_df['bedrooms'] *= 1.0   
normalized_df['price'] *= 2.0      
normalized_df['sizeMin'] *= 1.5


# Step 3: Calculate the Euclidean distance
def euclidean_distance(normalized_df, house1, house2):
    house1_data = normalized_df.loc[house1]
    house2_data = normalized_df.loc[house2]
    return np.sqrt(np.sum((house1_data - house2_data) ** 2))

# Step 4: Get recommendations
def get_recommendations(normalized_df, house_index):
    distances = []
    for i in normalized_df.index:
        if i == house_index:
            continue
        distance = euclidean_distance(normalized_df, house_index, i)
        distances.append((i, distance))
    distances.sort(key=lambda x: x[1])  # Sort by distance
    return distances[:5]  # Return top 5 recommendations

















# Example: Use the first house in the dataset for recommendations
house_index = normalized_df.index[:3]  # Get the index of the first 3 houses
avg_of_houses = normalized_df.loc[house_index].mean()  # Calculate the average of the first 3 houses
temp_df = pd.concat([normalized_df, pd.DataFrame([avg_of_houses])], ignore_index=True)
merged_houses_index = temp_df.index[-1] 
recommendations = get_recommendations(temp_df, merged_houses_index)

# Display recommendations
print("Top 5 similar houses:")
recommended_indices = [idx for idx, _ in recommendations]  # Extract recommended indices
recommended_houses = df.loc[recommended_indices]  # Use the original df to get all columns



# Print each recommended house
for i, row in recommended_houses.iterrows():
    print(f"House Index: {i}")
    print(row.to_string(), "\n")  # Display all columns of the house