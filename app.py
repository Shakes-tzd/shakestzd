import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime

# Set up the connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
url = "https://docs.google.com/spreadsheets/d/1bXjiWIRAUfvEWsHSzYYbpOKs9KUuEwq0MKy_nQ8oKPI/"
questions = conn.read(worksheet='questions', usecols=list(range(7)), ttl=5)
questions = questions.dropna(how="all")

# Streamlit app layout
st.title('Procrastination Journal')

# Define a function to get the options from the 'Options' worksheet
def get_options(sheet_name):
    worksheet = conn.read(worksheet=sheet_name, usecols=list(range(5)), ttl=5)
    options = worksheet.dropna(how="all")
    return options

# Get options for question 2 to 5
options_q2 = get_options('options')['Question 2'].dropna().tolist()
options_q3 = get_options('options')['Question 3'].dropna().tolist()
options_q4 = get_options('options')['Question 4'].dropna().tolist()
options_q5 = get_options('options')['Question 5'].dropna().tolist()

# Add "Other" option
options_q2.append("Other")
options_q3.append("Other")
options_q4.append("Other")
options_q5.append("Other")

# Create input fields for each question and option
task = st.text_area("**What task am I avoiding and why?**")

# Question 2 to 5 with "Other" option handling


with st.expander("**What emotions and thoughts are contributing to my procrastination?**"):
    emotion_selected = [opt for opt in options_q2 if st.checkbox(opt, key=f"emotion_{opt}")]
    if "Other" in emotion_selected:
        other_emotion = st.text_input("Please specify other emotions or thoughts:", key="other_emotion")
        emotion_selected.append(other_emotion) if other_emotion else None

with st.expander("**What activity am I choosing to do instead?**"):
    activity_selected = [opt for opt in options_q3 if st.checkbox(opt, key=f"activity_{opt}")]
    if "Other" in activity_selected:
        other_activity = st.text_input("Please specify other activities:", key="other_activity")
        activity_selected.append(other_activity) if other_activity else None

with st.expander("**What are the immediate and long-term consequences of procrastinating on this task?**"):
    consequences_selected = [opt for opt in options_q4 if st.checkbox(opt, key=f"consequences_{opt}")]
    if "Other" in consequences_selected:
        other_consequences = st.text_input("Please specify other consequences:", key="other_consequences")
        consequences_selected.append(other_consequences) if other_consequences else None

with st.expander("**What is one small step I can take right now towards completing the task?**"):
    step_selected = [opt for opt in options_q5 if st.checkbox(opt, key=f"step_{opt}")]
    if "Other" in step_selected:
        other_step = st.text_input("Please specify other steps:", key="other_step")
        step_selected.append(other_step) if other_step else None

# Button for submitting journal entry
if st.button("Submit Journal Entry"):
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    answer_data = pd.DataFrame(
        [{
            "What task am I avoiding and why?": task,
            "What emotions and thoughts are contributing to my procrastination?": ", ".join(emotion_selected),
            "What activity am I choosing to do instead?": ", ".join(activity_selected),
            "What are the immediate and long-term consequences of procrastinating on this task?": ", ".join(consequences_selected),
            "What is one small step I can take right now towards completing the task?": ", ".join(step_selected),
            "Date and Time": timestamp,
        }]
    )

    updated_df = pd.concat([questions, answer_data], ignore_index=True)
    conn.update(worksheet='questions', data=updated_df)
    st.success("Journal entry successfully submitted!")