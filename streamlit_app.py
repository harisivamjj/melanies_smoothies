import streamlit as st
import requests
from snowflake.snowpark.session import Session
from snowflake.snowpark.functions import col

# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :balloon:")
st.write("Choose the fruits you want in your smoothie")

# Get user input for the smoothie name
name_on_order = st.text_input('Name on smoothie')
st.write('The name on the smoothie will be ', name_on_order)

# Establish Snowflake connection
cnx = st.connection("snowflake")
session = cnx.session()

# Load data from Snowflake table
try:
    my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'), col('SEARCH_ON'))
    pd_df = my_dataframe.to_pandas()
except Exception as e:
    st.error(f"Error loading data from Snowflake: {e}")
    st.stop()

# Display the dataframe for debugging
st.write("Loaded fruit options from Snowflake:")
st.dataframe(pd_df)

# User selects ingredients
ingredients_list = st.multiselect('Choose up to 5 ingredients:', pd_df['FRUIT_NAME'].tolist(), max_selections=5)

if ingredients_list:
    ingredients_string = ' '.join(ingredients_list)

    for fruit_chosen in ingredients_list:
        try:
            search_on = pd_df.loc[pd_df['FRUIT_NAME'] == fruit_chosen, 'SEARCH_ON'].iloc[0]
            st.subheader(f"{fruit_chosen} Nutrition Information")
            fruityvice_response = requests.get(f"https://fruityvice.com/api/fruit/{search_on}")
            fruityvice_data = fruityvice_response.json()
            st.dataframe(fruityvice_data)
        except Exception as e:
            st.error(f"Error fetching nutrition information for {fruit_chosen}: {e}")

    # Insert order into Snowflake
    my_insert_stmt = f"""INSERT INTO smoothies.public.orders (ingredients, NAME_ON_ORDER)
                         VALUES ('{ingredients_string}', '{name_on_order}')"""

    time_to_insert = st.button('Submit Order')
    if time_to_insert:
        try:
            session.sql(my_insert_stmt).collect()
            st.success('Your Smoothie is ordered!', icon="✅")
        except Exception as e:
            st.error(f"Error submitting order: {e}")

st.stop()
