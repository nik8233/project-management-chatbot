import streamlit as st
from main import joint_activity_handler, augmentation_handler, symbiotic_handler, shared_mental_model_handler

st.set_page_config(page_title="Project Management Chatbot", layout="centered")

st.title(" Project Management Chatbot")
st.markdown("Select a model and enter the project name to get started.")

model = st.selectbox("Choose a model:", [
    "Joint Activity Theory", 
    "Augmentation Model", 
    "Symbiotic Model", 
    "Shared Mental Model"
])

project_name = ""
completion = None

if model != "Symbiotic Model":
    project_name = st.text_input("Enter project name:")

if model == "Augmentation Model":
    completion = st.text_input("Update Completion % (optional):")

if st.button("Run Model"):
    if model == "Joint Activity Theory":
        st.info(joint_activity_handler(project_name))

    elif model == "Augmentation Model":
        st.info(augmentation_handler(project_name, completion))

    elif model == "Symbiotic Model":
        st.info(symbiotic_handler())

    elif model == "Shared Mental Model":
        st.info(shared_mental_model_handler(project_name))
