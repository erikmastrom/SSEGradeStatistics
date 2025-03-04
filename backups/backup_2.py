import streamlit as st
import pandas as pd
import altair as alt
import openpyxl
from chart_data import chart, long_df
from logic import first_year, thesis, specialization, course_select, table, filter_select
from cache_and_update_functions import update_cache, update_prefill, clear_spec, selectable_courses

##
st.set_page_config(layout="wide")

global clear_spec
global course_dict
global num_courses
global years
global grades
global courses
global periods
global period_abbreviation
#global unique_courses
global course_sets
global filter


##
grades = pd.read_excel("sse_grade_stats_data.xlsx", sheet_name="Cleaned Data")
grades["year"] = grades["year"].astype(str)

unique_courses = list(dict.fromkeys(grades["full_name"].tolist()))
unique_years = list(dict.fromkeys(grades["year"].tolist()))

first_period_entries = grades.loc[grades["period"] == "P1",]
second_period_entries = grades.loc[grades["period"] == "P2",]
third_period_entries = grades.loc[grades["period"] == "P3",]
fourth_period_entries = grades.loc[grades["period"] == "P4",]

# CHANGE THESE TO SETS
first_period = list(dict.fromkeys(first_period_entries["full_name"].tolist()))
second_period = list(dict.fromkeys(second_period_entries["full_name"].tolist()))
third_period = list(dict.fromkeys(third_period_entries["full_name"].tolist()))
fourth_period = list(dict.fromkeys(fourth_period_entries["full_name"].tolist()))

course_sets = {"Period 1": first_period,
               "Period 2": second_period,
               "Period 3": third_period,
               "Period 4": fourth_period}



##
course_dict = {
    "Y1": {"P1": ["BE501 Economics I: Microeconomics", "BE601 Data Analytics I", "BE801 Global Challenges I"],
           "P2": ["BE301 Accounting I: Understanding Financial Reports", "BE101 Management I: Organizing",
                  "BE671 Business Law I"],
           "P3": ["BE602 Data Analytics II", "BE201 Marketing", "BE671 Business Law II"],
           "P4": ["BE701 Innovation", "BE401 Finance I", "BE502 Economics II: Macroeconomics"]},
    "Spec": {"Accounting": ["BE352 Financial Reporting and Financial Markets",
                            "BE353 Performance Measurement and Business Control"],
             "Finance": ["BE452 Investment Management", "BE453 Corporate Finance and Value Creation"],
             "Economics": ["BE552 Using Data to Solve Economic and Social Problems"],
             "Management": ["BE153 Management: Consulting and Change", "BE152 Management: Operations"],
             "Marketing": ["BE252 Applied Marketing Theory", "BE253 Marketing in Practice"]}
}

bsc_thesis = ["BE351 Degree Project in Accounting & Financial Mgmt",
                                       "BE551 Degree Project in Economics",
                                       "BE451 Degree Project in Finance",
                                       "BE151 Degree Project in Management",
                                       "BE251 Degree Project in Marketing"]

msc_thesis = ["3350 Thesis in Accounting and Financial Management",
                                                          "5350 Thesis in Economics",
                                                          "4350 Thesis in Finance",
                                                          "1351 Thesis in Business & Management",
                                                          "6181 MIB Research Project"]

##
if "courses" not in st.session_state:
    st.session_state.courses = ["BE501 Economics I: Microeconomics", "BE601 Data Analytics I",
                                "BE801 Global Challenges I"]

if "filter" not in st.session_state:
    st.session_state.filter = []

if "pre_select" not in st.session_state:
    st.session_state.pre_select = None

if "thesis" not in st.session_state:
    st.session_state.thesis = None

if "flag" not in st.session_state:
    st.session_state.flag = None








##

#column = st.columns(3)
#with column 1

with st.sidebar:
    st.write("# Select years")

    years = st.multiselect(
        "Select years:", unique_years,
        ["2022", "2023", "2024"],
        label_visibility="collapsed"
    )
    if not years:
        st.error("Select at least one year.")

    #FILTER
    st.write("# Filter courses by period")

    filter = st.multiselect(
        "Period", ["Period 1", "Period 2", "Period 3", "Period 4"],
        placeholder="Choose periods", label_visibility="collapsed", key="filter",
        on_change=update_cache, args=(course_sets, unique_courses),
        disabled=(True if st.session_state.pre_select else False))

    if st.session_state.courses != update_prefill(st.session_state.courses, course_sets, unique_courses):
        st.session_state.courses = update_prefill(st.session_state.courses, course_sets, unique_courses)

    if filter and not (st.session_state.pre_select or st.session_state.thesis):
        st.session_state.flag = "filter"
        selectables = selectable_courses(course_sets, unique_courses)
    else:
        st.session_state.flag = None
        selectables = unique_courses


    st.write("# Select courses")
    courses = st.multiselect("Choose courses:", selectables,
                             placeholder="Select courses",
                             label_visibility="collapsed",
                             key="courses",
                             disabled=(True if st.session_state.pre_select else False))

    if not courses and not (st.session_state.pre_select or st.session_state.thesis):
        st.error("Select at least one course")

    # SPECIALIZATION AND MANDATORY COURSES
    st.write("## Select a year or specialization to automatically fill in the courses")
    pre_select = st.selectbox(
        "Select a year or specialization to automatically fill in the courses",
        ("First Year", "Specializations"),
        index=None,
        placeholder="Year or Specialization",
        label_visibility="collapsed",
        key="pre_select"
    )

    match pre_select:
        case "First Year":
            st.button("Clear selection", on_click=clear_spec)
            st.session_state.flag = "first_year"
        case "Specializations":
            specs = st.multiselect(
                "Choose specializations to compare", ["Accounting", "Economics", "Finance", "Management", "Marketing"]
            )
            st.button("Clear specialization", on_click=clear_spec)

            if not specs:
                st.error("Please select at least one specialization")
            else:
                st.session_state.flag = "specialization"

    # THESIS
    st.write("## Statistics for BSc/MSc Thesis")
    level = st.selectbox("BSc or MSc", ("Bachelor", "Master"), index=None, placeholder="BSc or MSc",
                         label_visibility="collapsed", disabled=(True if pre_select else False))
    match level:
        case "Bachelor":
            subjects = st.multiselect("Select subject:", bsc_thesis, placeholder="Select subject",
                                      key="thesis")
        case "Master":
            subjects = st.multiselect("Select subject:", msc_thesis, placeholder="Select subject",
                                      key="thesis")
    if st.session_state.thesis:
        st.session_state.flag = "thesis"

match st.session_state.flag:
    case "filter":
       filter_select(courses, grades, years)
    case "first_year":
        first_year(grades, years, course_dict)
    case "specialization":
        specialization(grades, years, course_dict, specs)
    case "thesis":
        thesis(subjects, grades, years)
    case _:
        course_select(courses, grades, years)


##

# REQS - TODO:

# Select course packages (1st year, 1st period etc., specialization)
# Add %failed bar to stacked 100% bar chart (SBC) OPTION
# Add flags to hide/display fields
# build function that creates a multiselect for each period-filter selected

# Add ability to add/view multiple SBCs


# DONE
# Search for course in ALL FIELDS
# Add multiple courses (bars) per year to SBC
# Spreadsheet view: Select courses to display
