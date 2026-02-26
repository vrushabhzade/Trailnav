import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import classification_report, confusion_matrix, roc_auc_score, roc_curve
import shap
import os

# Set plotting style
sns.set(style="whitegrid")

def load_and_preprocess_data(filepath):
    """
    Loads the UCI Heart Disease dataset, handles missing values, and preprocesses features.
    """
    # Column names for the UCI Heart Disease dataset
    columns = [
        'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
        'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal', 'target'
    ]
    
    # Load data
    df = pd.read_csv(filepath, names=columns, na_values='?')
    
    # Handle missing values
    # In this dataset, missing values are rare and often represented by '?' (handled by na_values)
    # Mapping missing values to median/mode
    df['ca'] = df['ca'].fillna(df['ca'].mode()[0])
    df['thal'] = df['thal'].fillna(df['thal'].mode()[0])
    
    # Target transformation: 0 (no disease), >0 (disease)
    # The original dataset has values 0-4. 0 means absent, 1-4 mean present.
    df['target'] = df['target'].apply(lambda x: 1 if x > 0 else 0)
    
    return df

def perform_eda(df, output_dir='eda_plots'):
    """
    Performs Exploratory Data Analysis and saves plots.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    # Correlation Heatmap
    plt.figure(figsize=(12, 10))
    sns.heatmap(df.corr(), annot=True, cmap='coolwarm', fmt='.2f')
    plt.title('Feature Correlation Heatmap')
    plt.savefig(f'{output_dir}/correlation_heatmap.png')
    plt.close()
    
    # Target distribution
    plt.figure(figsize=(6, 4))
    sns.countplot(x='target', data=df)
    plt.title('Target Distribution (0: No Disease, 1: Disease)')
    plt.savefig(f'{output_dir}/target_distribution.png')
    plt.close()
    
    # Age vs Heart Disease
    plt.figure(figsize=(10, 6))
    sns.histplot(data=df, x='age', hue='target', kde=True, element="step")
    plt.title('Age Distribution by Heart Disease Presence')
    plt.savefig(f'{output_dir}/age_vs_target.png')
    plt.close()

def train_and_evaluate(df):
    """
    Trains a Random Forest Model and evaluates its performance.
    """
    X = df.drop('target', axis=1)
    y = df['target']
    
    # Split data
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # Scaling
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)
    
    # Train Random Forest
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train_scaled, y_train)
    
    # Predictions
    y_pred = model.predict(X_test_scaled)
    y_prob = model.predict_proba(X_test_scaled)[:, 1]
    
    # Metrics
    print("\n--- Model Evaluation ---")
    print(classification_report(y_test, y_pred))
    print(f"ROC-AUC Score: {roc_auc_score(y_test, y_prob):.4f}")
    
    return model, X_train_scaled, X_test_scaled, X_test, y_test, scaler

def explain_model(model, X_train_scaled, X_test_scaled, feature_names, output_dir='interpretability'):
    """
    Uses SHAP to explain model predictions.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_test_scaled)
    
    # Handle both binary and multi-class shap_values formats
    # Sometimes SHAP returns a list of two arrays for binary, sometimes just one.
    if isinstance(shap_values, list):
        # Taking values for the positive class (presence of disease)
        shap_vals_to_plot = shap_values[1] if len(shap_values) > 1 else shap_values[0]
    else:
        shap_vals_to_plot = shap_values

    # Summary Plot
    plt.figure()
    shap.summary_plot(shap_vals_to_plot, X_test_scaled, feature_names=feature_names, show=False)
    plt.title('SHAP Summary Plot (Heart Disease Presence)')
    plt.savefig(f'{output_dir}/shap_summary.png', bbox_inches='tight')
    plt.close()
    
    print(f"\nInterpretability plots saved to {output_dir}/")

if __name__ == "__main__":
    filepath = "data/heart_disease.csv"
    
    print(f"Current Working Directory: {os.getcwd()}")
    if not os.path.exists(filepath):
        print(f"Error: Dataset {filepath} not found!")
        # Try full path as fallback
        filepath = os.path.abspath(filepath)
        print(f"Trying absolute path: {filepath}")
        if not os.path.exists(filepath):
             print("Absolute path also failed.")
             # Check if we are in the right root
             if "trialnav" not in os.getcwd():
                 print("Warning: Might not be in trialnav directory.")
    
    print("Loading and preprocessing data...")
    df = load_and_preprocess_data(filepath)
    
    print("Performing EDA...")
    perform_eda(df)
    
    print("Training Model...")
    model, X_train_scaled, X_test_scaled, X_test, y_test, scaler = train_and_evaluate(df)
    
    print("Generating Explanations...")
    explain_model(model, X_train_scaled, X_test_scaled, df.columns[:-1])
    
    print("\nDone! Check the 'eda_plots' and 'interpretability' directories for results.")
