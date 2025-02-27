import streamlit as st
import pandas as pd
import altair as alt
import numpy as np
import openpyxl

##
st.set_page_config(layout="wide")

##
df = pd.read_csv("gradeData.csv")
df.drop(df.columns[9:14], axis=1, inplace=True)
df["Study period"] = df["Study period"].astype(str)

grades = pd.read_excel("sse_grade_stats_data.xlsx", sheet_name="Cleaned Data")
grades["year"] = grades["year"].astype(str)

unique_courses = list(
    dict.fromkeys(grades["full_name"].tolist()))  # translate the list to and from dict to get unique courses
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

period_abbreviation = {"Period 1": "P1",
                       "Period 2": "P2",
                       "Period 3": "P3",
                       "Period 4": "P4"}

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

##
if "courses" not in st.session_state:
    st.session_state.courses = ["BE501 Economics I: Microeconomics", "BE601 Data Analytics I",
                                "BE801 Global Challenges I"]

if "filter" not in st.session_state:
    st.session_state.filter = []

if "pre_select" not in st.session_state:
    st.session_state.pre_select =  None

def chart(data):
    global num_courses
    label_angle = (0 if (num_courses <= 6) else -90)
    label_align = ("center" if (num_courses <= 6) else "right")
    chart = alt.Chart(data).mark_bar().encode(
        x=alt.X('Year:N', title='Year'),  # Grouping by Year
        y=alt.Y('Percent:Q', title='Percent', stack='zero'),  # Stacked values
        color=alt.Color('Grade:N', title='Grade',
                        scale=alt.Scale(domain=["Excellent", "Very Good", "Good", "Pass"],
                                        range=["#cc0000", "#ff8e8e", "#8edeff", "#d68eff"]),
                        sort=["Excellent", "Very Good", "Good", "Pass"]),
        order=alt.Order("grade_order:Q", sort="ascending"),  # Different colors for Grades
        column=alt.Column('Course:N', title=None, header=alt.Header(labelFontSize=13, labelFontWeight="bold",
                                                                    labelAngle=label_angle, labelAlign=label_align)),
        # Grouping by Course
        tooltip=['Course:N', 'Grade:N', "Percent:Q"]).properties(width=600 / max(num_courses, 1))

    return chart


def long_df(crs, periods=None):
    global years
    temp = grades.copy()
    if periods is not None:
        temp = temp.loc[grades["period"].isin(periods),]

    long = temp.melt(id_vars=["full_name", "year"], var_name="Grade")
    long_filter = long.loc[long["full_name"].isin(crs) &
                           long["year"].isin(years) &
                           long["Grade"].isin(["Excellent", "Very Good", "Good", "Pass"]),]

    long_filter = long_filter.rename(
        columns={"full_name": "Course", "year": "Year", "value": "Percent"})

    grade_order = {
        "Pass": 0,
        "Good": 1,
        "Very Good": 2,
        "Excellent": 3
    }

    long_filter["grade_order"] = long_filter["Grade"].map(grade_order)

    return long_filter


def thesis(subjects):
    global years
    global grades
    global num_courses
    num_courses = len(subjects)

    st.write("## Thesis Statistics")

    col1, col2, col3 = st.columns([1, 10, 1])
    df_table = grades.drop(["Course name", "Study period", "Course no."], axis=1).rename(
        columns={"year": "Year", "No of registered students": "No. Students", "period": "Period",
                 "full_name": "Course name"}).copy()
    df_table = df_table[["Course name", "Year", "Period", "No. Students", "Main exam", 'At present', 'Excellent',
                         'Very Good', 'Good', 'Pass']]
    with col2:
        st.dataframe(
            df_table.loc[(df_table["Course name"].isin(courses)) & df_table["Year"].isin(years)].set_index(
                "Course name"),
            width=1000)

    col1, col2, col3 = st.columns([1, 100, 1])
    with col2:
        st.write("### Fall")
        st.altair_chart(chart(long_df(subjects, ["P1"])))
        st.write("### Spring")
        st.altair_chart(chart(long_df(subjects, ["P3"])))


def update_cache():
    st.session_state.courses = update_prefill(st.session_state.courses)


def update_prefill(courses):
    selectable = selectable_courses()
    cache = [course for course in courses if course in set(selectable)]

    return cache


