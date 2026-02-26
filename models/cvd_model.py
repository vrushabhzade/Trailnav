import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler
from sklearn.ensemble import RandomForestClassifier
import shap
import os
import pickle
from loguru import logger

class CVDModel:
    def __init__(self, data_path="data/heart_disease.csv", model_dir="models/saved"):
        self.data_path = data_path
        self.model_dir = model_dir
        self.scaler = StandardScaler()
        self.model = RandomForestClassifier(n_estimators=100, random_state=42)
        self.explainer = None
        self.feature_names = [
            'age', 'sex', 'cp', 'trestbps', 'chol', 'fbs', 'restecg', 
            'thalach', 'exang', 'oldpeak', 'slope', 'ca', 'thal'
        ]
        self.is_trained = False
        
        if not os.path.exists(self.model_dir):
            os.makedirs(self.model_dir)

    def load_and_train(self):
        """Loads the dataset, preprocesses it, and trains the Random Forest model."""
        if not os.path.exists(self.data_path):
            logger.error(f"Dataset not found at {self.data_path}")
            return False
        
        try:
            columns = self.feature_names + ['target']
            df = pd.read_csv(self.data_path, names=columns, na_values='?')
            
            # Basic preprocessing
            df['ca'] = df['ca'].fillna(df['ca'].mode()[0])
            df['thal'] = df['thal'].fillna(df['thal'].mode()[0])
            df['target'] = df['target'].apply(lambda x: 1 if x > 0 else 0)
            
            X = df.drop('target', axis=1)
            y = df['target']
            
            # Scaler fit and model train
            X_scaled = self.scaler.fit_transform(X)
            self.model.fit(X_scaled, y)
            
            # Initialize SHAP explainer
            self.explainer = shap.TreeExplainer(self.model)
            self.is_trained = True
            logger.info("CVD Model trained successfully.")
            return True
        except Exception as e:
            logger.exception(f"Error training CVD model: {e}")
            return False

    def predict(self, patient_features: dict):
        """
        Predicts CVD risk for a given patient.
        patient_features: dict containing the 13 features.
        """
        if not self.is_trained:
            if not self.load_and_train():
                return None
        
        try:
            # Convert dict to array in correct order
            data = [patient_features[f] for f in self.feature_names]
            X_input = np.array(data).reshape(1, -1)
            X_scaled = self.scaler.transform(X_input)
            
            # Predict
            prob = self.model.predict_proba(X_scaled)[0][1]
            risk_level = "High" if prob > 0.5 else "Low"
            
            # SHAP explanation
            shap_values = self.explainer.shap_values(X_scaled)
            
            if isinstance(shap_values, list):
                # Taking values for the positive class (presence of disease)
                shap_vals = shap_values[1][0] if len(shap_values) > 1 else shap_values[0][0]
            else:
                # Handle potential dimensionality variance
                if len(shap_values.shape) == 3:
                     shap_vals = shap_values[0, :, 1]
                else:
                     shap_vals = shap_values[0]

            # Pair feature names with their importance for this prediction
            explanations = dict(zip(self.feature_names, shap_vals.tolist()))
            
            # Sort explanations by absolute value to find most impactful features
            sorted_explanations = sorted(explanations.items(), key=lambda x: abs(x[1]), reverse=True)
            
            return {
                "risk_probability": round(float(prob), 4),
                "risk_level": risk_level,
                "top_factors": sorted_explanations[:5]
            }
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return None

# Singleton instance
cvd_model_engine = CVDModel()
