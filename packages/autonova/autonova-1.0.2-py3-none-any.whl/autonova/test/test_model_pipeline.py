import pandas as pd
import numpy as np
from sklearn.datasets import make_classification, make_regression
from sklearn.model_selection import KFold, cross_val_score

from pipeline.preprocessing import preprocessPipeline
from model.modelTraining import ModelTrainer
from autonova.data_spliting import Spliting
from exception.exception import ProjectXecption

def test_classification_pipeline():
    """Test pipeline on synthetic classification dataset."""
    # 1. Create synthetic classification dataset
    X, y = make_classification(
        n_samples=200,
        n_features=10,
        n_informative=5,
        n_redundant=2,
        random_state=42
    )
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
    df["target"] = y

    target_col = "target"

    # 2. Preprocessing
    preprocess = preprocessPipeline()
    processed_df = preprocess.fit_transform(df=df, target_col=target_col)

    # 3. Split
    splitter = Spliting()
    X_train, X_test, y_train, y_test = splitter.fit_transform(processed_df, target_col=target_col)

    # 4. Train model
    model = ModelTrainer(use_gpu=False, fast_mode=True, cv_splits=3, n_trials=5)
    best_model = model.fit(X_train=X_train, y_train=y_train)

    # 5. Evaluate
    score = best_model.score(X_test, y_test)
    assert score > 0.6, f"Expected regression R² > 0.6, got {score}"

def test_regression_pipeline():
    """Test pipeline on synthetic regression dataset."""
    # 1. Create synthetic regression dataset
    X, y = make_regression(
        n_samples=200,
        n_features=10,
        n_informative=5,
        noise=0.1,
        random_state=42
    )
    df = pd.DataFrame(X, columns=[f"feature_{i}" for i in range(X.shape[1])])
    df["target"] = y

    target_col = "target"

    # 2. Preprocessing
    preprocess = preprocessPipeline()
    processed_df = preprocess.fit_transform(df=df, target_col=target_col)

    # 3. Split
    splitter = Spliting()
    X_train, X_test, y_train, y_test = splitter.fit_transform(processed_df, target_col=target_col)

    # 4. Train model
    model = ModelTrainer(use_gpu=False, fast_mode=True, cv_splits=3, n_trials=5)
    best_model = model.fit(X_train=X_train, y_train=y_train)

    # 5. Evaluate
    score = best_model.score(X_test, y_test)
    assert score > 0.6, f"Expected regression R² > 0.6, got {score}"



