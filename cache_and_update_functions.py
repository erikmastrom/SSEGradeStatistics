import streamlit as st

global course_sets
global filter
global unique_courses

def update_cache(course_sets, unique_courses):
    st.session_state.courses = update_prefill(st.session_state.courses, course_sets, unique_courses)


def update_prefill(courses, course_sets, unique_courses):
    selectable = selectable_courses(course_sets, unique_courses)
    cache = [course for course in courses if course in set(selectable)]

    return cache


def selectable_courses(course_sets, unique_courses):
    if st.session_state.filter:
        st.write("in function")
        selectable = []
        for i in st.session_state.filter:
            selectable.extend(course_sets[i])
    else:
        selectable = unique_courses
        st.write("no filter")

    return selectable


def clear_spec():
    st.session_state.pre_select = None