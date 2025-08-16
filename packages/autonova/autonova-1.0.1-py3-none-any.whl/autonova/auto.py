from autoMLX.data_balancing import Balance
from autoMLX.data_featureEngineering import FeatureEngineer
from autoMLX.data_featureselection import FeatureSelection
from autoMLX.data_preprocessing import Preprocess
from autoMLX.data_spliting import Spliting
from autoMLX.data_transformation import Transformation
import pandas as pd
from pipeline import preprocessing
from model.modelTraining import ModelTrainer
from sklearn.model_selection import KFold, cross_val_score
from pipeline.preprocessing import preprocessPipeline
from exception.exception import ProjectXecption
import sys

class autonova:
    def __init__(self, data: pd.DataFrame, target_col: str):
        if target_col not in data.columns:
            raise ProjectXecption(f"target_col '{target_col}' not found in DataFrame", sys)

        self.data = data
        self.target_col = target_col

        # Internal attributes
        self.__preprocess = None
        self.__train = None
        self.__test = None
        self.__bestmodel = None
        self.__evaluate = None

    def go(self, use_gpu=False, fast_mode=False, cv_splits=5, n_trials=50):
        # Step 1: Preprocessing
        self.__preprocess = preprocessPipeline()
        processed_data = self.__preprocess.fit_transform(df=self.data, target_col=self.target_col)

        # Step 2: Splitting
        splitter = Spliting()
        X_train, X_test, y_train, y_test = splitter.fit_transform(processed_data, target_col=self.target_col)
        self.__train = (X_train, y_train)
        self.__test = (X_test, y_test)

        # Step 3: Model Training
        model_trainer = ModelTrainer(use_gpu=use_gpu, fast_mode=fast_mode, cv_splits=cv_splits, n_trials=n_trials)
        self.__bestmodel = model_trainer.fit(X_train=X_train, y_train=y_train)

        # Step 4: Evaluation
        cv = KFold(n_splits=cv_splits, shuffle=True, random_state=42)
        self.__evaluate = cross_val_score(self.__bestmodel, X_test, y_test, cv=cv).mean()

        return self  # Allow chaining if needed

    @property
    def best_model(self):
        return self.__bestmodel

    @property
    def preprocess_logic(self):
        return self.__preprocess

    @property
    def score(self):
        return self.__evaluate

    @property
    def train_data(self):
        return self.__train

    @property
    def test_data(self):
        return self.__test