def selectable_courses():
    global course_sets
    global filter
    global unique_courses

    if filter:
        selectable = []
        for i in st.session_state.filter:
            selectable.extend(course_sets[i])
    else:
        selectable = unique_courses

    return selectable

def clear_spec():
    st.session_state.pre_select = None


##

column = st.columns(3)

with column[1]:
    st.write("""# Grade Statistics""")
    st.markdown('*Note: If graph shows 0, the course is likely pass/fail*')
    st.markdown("###")

# course = st.selectbox(
#     "Choose course:", options=(list(dict.fromkeys(list(df.iloc[:,0])))),
#     placeholder='Economics I: Microeconomics'
# )

# if not course:
#     st.error("Please select at least one course.")

with st.sidebar:
    st.write("""# Select years""")

    years = st.multiselect(
        "Select years:", unique_years,
        ["2022", "2023", "2024"]
    )
    if not years:
        st.error("Select at least one year.")

    st.write("## Select a year or specialization to automatically fill in the courses")
    pre_select = st.selectbox(
        "Select a year or specialization to automatically fill in the courses",
        ("First Year", "Specializations"),
        index=None,
        placeholder="Year or Specialization",
        label_visibility="collapsed",
        key = "pre_select"
    )

    match pre_select:
        case "First Year":
            # in order to display the table with all Y1 courses

            mandatory_courses = course_dict["Y1"]["P1"].copy()  # init courses as first period
            for i in range(2, 5):  # add period 2-4's courses to course list
                mandatory_courses.extend(course_dict["Y1"]["P{}".format(i)])

            num_courses = 3  # to determine how wide the stacked bar chart(s) should be (3 courses per period/chart)

            flag = "Y1"

        case "Specializations":
            flag = "spec"

            specs = st.multiselect(
                "Choose specializations to compare", ["Accounting", "Economics", "Finance", "Management", "Marketing"]
            )
            st.button("Clear specialization", on_click=clear_spec)

            if not specs:
                st.error("Please select at least one specialization")
            else:
                # create list of all courses in all selected specializations
                courses = course_dict["Spec"][
                    "{}".format(specs[0])].copy()  # init courses as first selected specialization
                for i in range(1, len(specs)):  # add period 2-4's courses to course list
                    try:
                        courses.extend(course_dict["Spec"]["{}".format(specs[i])])
                    except:
                        break

                num_courses = len(specs)
                # period one courses are the first course of every spec i.e the even indexes in the course list
                period1 = [courses[i] for i in range(0, len(courses)) if i % 2 == 0]
                period2 = list(set(courses) - set(period1))  # the rest are period two courses


    st.write("# Filter courses by period")
    filter = st.multiselect(
        "Period", ["Period 1", "Period 2", "Period 3", "Period 4"],
        placeholder="Choose periods", label_visibility="collapsed", key="filter",
        on_change=update_cache, args=(),
        disabled=(True if pre_select else False))

    if st.session_state.courses != update_prefill(st.session_state.courses):
        st.session_state.courses = update_prefill(st.session_state.courses)

    # function that creates a multiselect for each period-filter selecte

    if filter:
        selectables = selectable_courses()
        flag = "filter"
        periods = [period_abbreviation["{}".format(p)] for p in filter]
    if pre_select:
        selectables = unique_courses
        periods = None
    else:
        selectables = unique_courses
        periods, flag = None, None

    st.write("# Select courses")

    courses = st.multiselect("Choose courses:", selectables,
                             placeholder="Select courses",
                             label_visibility="collapsed",
                             key="courses",
                             disabled=(True if pre_select else False))

    if not courses and not pre_select:
        st.error("Select at least one course")
    num_courses = len(courses)

    # THESIS SWITCH
    st.write("## Statistics for BSc/MSc Thesis")

    level = st.selectbox("BSc or MSc", ("Bachelor", "Master"), index=None, placeholder="BSc or MSc",
                         label_visibility="collapsed", disabled=(True if pre_select else False))
    match level:
        case "Bachelor":
            subjects = st.multiselect("Select subject:",
                                      ["BE351 Degree Project in Accounting & Financial Mgmt",
                                       "BE551 Degree Project in Economics",
                                       "BE451 Degree Project in Finance",
                                       "BE151 Degree Project in Management",
                                       "BE251 Degree Project in Marketing"],
                                      placeholder="Select subject")
        case "Master":
            subjects = st.multiselect("Select subject:", ["3350 Thesis in Accounting and Financial Management",
                                                          "5350 Thesis in Economics",
                                                          "4350 Thesis in Finance",
                                                          "1351 Thesis in Business & Management",
                                                          "6181 MIB Research Project"],
                                      placeholder="Select subject")
        case _:
            subjects = False

    if subjects and not pre_select:
        flag = "thesis"

