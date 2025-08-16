import os

import mlflow
import mlflow.sklearn


def log_run(
    model_name,
    params,
    metrics,
    artifacts=None,
    model_object=None,
    experiment_name="glazzbocks",
):
    """
    Logs parameters, metrics, and artifacts to MLflow.
    """
    mlflow.set_experiment(experiment_name)
    with mlflow.start_run():
        mlflow.log_params(params)
        mlflow.log_metrics(metrics)

        if model_object is not None:
            mlflow.sklearn.log_model(model_object, artifact_path="model")

        if artifacts:
            for name, path in artifacts.items():
                if os.path.exists(path):
                    mlflow.log_artifact(path, artifact_path="artifacts")
