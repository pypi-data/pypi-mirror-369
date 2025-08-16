# report_generator.py
import json

def generate_model_report(model, X_test, y_test):
    return {
        "classification_report": classification_report(y_test, model.predict(X_test), output_dict=True),
        "feature_importance": model.feature_importances_.tolist() if hasattr(model, 'feature_importances_') else None,
        "confusion_matrix": confusion_matrix(y_test, model.predict(X_test)).tolist(),
        # You can add SHAP, ROC, etc. here as well
    }
