import streamlit as st
from main import (
    joint_activity_handler,
    augmentation_handler,
    symbiotic_handler_streamlit,
    shared_mental_model_handler,
    load_data,
    update_project_field
)

# Dummy credentials
VALID_USERS = {"admin": "password123", "user": "test123"}

# --- Session state for login ---
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

# --- Login Page ---
def login():
    st.title(" Login to Project Management Chatbot")
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")
    if st.button("Login"):
        if username in VALID_USERS and VALID_USERS[username] == password:
            st.session_state.logged_in = True
            st.success(" Logged in successfully!")
        else:
            st.error(" Invalid username or password.")

# --- Chatbot Interface ---
def chatbot_interface():
    st.title(" Project Management Chatbot")

    model = st.selectbox("Choose a model:", [
        "Joint Activity Theory",
        "Augmentation Model",
        "Symbiotic Model",
        "Shared Mental Model"
    ])

    # --- Model 1: Joint Activity Theory ---
    if model == "Joint Activity Theory":
        project = st.text_input("Enter project name:")
        if st.button("Check Status"):
            st.write(joint_activity_handler(project))

    # --- Model 2: Augmentation Model ---
    elif model == "Augmentation Model":
        project = st.text_input("Enter project name:")
        field = st.selectbox("Select field to update", ["Completion%", "Phase", "Project Manager", "Status"])
        new_value = st.text_input(f"Enter new value for {field}:")
        if st.button("Update Project"):
            result = update_project_field(project, field, new_value)
            st.success(result)

    # --- Model 3: Symbiotic Model ---
    elif model == "Symbiotic Model":
        st.subheader(" Symbiotic Model - Filter by Status")
        df = load_data()
        unique_statuses = sorted(df["Status"].dropna().unique())
        status_choice = st.selectbox("Select Project Status", unique_statuses)
        if st.button("Show Projects"):
            status_text, project_list = symbiotic_handler_streamlit(status_choice)
            st.write(status_text)
            for proj in project_list:
                st.markdown(f"- {proj}")

    # --- Model 4: Shared Mental Model ---
    elif model == "Shared Mental Model":
        project = st.text_input("Enter project name:")
        if st.button("Get Project Details"):
            st.write(shared_mental_model_handler(project))

# --- App Flow ---
if not st.session_state.logged_in:
    login()
else:
    chatbot_interface()
