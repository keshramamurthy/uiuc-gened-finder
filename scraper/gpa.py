import csv
import sqlite3
from store_data import get_all_gened_courses, save_gpa_data, DATABASE_PATH

CSV_FILENAME = "gpa-dataset.csv"

# Parse the GPA CSV Dataset and store all the GPA data for available GenEd courses
# LIMITATION: This only stores GPA data of courses classified as GenEds
# This is to save space and execution time by only querying relevant data
def geneds_gpa_calc():
    # Import path from store_data.py
    con = sqlite3.connect(DATABASE_PATH)
    cur = con.cursor()

    csvfile = open(CSV_FILENAME)
    reader = csv.DictReader(csvfile)

    # LIMITATION: This only stores GPA data of courses with their most relevant GPA data being published IN 2019 OR LATER
    rows = list(filter(lambda r: int(r["Year"]) > 2018, list(reader)))

    # Query for all the gened courses only
    geneds = get_all_gened_courses(cur)
    for gened_obj in geneds:
        subject_id = gened_obj[1]
        course_id = gened_obj[2]
        course_name = subject_id + " " + course_id

        course_sections = list(filter(lambda c: c["Subject"] == subject_id and c["Number"] == course_id, rows))

        # If no GPA data, continue -- the University has not published it
        if course_sections == None or len(course_sections) == 0:
            continue

        course_data = course_gpa_data(course_sections)

        course_gpa = course_data[0]
        high_grades_percentage = f"{course_data[1]}%"
        low_grades_percentage = f"{course_data[2]}%"

        db_data = (subject_id, course_id, course_gpa, high_grades_percentage, low_grades_percentage)
        # print(f"{course_name}: GPA: {course_data[0]}, 4.0 Percentage: {course_data[1]}%, Low Grade Percentage: {course_data[2]}%")

        save_gpa_data(db_data, cur)
        con.commit()

# Helper method to calculate the average GPA, percentage of 4.0s, and percentage of grades below C of a course, given a list of the course's sections
# (Course average GPA, percentage of 4.0s, percentage of grades <= C)
def course_gpa_data(course_sections):
    average_gpas = []
    total_students = 0
    a_or_plus_grades = 0
    grades_below_c = 0
    for section in course_sections:
        section_data = section_gpa_data(section)

        average_gpas.append(section_data[0])
        total_students += section_data[1]
        a_or_plus_grades += section_data[2]
        grades_below_c += section_data[3]

    course_average_gpa = round(sum(average_gpas) / len(average_gpas), 2)

    perfect_percentage = round((a_or_plus_grades / total_students) * 100, 2)
    low_grade_percentage = round((grades_below_c / total_students) * 100, 2)

    return (course_average_gpa, perfect_percentage, low_grade_percentage)


# Helper method to calculate the data of a section:
# (Average GPA, total students, total 4.0s, total grades <= C)
def section_gpa_data(row):
    a_plus = int(row["A+"])
    a_reg = int(row["A"])
    a_minus = int(row["A-"])
    b_plus = int(row["B+"])
    b_reg = int(row["B"])
    b_minus = int(row["B-"])
    c_plus = int(row["C+"])
    c_reg = int(row["C"])
    c_minus = int(row["C-"])
    d_plus = int(row["D+"])
    d_reg = int(row["D"])
    d_minus = int(row["D-"])
    f_reg = int(row["F"])
    
    total_grades = a_plus + a_reg + a_minus + b_plus + b_reg + b_minus + c_plus + c_reg + c_minus + d_plus + d_reg + d_minus + f_reg
    total_gpa = ((a_plus + a_reg) * 4.00) + (a_minus * 3.67) + (b_plus * 3.33) + (b_reg * 3.00) + (b_minus * 2.67) + (c_plus * 2.33) + (c_reg * 2.00) + (c_minus * 1.67) + (d_plus * 1.33) + (d_reg * 1.00) + (d_minus * 0.67)

    average_gpa = round(total_gpa / total_grades, 2)
    return (average_gpa, total_grades, (a_plus + a_reg), (c_reg + c_minus + d_plus + d_minus + d_reg + f_reg))