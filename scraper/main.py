from scrape_links import scrape_links as scrape
from store_data import store_gened_term_and_location_data, store_data as store

# Initialize and store ALL data

# Comment this out if links have already been scraped and added to the links.txt file
scrape()

# Run this AFTER scrape() has been run at least once
store()

# Run this to update term and location data for geneds
store_gened_term_and_location_data()