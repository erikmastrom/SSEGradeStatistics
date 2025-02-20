import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

##
st.set_page_config(layout="wide")
st.write(""" # Trying this shit
Hello motherfucker""")

##
df = pd.read_csv("gradeData.csv")
df.drop(df.columns[9:14], axis=1, inplace=True)
df["Study period"] = df["Study period"].astype(str)

##

st.write("""## Grade Statistics
### Select course and year(s)""")
column=st.columns(3)

with column[1]:
    course = st.selectbox(
        "Choose course:", options=(list(dict.fromkeys(list(df.iloc[:,0])))),
        placeholder='Economics I: Microeconomics'
    )

    if not course:
        st.error("Please select at least one course.")

    years = st.multiselect(
        "Choose years:", list(dict.fromkeys(list(df.iloc[:,1]))),
        ["2021","2022", "2023", "2024"]
    )
    if not years:
        st.error("Please select at least one year.")


    st.bar_chart(df.loc[(df["Course name"] == course) & (df["Study period"].isin(years)),],
        x="Study period", y=["Excellent", "Very Good", "Good", "Pass"])

    courses = st.multiselect(
        "Choose courses:", list(dict.fromkeys(list(df.iloc[:, 0]))),
        ["Economics I: Microeconomics", "Data Analytics I", "Global Challenges I"])
##
# tracking how many of the selected years actually contain grade statistics for the selected courses
existing_years = 0
# for every selected in every selected year, if at least one course exists, increase counter
for year in years:
    for course in courses:
        if df.loc[(df["Course name"] == course) & (df["Study period"] == year),].all(axis=1).any():
            # if course/year combination exists in the data
            existing_years += 1
            break  # break as soon as a course is encountered, no need to count all

long = df.melt(id_vars=["Course name", "Study period"], var_name="Grade")
long_filter = long.loc[long["Course name"].isin(courses) &
         long["Study period"].isin(years) &
         long["Grade"].isin(["Excellent","Very Good", "Good", "Pass"]),]


long_filter["Grade"] = pd.Categorical(long_filter["Grade"], categories=["Excellent", "Very Good", "Good", "Pass"],
                                      ordered=True)
grade_order = {
    "Pass":0,
    "Good":1,
    "Very Good":2,
    "Excellent":3
}

long_filter["grade_order"] = long_filter["Grade"].map(grade_order)

chart = alt.Chart(long_filter).mark_bar().encode(
    x=alt.X('Course name:N', title='Course'),  # Grouping by Year
    y=alt.Y('value:Q', title='Percent', stack='zero'),  # Stacked values
    color=alt.Color('Grade:N', title='Grade', scale=alt.Scale(scheme='set1'),
                    sort=["Excellent", "Very Good", "Good", "Pass"]),
    order=alt.Order("grade_order:Q", sort="ascending"),# Different colors for Grades
    column=alt.Column('Study period:Q', title='Year')# Grouping by Course
).properties(width=1100/max(existing_years,1))


col1, col2, col3 = st.columns([1, 10, 1])

with col2:
    st.altair_chart(chart)

col3.write("here")


# REQS - TODO:
# Spreadsheet view: Select courses to display
# Select course packages (1st year, 1st period etc., specialization)
# Add %failed bar to stacked 100% bar chart (SBC) OPTION
# Add multiple courses (bars) per year to SBC
# Add ability to add/view multiple SBCs
# Search for course in ALL FIELDS

##

