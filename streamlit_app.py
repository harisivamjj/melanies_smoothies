import streamlit as st
import requests
from snowflake.snowpark.functions import col
from snowflake.snowpark.session import Session
import pandas as pd

# Write directly to the app
st.title("🥤 Customize your Smoothie! 🎈")
st.write("Choose the fruits you want in your smoothie")

name_on_order = st.text_input('Name on smoothie')
st.write('The name on the smoothie will be ', name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Verify the session is established
if session:
    st.write("Snowflake session established successfully!")
else:
    st.error("Failed to establish Snowflake session")
    st.stop()

# Fetch and display column names to debug the issue
try:
    fruit_options_table = session.table("smoothies.public.fruit_options")
    columns = [col.name for col in fruit_options_table.schema.fields]
    st.write("Columns in the fruit_options table:", columns)
    
    # Check if 'SEARCH_ON' and 'Fruit_name' exist in the columns
    if 'SEARCH_ON' in columns and 'Fruit_name' in columns:
        my_dataframe = fruit_options_table.select(col('Fruit_name'), col('SEARCH_ON'))
        st.write("Data fetched successfully from Snowflake")
        
        # Convert to pandas DataFrame
        pd_df = my_dataframe.to_pandas()
        st.write("Converted Snowflake DataFrame to pandas DataFrame")
    else:
        st.error("The required columns are not present in the table.")
        st.stop()
except Exception as e:
    st.error(f"Error fetching data from Snowflake: {e}")
    st.stop()

# Display the DataFrame
st.dataframe(pd_df)

ingredients_list = st.multiselect('Choose upto 5 ingredients: ', pd_df['Fruit_name'].tolist(), max_selections=5)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)
    
    for fruit_chosen in ingredients_list:
        search_on = pd_df.loc[pd_df['Fruit_name'] == fruit_chosen, 'SEARCH_ON'].values[0]
        st.subheader(f"{fruit_chosen} Nutrition Information")
        fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
        
        if fruityvice_response.status_code == 200:
            fv_df = pd.DataFrame(fruityvice_response.json(), index=[0])
            st.dataframe(fv_df)
        else:
            st.error(f"Failed to fetch data for {fruit_chosen} from Fruityvice API")

    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    st.write(my_insert_stmt)

    if st.button('Submit Order'):
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Failed to submit order: {e}")

    st.stop()
