import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
from streamlit_extras.stoggle import stoggle

# Set up the connection to Google Sheets
# Establishing a Google Sheets connection
conn = st.connection("gsheets", type=GSheetsConnection)

# Fetch existing vendors data
questions = conn.read(worksheet='questions', usecols=list(range(7)), ttl=5)
questions = questions.dropna(how="all")



# Streamlit app layout
st.title('Procrastination Journal')
st.markdown("""
    <style>
        .stMultiSelect [data-baseweb=select] span{
            max-width: 250px;
            font-size: 0.6rem;
        },
        #stExpander {
    border: 0 !important;}
    </style>
    """, unsafe_allow_html=True)

# hide = """
# <style>
# #stExpander {
#     border: 0 !important;}
# </style>
# """

# st.markdown(hide, unsafe_allow_html=True)
# Define a function to get the options from the 'Options' worksheet
def get_options(sheet_name):
    worksheet = conn.read(worksheet=sheet_name, usecols=list(range(5)), ttl=5)
    options=worksheet.dropna(how="all")
    # Get all the records of the data
    # records = worksheet.get_all_records()
    # Convert to a list of tuples (first column will be the key)
    return options#[tuple(record.values())[0] for record in records if tuple(record.values())[0].strip()]

# Get options for question 2
# Get options for question 2
options_q2 = get_options('options')['Question 2'].dropna().tolist()  # Use the appropriate column name for options
options_q3 = get_options('options')['Question 3'].dropna().tolist()
options_q4 = get_options('options')['Question 4'].dropna().tolist()
options_q5 = get_options('options')['Question 5'].dropna().tolist()

# Start a form for the procrastination journal entries
with st.form("procrastination_journal_form",border=False):
    # st.write("Please answer the following questions:")

    # Create input fields for each question and option
    task = st.text_area("**What task am I avoiding and why?**")
    with st.expander("**What emotions and thoughts are contributing to my procrastination?**"):

        emotion = [st.checkbox(opt) for opt in options_q2]#st.multiselect("**What emotions and thoughts are contributing to my procrastination?**", options_q2,options_q2[-1])
    with st.expander("**What activity am I choosing to do instead?**"):
        activity = [st.checkbox(opt) for opt in options_q3] #st.multiselect("**What activity am I choosing to do instead?**",options_q3,options_q3)
    with st.expander("**What are the immediate and long-term consequences of procrastinating on this task?**"):
        consequences = [st.checkbox(opt) for opt in options_q4]#st.multiselect("**What are the immediate and long-term consequences of procrastinating on this task?**",options_q4,options_q4[2])
    with st.expander("**What is one small step I can take right now towards completing the task?**"):
        step =[st.checkbox(opt) for opt in options_q5]#st.multiselect("**What is one small step I can take right now towards completing the task?**",options_q5,options_q5[2])

    # Submit button for the form
    submitted = st.form_submit_button("Submit Journal Entry")

if submitted:
    # Add a timestamp
    timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')


   
        # Create a new row of vendor data
    answer_data = pd.DataFrame(
        [
            {
                "What task am I avoiding and why?": task,
                "What emotions and thoughts are contributing to my procrastination?": ", ".join(emotion),
                "What activity am I choosing to do instead?": activity,
                "What are the immediate and long-term consequences of procrastinating on this task?": ", ".join(consequences),
                "What is one small step I can take right now towards completing the task?": ", ".join(step),
                "Date and Time": timestamp,
            }
        ]
    )

    # Add the new vendor data to the existing data
    updated_df = pd.concat([questions, answer_data], ignore_index=True)

    # Update Google Sheets with the new vendor data
    conn.update(worksheet='questions', data=updated_df)

    st.success("Vendor details successfully submitted!")