col1, col2, col3 = st.columns([1, 40, 1])
df_table = grades.drop(["Course name", "Study period", "Course no."], axis=1).rename(
    columns={"year": "Year", "No of registered students": "No. Students", "period": "Period",
             "full_name": "Course name"}).copy()
df_table = df_table[["Course name", "Year", "Period", "No. Students", "Main exam", 'At present', 'Excellent',
                     'Very Good', 'Good', 'Pass']]

if flag != "thesis":
    try:
        with col2:
            if flag != ("filter"):
                st.dataframe(
                    df_table.loc[(df_table["Course name"].isin(courses)) & df_table["Year"].isin(years)].set_index(
                        "Course name"),
                    width=2000)
            else:
                st.dataframe(
                    df_table.loc[(df_table["Course name"].isin(courses)) & df_table["Year"].isin(years) &
                                 df_table["Period"].isin(periods)].set_index("Course name"),
                    width=2000)

            st.markdown("# ")
    except:
        st.write("## No courses selected")

##


# scale=alt.Scale(scheme='set1')
col1, col2, col3 = st.columns([1, 40, 1])

try:
    with col2:

        match flag:
            case "Y1":
                st.write("## First Period")
                st.altair_chart(chart(long_df(course_dict["Y1"]["P1"])))
                st.write("## Second Period")
                st.altair_chart(chart(long_df(course_dict["Y1"]["P2"])))
                st.write("## Third Period")
                st.altair_chart(chart(long_df(course_dict["Y1"]["P3"])))
                st.write("## Fourth Period")
                st.altair_chart(chart(long_df(course_dict["Y1"]["P4"])))

            case "spec":
                if "Economics" in specs:
                    st.write(
                        """Note: The second course in the economics specialization - The Economic Approach to Policy Design - is new, starting in 2025. Thus, there are no statistics for this course.""")
                st.write("## First Period")
                st.altair_chart(chart(long_df(period1)))
                st.write("## Second Period")
                st.altair_chart(chart(long_df(period2)))

            case "filter":
                st.altair_chart(chart(long_df(courses, periods)))

            case "thesis":
                thesis(subjects)

            case _:
                st.altair_chart(chart(long_df(courses)))




except:
    print("something wrong")
    pass

# col3.write("here") # DEBUGGING

## Area Chart
st.markdown("#")
long_exc = (grades[["year", "full_name", "Excellent"]].melt(id_vars=["year", "full_name"]).rename(
    columns={"year": "Year", "full_name": "Course", "variable": "Grade", "value": "% Excellent"})
)
try:
    long_exc = long_exc.loc[(long_exc["Year"].isin(years)) & (long_exc["Course"].isin(courses)),]

    selection = alt.selection_point(fields=['Course'], bind='legend')
    chart_2 = (alt.Chart(long_exc, title=alt.TitleParams(
        "% Excellent for every selected course | Click on course name for highlight",
        anchor="middle")).mark_line().encode(
        x="Year:O",
        y=alt.Y("% Excellent:Q", stack=None),
        color="Course:N",
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)))).properties(
        width=1100 / max(num_courses, 1)).add_selection(selection)

    col1, col2, col3 = st.columns([1, 4, 1])

    with col2:
        if flag != "thesis":
            st.altair_chart(chart_2)
except:
    pass

##

# REQS - TODO:

# Select course packages (1st year, 1st period etc., specialization)
# Add %failed bar to stacked 100% bar chart (SBC) OPTION
# Add flags to hide/display fields

# Add ability to add/view multiple SBCs


# DONE
# Search for course in ALL FIELDS
# Add multiple courses (bars) per year to SBC
# Spreadsheet view: Select courses to display
