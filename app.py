import re
import pandas as pd
import numpy as np
import folium
from folium.plugins import MarkerCluster

def parse_amenities(amenities_string):
    amenities_string = amenities_string.strip('{}').strip('"').strip(':')
    amenities_list = re.split(r',\s*', amenities_string)
    return amenities_list

def load_data(path, columns=None):
    return pd.read_csv(path, usecols=columns, dtype=str)

details_path = "./smaller/Details_Data.csv"
price_path = "./smaller/Price.csv"
mesh_path = "./smaller/Mesh_Ids_Data_Itapema.csv"

details_df = load_data(details_path, columns=["ad_id", "aquisition_date", "amenities", "latitude", "longitude"])
price_df = load_data(price_path, columns=["airbnb_listing_id", "price", "aquisition_date"])
mesh_df  = load_data(mesh_path, columns=["airbnb_listing_id","latitude","longitude","aquisition_date","ano","mes","dia"])

potential_features = ["number_of_bedrooms", "number_of_bathrooms", "number_of_guests", "star_rating", "listing_type"]

details_df['amenities_list'] = details_df['amenities'].apply(parse_amenities)

price_df["price"] = pd.to_numeric(price_df["price"], errors='coerce')

# mesh_df["airbnb_listing_id"] = pd.to_numeric(mesh_df["airbnb_listing_id"], errors='coerce')
# price_with_location = price_df.merge(mesh_df, left_on="airbnb_listing_id", right_on="airbnb_listing_id", how="inner")
# price_with_location = price_df.merge(mesh_df, on="airbnb_listing_id", how="inner", suffixes=('_price', '_mesh'))
price_with_location = price_df.merge(details_df, left_on="airbnb_listing_id", right_on="ad_id", how="inner")
avg_revenue_per_location = price_with_location.groupby("ad_id")["price"].mean()

print(price_with_location, avg_revenue_per_location)

m = folium.Map(location=[-27.5969, -48.5333], zoom_start=13)
marker_cluster = MarkerCluster().add_to(m)

for idx, row in avg_revenue_per_location.reset_index().iterrows():
    latitude = price_with_location.loc[price_with_location["ad_id"] == row["ad_id"], "latitude"].values[0]
    longitude = price_with_location.loc[price_with_location["ad_id"] == row["ad_id"], "longitude"].values[0]
    folium.Marker(
        location=[latitude, longitude],
        popup=f"Listing ID: {row['ad_id']}, Avg. Revenue: {row['price']:.2f}",
    ).add_to(marker_cluster)

# Display the map
m.save("./output/map.html")

