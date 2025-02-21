import streamlit as st
import pandas as pd
import altair as alt
import numpy as np

##
st.set_page_config(layout="wide")

##
df = pd.read_csv("gradeData.csv")
df.drop(df.columns[9:14], axis=1, inplace=True)
df["Study period"] = df["Study period"].astype(str)

##


column=st.columns(3)

with column[1]:

    st.write("""# Grade Statistics""")
    st.write("""### Select course(s) and year(s)""")


   # course = st.selectbox(
   #     "Choose course:", options=(list(dict.fromkeys(list(df.iloc[:,0])))),
   #     placeholder='Economics I: Microeconomics'
   # )

   # if not course:
   #     st.error("Please select at least one course.")

with st.sidebar:
    pack = st.multiselect(
            "Choose period or course type", ["Semester 1", "Electives"]
    )

    packages = {"Semester 1": ["Data Analytics I", "Global Challenges I"],
                "Electives": ["Finance I", "Business Law II"]}

    if pack:
        pre_course = []
        for package in pack:
            pre_course.extend(packages[package])

    courses = st.multiselect(
        "Choose courses:", list(dict.fromkeys(list(df.iloc[:, 0]))),
        (pre_course if pack else
        ["Economics I: Microeconomics", "Data Analytics I", "Global Challenges I"]))

  #  courses = st.multiselect(
  #      "Choose courses:", list(dict.fromkeys(list(df.iloc[:, 0]))),
  #      ["Economics I: Microeconomics", "Data Analytics I", "Global Challenges I"])

    if not courses:
        st.error("Please select at least one course")

    years = st.multiselect(
        "Choose years:", list(dict.fromkeys(list(df.iloc[:, 1]))),
        ["2021", "2022", "2023", "2024"]
    )
    if not years:
        st.error("Please select at least one year.")

    st.write("""\n""")

col1, col2, col3 = st.columns([1, 2.5, 1])
with col2:
    st.write(df.loc[(df["Course name"].isin(courses)) & df["Study period"].isin(years)].set_index("Course name"))


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

long_filter = long_filter.rename(
    columns={"Course name": "Course", "Study period": "Year", "value": "Percent"})


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
    x=alt.X('Course:N', title='Course'),  # Grouping by Year
    y=alt.Y('Percent:Q', title='Percent', stack='zero'),  # Stacked values
    color=alt.Color('Grade:N', title='Grade',
                    scale=alt.Scale(domain=["Excellent", "Very Good", "Good", "Pass"],
                                    range=["#cc0000", "#ff8e8e", "#8edeff", "#d68eff"]),
                    sort=["Excellent", "Very Good", "Good", "Pass"]),
    order=alt.Order("grade_order:Q", sort="ascending"),# Different colors for Grades
    column=alt.Column('Year:Q', title='Year',),# Grouping by Course
    tooltip=['Course:N', 'Grade:N', "Percent:Q"]
).properties(width=950/max(existing_years,1))

# scale=alt.Scale(scheme='set1')

col1, col2, col3 = st.columns([1, 40, 1])

with col2:
    st.altair_chart(chart)

col3.write("here")

##
long_exc = (df[["Study period", "Course name", "Excellent"]].melt(id_vars=["Study period", "Course name"]).rename(
    columns={"Study period": "Year", "Course name": "Course", "variable": "Grade", "value": "% Excellent"})
)
long_exc = long_exc.loc[(long_exc["Year"].isin(years)) & (long_exc["Course"].isin(courses)),]

chart_2 = alt.Chart(long_exc).mark_area(opacity=0.3).encode(
    x = "Year:O",
    y = alt.Y("% Excellent:Q", stack=None),
    color = "Course:N").properties(width=1100/max(existing_years, 1))


col1, col2, col3 = st.columns([1, 4, 1])

with col2:
    st.altair_chart(chart_2)

##

# REQS - TODO:

# Select course packages (1st year, 1st period etc., specialization)
# Add %failed bar to stacked 100% bar chart (SBC) OPTION

# Add ability to add/view multiple SBCs



# DONE
# Search for course in ALL FIELDS
# Add multiple courses (bars) per year to SBC
# Spreadsheet view: Select courses to display

##
pack = ["A", "B"]
crspack = {"A": ["1", "2"], "B": ["30", "40"]}

temp = []

for i in pack:
    temp.extend(crspack[i])

print(temp)

##

