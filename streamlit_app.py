# Import python packages
import streamlit as st
from snowflake.snowpark.functions import col
 
# Write directly to the app
st.title(":cup_with_straw: Customize your Smoothie! :balloon:")
st.write(
    """ Choose the fruits you want in your smoothie""")
 
 
name_on_order = st.text_input('Name on smoothie')
st.write('The name on the smoothie will be ', name_on_order)
 
cnx = st.connection("snowflake") 
session = cnx.session()
my_dataframe = session.table("smoothies.public.fruit_options").select(col('Fruit_name'))
#st.dataframe(data=my_dataframe, use_container_width=True)
 
ingredients_list= st.multiselect('Choose upto 5 ingredients: ',my_dataframe,max_selections=5)
 
if ingredients_list:
 
    ingredients_string = ' '
 
    for fruit_chosen in ingredients_list:
        ingredients_string += fruit_chosen + ' '
 
    #st.write(ingredients_string)
 
    my_insert_stmt = """ insert into smoothies.public.orders(ingredients,NAME_ON_ORDER)
            values ('""" + ingredients_string + """','"""+name_on_order+"""')"""
 
    st.write(my_insert_stmt)
    time_to_insert = st.button('Submit Order')
 
    if time_to_insert:
        session.sql(my_insert_stmt).collect()
        st.success('Your Smoothie is ordered!', icon="✅")
 
    st.stop()


import requests
fruityvice_response = requests.get("https://fruityvice.com/api/fruit/watermelon")
st.text(fruityvice_response)

