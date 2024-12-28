import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut

# Function to geocode addresses
def geocode_address(address):
    try:
        location = geolocator.geocode(address)
        return (location.latitude, location.longitude) if location else (None, None)
    except GeocoderTimedOut:
        return geocode_address(address)

# Initialize the geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Streamlit app title
st.title("Interactive Map-Based Data Visualization")

# File uploader for CSV or Excel files
uploaded_file = st.file_uploader("Upload your CSV or Excel file", type=['csv', 'xlsx'])

if uploaded_file is not None:
    # Load the data
    if uploaded_file.name.endswith('.csv'):
        data = pd.read_csv(uploaded_file)
    else:
        data = pd.read_excel(uploaded_file)

    # Display the first few rows of the data
    st.write("Data Preview:")
    st.write(data.head())

    # Check if 'Address' column exists
    if 'Address' not in data.columns:
        st.error("The uploaded file must contain an 'Address' column.")
    else:
        # Geocode addresses
        st.write("Geocoding addresses...")
        data['Coordinates'] = data['Address'].apply(geocode_address)
        data[['Latitude', 'Longitude']] = pd.DataFrame(data['Coordinates'].tolist(), index=data.index)

        # Create a map visualization
        fig = px.scatter_mapbox(data, lat='Latitude', lon='Longitude', hover_name='Address',
                                 mapbox_style="carto-positron", zoom=10, title="Customer Locations")
        st.plotly_chart(fig)

        # Identify and display unplotted areas
        unplotted = data[data['Latitude'].isnull() | data['Longitude'].isnull()]
        if not unplotted.empty:
            st.write("Unplotted Areas:")
            st.write(unplotted)
        else:
            st.success("All addresses were successfully geocoded!")
