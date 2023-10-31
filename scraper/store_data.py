import sqlite3
import xml.etree.ElementTree as ET
import requests

DATABASE_PATH = "../sp24-courses.db" # MODIFY THIS AS PER SEMESTER/YEAR


# Initialize and store all courses in database
# This function should be run only AFTER scrape_links has been called
def store_data():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    cur.execute("CREATE TABLE IF NOT EXISTS courses(courseTitle, courseDesc, courseID, subjectID, subjectName, creditHrs, url, genEds, pot, location, gpa, highGrades, lowGrades)")

    f = open("links.txt", "r+")
    f_data = f.read()
    if f_data == "":
        raise ValueError("ERR: links.txt is empty")
    links = f_data.split("\n")

    for link in links:
        d = grab_data(link)
        if d != None:
            save_to_db(d, cur)

    con.commit()

# Store term and location information for courses designated as fulfilling general education requirements
# LIMITATION: This only stores data for term and location of courses classified as GenEds
# This is to save space and execution time by only querying relevant data
def store_gened_term_and_location_data():
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    geneds = get_all_gened_courses(cur)
    for raw_gened_obj in geneds:
        url = raw_gened_obj[0]
        subject_id = raw_gened_obj[1]
        course_id = raw_gened_obj[2]
        term_and_loc = get_course_terms_and_locations(url, subject_id, course_id)
        if term_and_loc != None:
            cur.execute(f"UPDATE courses SET pot=\'{term_and_loc[0]}\', location=\'{term_and_loc[1]}\' WHERE url=\'{url}\';")
            con.commit()

# Helper func to get the term and location data of a course
def get_course_terms_and_locations(url, subject_id, course_id):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            print(f"REQUEST FAILED: {url}")
            print(res.status_code)
            return None
        xml = ET.fromstring(res.text)

        sections = xml.find("sections")
        terms = set()
        locs = set()    

        for sec in sections:
            sec_url = f"https://courses.illinois.edu/cisapp/explorer/schedule/2024/spring/{subject_id}/{course_id}/{sec.get('id')}.xml"
            sec_res = requests.get(sec_url)
            if sec_res.status_code != 200:
                print(f"SECTION REQUEST FAILED: {sec_url}")
                print(res.status_code)
                continue
            sec_xml = ET.fromstring(sec_res.text)

            term = sec_xml.find("partOfTerm")
            if term != None:                
                terms.add(term.text)
            else:
                print(f"TERM NOT FOUND AT: ${url}")

            meeting = sec_xml.find("meetings").find("meeting")
            if meeting.find("buildingName") != None:
                locs.add(meeting.find("buildingName").text)
            else:
                locs.add("ONLINE")
        term_str = "~".join(terms)
        loc_str = "~".join(locs)
        return (term_str, loc_str)
    except Exception as err:
        print(err.with_traceback())
        return None

# Helper func to grab the attributes of a specific course using its URL
def grab_data(url):
    try:
        res = requests.get(url)
        if res.status_code != 200:
            return None
        xml = ET.fromstring(res.text)

        course_title = xml.find("label").text
        course_desc = xml.find("description").text
        course_id = xml.get("id").split(" ")[1]
        subject_id = xml.find("parents").find("subject").get("id")
        subject_name = xml.find("parents").find("subject").text
        credit_hours = int(xml.find("creditHours").text.split(" ")[0])
        geneds = ""
        geneds_raw = xml.find("genEdCategories")
    
        if geneds_raw != None:
            temp = []
            for attr in geneds_raw.iter("genEdAttribute"):
                temp.append(attr.get("code"))
            geneds = ",".join(temp)

        return (course_title, course_desc, course_id, subject_id, subject_name, credit_hours, url, geneds)
    except:
        return None
    
# Save course information to the database
def save_to_db(tuple: tuple, cur: sqlite3.Cursor):
    try:
        cur.execute("INSERT INTO courses (courseTitle, courseDesc, courseID, subjectID, subjectName, creditHrs, url, genEds) VALUES (?, ?, ?, ?, ?, ?, ?, ?)", tuple)
    except Exception as err:
        print(err.with_traceback())
        return None
    
# Save the grades & GPA data about a particular course into the database
def save_gpa_data(tuple: tuple[str, str, float, str, str], cur: sqlite3.Cursor):
    if tuple != None:
        try:
            cur.execute(f"UPDATE courses SET gpa={tuple[2]}, highGrades=\'{tuple[3]}\', lowGrades=\'{tuple[4]}\' WHERE subjectID=\'{tuple[0]}\' AND courseID=\'{tuple[1]}\';")
        except Exception as err:
            print(err.with_traceback())
            return None

# Get a list of all courses that fulfill at least one general education requirement
def get_all_gened_courses(cur: sqlite3.Cursor):
    try:
        cur.execute("SELECT url, subjectID, courseID FROM courses WHERE genEds != \"\"")
        res = cur.fetchall()
        return res
    except Exception as err:
        print(err.with_traceback())
        return None