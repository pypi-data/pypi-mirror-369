import pandas as pd
import pickle
from exception.exception import ProjectXecption
import sys
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


class preprocessPipeline:
    def __init__(self, 
                 ):
        """
        Parameters:
        -----------
        preprocessing : data_preprocessing object
        transformation : data_transformation object
        feature_engineering : data_featureEngineering object
        feature_selection : data_featureselection object
        balancing : data_balancing object
        splitting : data_spliting object
        """
        self.preprocessing = Preprocess()
        self.transformation = Transformation()
        self.feature_engineering = FeatureEngineer()
        self.feature_selection = FeatureSelection()
        self.balancing = Balance()
        self.splitting = Spliting()

        self.fitted = False
        self.fitted_df = None
        self.target_col = None

    def fit(self, df: pd.DataFrame, target_col: str):
        print(r"""
     _         _        __  __ _     __  __
    / \  _   _| |_ ___ |  \/  | |    \ \/ /
   / _ \| | | | __/ _ \| |\/| | |     \  / 
  / ___ \ |_| | || (_) | |  | | |___  /  \ 
 /_/   \_\__,_|\__\___/|_|  |_|_____|/_/\_\

           AUTO MLX :::: 1.0.0
""")

        try:
            # Stage 1: Preprocessing
            df = self.preprocessing.fit_transform(df, target_col)
            print(f"Preprocessing Done : {df.shape}")
            print(f"{df.columns}")

            # Stage 2: Transformation
            df = self.transformation.fit_transform(df, target_col)
            print(f"Transformation Done : {df.shape}")
            print(f"{df.columns}")

            # Stage 3: Feature Engineering
            df = self.feature_engineering.fit_transform(df, target_col)
            print(f"Feature Engineering Done : {df.shape}")
            print(f"{df.columns}")

            # Stage 4: Feature Selection
            df = self.feature_selection.fit_transform(df, target_col)
            print(f"Feature Selection Done : {df.shape}")
            print(f"{df.columns}")

            # Stage 5: Balancing
            df = self.balancing.fit_transform(df, target_col)
            print(f"Balancing Done : {df.shape}")
            print(f"{df.columns}")

            self.target_col = target_col
            self.fitted_df = df
            self.fitted = True

            print(" AutoMLPipeline: Fit completed successfully.")
            return self
        except Exception as e:
            raise ProjectXecption(e, sys)

    def transform(self, df: pd.DataFrame):
        if not self.fitted:
            raise ProjectXecption("You must call fit() before transform()", sys)

        try:
            df = self.preprocessing.transform(df)
            df = self.transformation.transform(df)
            df = self.feature_engineering.transform(df)
            df = self.feature_selection.transform(df)
            # ⚠️ Balancing usually not applied at inference; skip for prediction
            return df
        except Exception as e:
            raise ProjectXecption(e, sys)

    def fit_transform(self, df: pd.DataFrame, target_col: str):
        self.fit(df, target_col)
        self.transform(df)
        return self.fitted_df

   