import pandas as pd
import numpy as np
from imblearn.over_sampling import SMOTE
from exception.exception import ProjectXecption
import sys

class Balance:
    def __init__(self):
        self.target_col = None
        self.problem_type = None
        self.smote = SMOTE(random_state=42)
        self.balanced_df_ = None

    def detect_problem_type(self, y: pd.Series):
        """Detect whether the target is classification or regression."""
        if pd.api.types.is_numeric_dtype(y):
            # If continuous (many unique values → regression)
            if y.nunique() > 20:  
                return "regression"
            else:
                return "classification"
        else:
            return "classification"

    def fit(self, df: pd.DataFrame, target: str):
        try:
            self.target_col = target
            y = df[self.target_col]
            self.problem_type = self.detect_problem_type(y)

            if self.problem_type == "regression":
                print("⚠️ Regression problem detected → Skipping balancing.")
                self.balanced_df_ = df.copy()
                return self

            print("✅ Classification problem detected → Applying SMOTE balancing.")
            X = df.drop(columns=[self.target_col])
            X_res, y_res = self.smote.fit_resample(X, y)

            self.balanced_df_ = pd.concat(
                [pd.DataFrame(X_res, columns=X.columns),
                 pd.Series(y_res, name=self.target_col)], axis=1
            )

            print("✅ Balancing Completed using SMOTE.")
            return self

        except Exception as e:
            raise ProjectXecption(e, sys)

    def transform(self, df: pd.DataFrame):
        """Balancing is not applied at inference → just return df."""
        return df

    def fit_transform(self, df: pd.DataFrame, target: str):
        self.fit(df, target)
        return self.balanced_df_
