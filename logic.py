import streamlit as st
import pandas as pd
import altair as alt
from chart_data import chart, long_df, line_chart
from cache_and_update_functions import update_cache, update_prefill, clear_spec, selectable_courses

global clear_spec
global course_dict
global num_courses
global years
global grades
global courses
global periods
global period_abbreviation
global unique_courses


def first_year(grades, years, course_dict):
    # in order to display the table with all Y1 courses

    mandatory_courses = course_dict["Y1"]["P1"].copy()  # init courses as first period
    for i in range(2, 5):  # add period 2-4's courses to course list
        mandatory_courses.extend(course_dict["Y1"]["P{}".format(i)])

    num_courses = 3  # to determine how wide the stacked bar chart(s) should be (3 courses per period/chart)

    table(grades, mandatory_courses, years, None)

    col1, col2, col3 = st.columns([1, 40, 1])
    with col2:
        st.write("## First Period")
        chart(long_df(course_dict["Y1"]["P1"], grades, years), num_courses)
        st.write("## Second Period")
        chart(long_df(course_dict["Y1"]["P2"], grades, years), num_courses)
        st.write("## Third Period")
        chart(long_df(course_dict["Y1"]["P3"], grades, years), num_courses)
        st.write("## Fourth Period")
        chart(long_df(course_dict["Y1"]["P4"], grades, years), num_courses)

    line_chart(mandatory_courses, grades, years)


def specialization(grades, years, course_dict, specs):
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

        table(grades, courses, years, None)

        col1, col2, col3 = st.columns([1, 40, 1])
        with col2:
            if "Economics" in specs:
                st.write(
                    "Note: The second course in the economics specialization \
                    - The Economic Approach to Policy Design - is new, starting in 2025. \
                    Thus, there are no statistics for this course.")
            st.write("## First Period")
            chart(long_df(period1, grades, years), num_courses)
            st.write("## Second Period")
            chart(long_df(period2, grades, years), num_courses)

            line_chart(courses, grades, years)


def filter_select(courses, grades, years):
    period_abbreviation = {"Period 1": "P1",
                           "Period 2": "P2",
                           "Period 3": "P3",
                           "Period 4": "P4"}

    periods = [period_abbreviation["{}".format(p)] for p in st.session_state.filter]
    num_courses = len(courses)

    if (st.session_state.pre_select or st.session_state.thesis):
        periods = None
        return

    table(grades,courses, years,None)

    col1, col2, col3 = st.columns([1, 40, 1])
    with col2:
        chart(long_df(courses, grades, years, periods=periods),num_courses)

    line_chart(courses, grades, years)

def course_select(courses, grades, years):
    periods = None
    num_courses = len(courses)

    if (st.session_state.pre_select or st.session_state.thesis):
        return

    table(grades,  courses, years,None)

    col1, col2, col3 = st.columns([1, 40, 1])
    with col2:
        chart(long_df(courses, grades, years),num_courses)

    line_chart(courses, grades, years)


def thesis(subjects, grades, years):
    num_courses = len(subjects)

    st.write("## Thesis Statistics")

    col1, col2, col3 = st.columns([1, 10, 1])

    with col2:
        table(grades, subjects, years)

    col1, col2, col3 = st.columns([1, 100, 1])
    with col2:
        st.write("### Fall")
        chart(long_df(subjects, grades, years, periods=["P1"]),num_courses)
        st.write("### Spring")
        chart(long_df(subjects, grades, years, periods=["P3"]),num_courses)

    line_chart(subjects, grades, years)


def table(grades, courses, years, filter = None):
    df_table = grades.drop(["Course name", "Study period", "Course no."], axis=1).rename(
        columns={"year": "Year", "No of registered students": "No. Students", "period": "Period",
                 "full_name": "Course name"}).copy()
    df_table = df_table[["Course name", "Year", "Period", "No. Students", "Main exam", 'At present', 'Excellent',
                         'Very Good', 'Good', 'Pass']]

    col1, col2, col3 = st.columns([1, 100, 1])
    with col2:
        if not filter:
            st.dataframe(df_table.loc[(df_table["Course name"].isin(courses)) & df_table["Year"].isin(years)].set_index(
                "Course name"),
                width=2000)
        else:
            st.dataframe(
                df_table.loc[(df_table["Course name"].isin(courses)) & df_table["Year"].isin(years) &
                             df_table["Period"].isin(periods)].set_index("Course name"),
                width=2000)
