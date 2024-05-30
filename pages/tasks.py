import streamlit as st
from streamlit_gsheets import GSheetsConnection
import pandas as pd
from datetime import datetime
import random
from streamlit_calendar import calendar
from streamlit_elements import elements, mui, html, dashboard, sync

# Set up the connection to Google Sheets
conn = st.connection("gsheets", type=GSheetsConnection)
url = "https://docs.google.com/spreadsheets/d/1bXjiWIRAUfvEWsHSzYYbpOKs9KUuEwq0MKy_nQ8oKPI/"
tasks = conn.read(worksheet='tasks', usecols=list(range(9)), ttl=5)
tasks = tasks.dropna(how="all")

# Define data types for all columns
tasks['Task ID'] = tasks['Task ID'].astype(int)
tasks['Task Description'] = tasks['Task Description'].astype(str)
tasks['Category'] = tasks['Category'].astype(str)
tasks['Priority'] = tasks['Priority'].astype(str)
tasks['Due Date'] = pd.to_datetime(tasks['Due Date'], errors='coerce')
tasks['Status'] = tasks['Status'].astype(str)
tasks['Created Date'] = pd.to_datetime(tasks['Created Date'], errors='coerce')
tasks['Completed Date'] = pd.to_datetime(tasks['Completed Date'], errors='coerce')
tasks['Notes'] = tasks['Notes'].astype(str)

# Streamlit app layout
st.title('Task Management Dashboard')

# Function to display tasks
# def display_tasks(df):
#     st.dataframe(df)
# Function to display and edit tasks
def display_tasks(df):
    edited_df = st.data_editor(
        df,
        num_rows="fixed",
        column_config={
            "Task ID": st.column_config.NumberColumn("Task ID", disabled=True),
            "Task Description": st.column_config.TextColumn("Task Description"),
            "Category": st.column_config.SelectboxColumn("Category", options=["Work", "Personal", "Medical School", "Other"]),
            "Priority": st.column_config.SelectboxColumn("Priority", options=["High", "Medium", "Low"]),
            "Due Date": st.column_config.DateColumn("Due Date"),
            "Status": st.column_config.SelectboxColumn("Status", options=["Not Started", "In Progress", "Completed"]),
            "Created Date": st.column_config.DateColumn("Created Date", disabled=True),
            "Completed Date": st.column_config.DateColumn("Completed Date", disabled=True),
            "Notes": st.column_config.TextColumn("Notes"),
        },
        use_container_width=True,
        hide_index=True,
        key="task_data_editor"
    )
    return edited_df

# Function to add a new task
def generate_unique_task_id(existing_ids):
    while True:
        new_id = random.randint(1, 10000)  # Adjust the range as needed
        if new_id not in existing_ids:
            return new_id

# Function to add a new task
@st.experimental_dialog("Add a New Task", width="large")
def add_task():
    existing_ids = tasks['Task ID'].tolist()
    task_id = generate_unique_task_id(existing_ids)
    created_date = datetime.now().strftime('%Y-%m-%d')
    status = "Not Started"
    
    with st.form(key='add_task_form'):
        task_description = st.text_input("Task Description", key="task_description_add")
        category = st.selectbox("Category", ["Work", "Personal", "Medical School", "Other"], key="category_add")
        priority = st.selectbox("Priority", ["High", "Medium", "Low"], key="priority_add")
        due_date = st.date_input("Due Date", key="due_date_add")
        notes = st.text_area("Notes", key="notes_add")
        submit_button = st.form_submit_button(label='Add Task')
    
    if submit_button:
        new_task = pd.DataFrame([{
            "Task ID": task_id,
            "Task Description": task_description,
            "Category": category,
            "Priority": priority,
            "Due Date": due_date.strftime('%Y-%m-%d'),
            "Status": status,
            "Created Date": created_date,
            "Completed Date": "",
            "Notes": notes,
        }])
        updated_df = pd.concat([tasks, new_task], ignore_index=True)
        conn.update(worksheet='tasks', data=updated_df)
        st.success("Task added successfully!")
        st.rerun()


# Function to update task status
def update_task_status(task_id, new_status):
    tasks.loc[tasks['Task ID'] == task_id, 'Status'] = new_status
    if new_status == "Completed":
        tasks.loc[tasks['Task ID'] == task_id, 'Completed Date'] = datetime.now().strftime('%Y-%m-%d')
    conn.update(worksheet='tasks', data=tasks)
    st.success("Task status updated successfully!")

# Prepare calendar events from tasks
def prepare_calendar_events(tasks):
    events = []
    for _, row in tasks.iterrows():
        event = {
            "title": row["Task Description"],
            "start": row["Due Date"],
            "end": row["Due Date"],
            "resourceId": row["Category"],
            "backgroundColor": "#FF6C6C" if row["Priority"] == "High" else "#FFAA6C" if row["Priority"] == "Medium" else "#FFDD6C"
        }
        events.append(event)
    return events

# Main interface
tab1, tab2, tab3, tab4 = st.tabs(["View Tasks", "Add Task", "Dashboard", "Calendar"])

with tab1:
    
    # st.header("Your Tasks")
    if st.button("Add Task", key="add_task_button"):
        add_task()
    
    edited_tasks = display_tasks(tasks)
    if st.button("Save Changes", key="save_changes_button"):
        conn.update(worksheet='tasks', data=edited_tasks)
        st.success("Changes saved successfully!")
    
    # task_to_edit = st.selectbox("Select Task to Edit", tasks['Task ID'].tolist(), key="task_to_edit")
    # if st.button("Edit Task", key="edit_task_button"):
    #     task = tasks[tasks['Task ID'] == task_to_edit].iloc[0].to_dict()
    #     edit_task(task)

