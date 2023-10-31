# Crawl all links for a given year and semester using the Course Explorer API
# This is a helper function to feed to the crawler methods in store_data.py
# To be run only once

import requests
import xml.etree.ElementTree as ET
def scrape_links():
    year = "2024" # Any valid year for which a schedule has already been released
    semester = "spring" # Can be "fall", "summer", "spring" or "winter"
    data = requests.get(
        f"https://courses.illinois.edu/cisapp/explorer/schedule/{year}/{semester}.xml"
    )
    f = open("links.txt", "a+")
    fileExists = open("links.txt", "r+")
    if fileExists.read() != "":
        print("WARN: links.txt has already been populated")
        return

    root = ET.fromstring(data.text)

    # Get a list of all available subjects for that semester
    r = root.find("subjects")
    for sub in r:
        subject_link = sub.get("href")
        sub_xml = requests.get(subject_link)
        parsed_xml = ET.fromstring(sub_xml.text)

        # Iterate over the courses for each subject, adding the XML link to a file
        courses = parsed_xml.find("courses")
        str = ""
        for course in courses:
            course_link = course.get("href")
            str += f"{course_link}\n"
        f.write(str)
