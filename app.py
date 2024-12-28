import streamlit as st
import pandas as pd
import plotly.express as px
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable
import time
from functools import lru_cache

# Initialize the geolocator
geolocator = Nominatim(user_agent="geoapiExercises")

# Caching for geocoding results
@lru_cache(maxsize=512)
def geocode_address(address, retries=3):
    if not isinstance(address, str):
      return None, None
    try:
        location = geolocator.geocode(address)
        return (location.latitude, location.longitude) if location else (None, None)
    except (GeocoderTimedOut, GeocoderServiceError, GeocoderUnavailable) as e:
      if retries > 0:
        time.sleep(1) # Wait for one second before retrying
        return geocode_address(address, retries-1)
      else:
         print(f"Geocoding failed for {address} after {retries} retries: {e}")
         return None, None

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

    # Display the full data
    st.write("Full Data:")
    st.write(data)

    # Display the first few rows of the data
    st.write("Data Preview:")
    st.write(data.head())


    # Allow user to select address column
    address_column = st.selectbox("Select the column with addresses:", data.columns)

    if address_column:
        # Verify that the address column exists and contains strings
        if address_column not in data.columns:
            st.error(f"The specified column '{address_column}' was not found in the dataset.")
        else:
            data[address_column] = data[address_column].astype(str)

            # Geocode addresses with progress bar
            st.write("Geocoding addresses...")
            progress_bar = st.progress(0)
            total_addresses = len(data)

            # Create a new column to indicate geocoding failure
            data['GeocodingFailed'] = False
            for index, row in data.iterrows():
               coords = geocode_address(row[address_column])
               if coords == (None, None):
                  data.loc[index,'GeocodingFailed'] = True
                  data.loc[index,'Latitude'] = None
                  data.loc[index,'Longitude'] = None
               else:
                   data.loc[index,'Latitude'] = coords[0]
                   data.loc[index,'Longitude'] = coords[1]

               progress_bar.progress((index + 1) / total_addresses)


            # Create a map visualization
            fig = px.scatter_mapbox(data, lat='Latitude', lon='Longitude', hover_name=address_column,
                                     color='GeocodingFailed', color_discrete_sequence=['blue','red'],
                                     mapbox_style="carto-positron", zoom=10, title="Customer Locations")

            # Update the hover template to not show the 'GeocodingFailed' boolean
            fig.update_traces(hovertemplate="%{hovertext}")


            st.plotly_chart(fig)

            # Identify and display unplotted areas
            unplotted = data[data['Latitude'].isnull() | data['Longitude'].isnull()]
            if not unplotted.empty:
                st.write("Unplotted Areas:")
                st.write(unplotted[[address_column]]) #Show the address column that we used
            else:
               st.success("All addresses were successfully geocoded!")

