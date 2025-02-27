import streamlit as st
import pandas as pd
import altair as alt

global courses
global num_courses
global years
global grades
global flag
global grades


def chart(data, passfail, num_courses):
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
        column=alt.Column('Course:N', title=None, header=alt.Header(labelFontSize=13,
                                                                    labelAngle=label_angle, labelAlign=label_align,
                                                                    labelColor="black")),
        # Grouping by Course
        tooltip=['Course:N', 'Grade:N', "Percent:Q"]).properties(width=600 / max(num_courses, 1))

    if passfail:
        st.markdown("***One or more selected courses seem to be Pass/Fail. Their grade statistics are shown as 0.***")
    st.altair_chart(chart)

    return


def long_df(crs, grades, years, periods=None):
    passfail = False
    temp = grades.loc[grades["full_name"].isin(crs)].copy()
    if periods is not None:
        temp = temp.loc[grades["period"].isin(periods),]

    # Check if any course's grades only contains zeroes (= pass/fail)
    for name in set(temp["Course name"]):
        grade_set = set(temp.loc[temp["Course name"] == name, ["Excellent", "Very Good", "Good", "Pass"]].values[0])
        if grade_set == {0.0}:
            passfail = True
            break

    long = temp.melt(id_vars=["full_name", "year"], var_name="Grade")
    long_filter = long.loc[long["year"].isin(years) &
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

    return long_filter, passfail


def line_chart(courses, grades, years):
    st.markdown("#")
    long_exc = (grades[["year", "full_name", "Excellent"]].melt(id_vars=["year", "full_name"]).rename(
        columns={"year": "Year", "full_name": "Course", "variable": "Grade", "value": "% Excellent"}))

    long_exc = long_exc.loc[(long_exc["Year"].isin(years)) & (long_exc["Course"].isin(courses)),]

    selection = alt.selection_point(fields=['Course'], bind='legend')
    chart_2 = (alt.Chart(long_exc, title=alt.TitleParams(
        "% Excellent for every selected course | Click on course name for highlight",
        anchor="middle")).mark_line().encode(
        x="Year:O",
        y=alt.Y("% Excellent:Q", stack=None),
        color="Course:N",
        opacity=alt.condition(selection, alt.value(1), alt.value(0.2)))).properties(
        width=1100).add_selection(selection)

    col1, col2, col3 = st.columns([1, 4, 1])
    with col2:
        st.altair_chart(chart_2)