import pytest
from glazzbocks import DataExplorer, MLPipeline, ModelDiagnostics, ModelInterpreter
import pandas as pd
from sklearn.linear_model import LinearRegression

@pytest.fixture
def sample_data():
    df = pd.DataFrame({
        'feature1': [1, 2, 3, 4],
        'feature2': [5, 6, 7, 8],
        'target': [10, 20, 30, 40]
    })
    return df

def test_dataexplorer_init(sample_data):
    explorer = DataExplorer(sample_data, target_col='target')
    assert explorer is not None

def test_mlpipeline_basic(sample_data):
    pipeline = MLPipeline(model=LinearRegression())
    X_train, X_test, y_train, y_test = pipeline.split_data(sample_data, "target")
    pipeline.build_pipeline(X_train)
    pipeline.fit(X_train, y_train)
    results = pipeline.evaluate_on_test(X_test, y_test)
    assert results is not None

def test_modeldiagnostics_auto(sample_data):
    pipeline = MLPipeline(model=LinearRegression())
    X_train, X_test, y_train, y_test = pipeline.split_data(sample_data, "target")
    pipeline.build_pipeline(X_train)
    pipeline.fit(X_train, y_train)
    diagnostics = ModelDiagnostics(pipeline.pipeline)
    assert diagnostics is not None

def test_modelinterpreter_shap(sample_data):
    X = sample_data[['feature1', 'feature2']]
    y = sample_data['target']
    model = LinearRegression().fit(X, y)
    interpreter = ModelInterpreter(model, X, y)
    assert interpreter is not None
