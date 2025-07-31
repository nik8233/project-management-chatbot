import time
from main import (
    joint_activity_handler,
    augmentation_handler,
    symbiotic_handler_streamlit,
    shared_mental_model_handler
)
from utils import load_data

def compare_models():
    df = load_data()
    project_name = df.iloc[0]['Project Name']
    status_choice = df.iloc[0]['Status']

    results = []

    # 1. Joint Activity
    start = time.time()
    joint_result = joint_activity_handler(project_name)
    end = time.time()
    results.append(("Joint Activity", f"{(end - start):.4f}s", "Structured tracking", "Quantitative", "Medium", "Basic progress monitoring"))

    # 2. Augmentation
    start = time.time()
    aug_result = augmentation_handler(project_name)
    end = time.time()
    results.append(("Augmentation", f"{(end - start):.4f}s", "Human input + AI assist", "Semi-quantitative", "Low", "Good for status updates"))

    # 3. Symbiotic
    start = time.time()
    sym_result, _ = symbiotic_handler_streamlit(status_choice)
    end = time.time()
    results.append(("Symbiotic", f"{(end - start):.4f}s", "Mutual control", "Qualitative", "High", "Context-aware interaction"))

    # 4. Shared Mental Model
    start = time.time()
    shared_result = shared_mental_model_handler(project_name)
    end = time.time()
    results.append(("Shared Mental", f"{(end - start):.4f}s", "Team-based understanding", "Qualitative", "Medium", "Deep project context"))

    # Print Results
    print("\n Model Comparison (Terminal View)\n")
    print(f"{'Model':<20}{'Time':<10}{'Efficiency':<25}{'Data Type':<18}{'Complexity':<10}{'Capability'}")
    print("-" * 95)
    for r in results:
        print(f"{r[0]:<20}{r[1]:<10}{r[2]:<25}{r[3]:<18}{r[4]:<10}{r[5]}")
    

if __name__ == "__main__":
    compare_models()
