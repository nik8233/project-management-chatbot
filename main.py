import pandas as pd

# Path to your project CSV file
DATA_PATH = "Project_Management_Dataset.csv"

# --- Load & Save Data ---
def load_data():
    return pd.read_csv(DATA_PATH)

def save_data(df):
    df.to_csv(DATA_PATH, index=False)

# --- Model 1: Joint Activity Theory Handler ---
def joint_activity_handler(project_name):
    df = load_data()
    row = df[df["Project Name"].str.lower() == project_name.lower()]
    if not row.empty:
        status = row.iloc[0]["Status"]
        completion = row.iloc[0]["Completion%"]
        return f"Project '{project_name}' is currently '{status}' with {completion}% completed."
    return f"Project '{project_name}' not found."

# --- Model 2: Augmentation Handler ---
def augmentation_handler(project_name, update_completion=None):
    df = load_data()
    index = df[df["Project Name"].str.lower() == project_name.lower()].index
    if not index.empty:
        if update_completion is not None:
            df.at[index[0], "Completion%"] = update_completion
            save_data(df)
            return f"Completion for '{project_name}' updated to {update_completion}%."
        return f"You can update completion % for '{project_name}'."
    return f"Project '{project_name}' not found."

#  New: Augmentation Field Updater (Phase, Manager, Status, etc.)
def update_project_field(project_name, field, new_value):
    df = load_data()
    index = df[df["Project Name"].str.lower() == project_name.lower()].index
    if not index.empty and field in df.columns:
        df.at[index[0], field] = new_value
        save_data(df)
        return f"{field} for '{project_name}' updated to '{new_value}'."
    return "Project not found or invalid field selected."

# --- Model 3: Symbiotic Handler (Streamlit Version with Dropdown) ---
def symbiotic_handler_streamlit(selected_status):
    df = load_data()
    df["Normalized Status"] = df["Status"].str.strip().str.lower().str.replace(" ", "").str.replace("-", "")
    norm_status = selected_status.strip().lower().replace(" ", "").replace("-", "")
    matched = df[df["Normalized Status"] == norm_status]

    if matched.empty:
        return f"No projects found with status '{selected_status}'", []
    return f"Projects with status '{selected_status}':", matched["Project Name"].tolist()

# --- Model 4: Shared Mental Model Handler ---
def shared_mental_model_handler(project_name):
    df = load_data()
    row = df[df["Project Name"].str.lower() == project_name.lower()]
    if not row.empty:
        desc = row.iloc[0]["Project Description"]
        phase = row.iloc[0]["Phase"]
        team = row.iloc[0]["Department"]
        return f"'{project_name}' is in the '{phase}' phase. Department: {team}\nOverview: {desc}"
    return f"Project '{project_name}' not found."
