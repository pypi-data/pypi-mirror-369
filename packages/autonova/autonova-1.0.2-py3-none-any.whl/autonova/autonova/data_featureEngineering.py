import pandas as pd
import numpy as np
from sklearn.preprocessing import PolynomialFeatures
from exception.exception import ProjectXecption
import sys

class FeatureEngineer:
    def __init__(self, add_polynomial: bool = True, degree: int = 2, include_interaction: bool = True, fill_na: float = 0.0):
        """
        Parameters:
        -----------
        add_polynomial : bool
            Whether to generate polynomial & interaction features.
        degree : int
            Polynomial degree.
        include_interaction : bool
            Whether to include interaction-only features.
        fill_na : float
            Value to replace NaNs before polynomial transformation.
        """
        self.add_polynomial = add_polynomial
        self.degree = degree
        self.include_interaction = include_interaction
        self.fill_na = fill_na

        self.poly = None
        self.num_cols = []
        self.fitted = False
        self.target_col = None

    def extract_datetime_features(self, df: pd.DataFrame):
        """Extracts year, month, day, weekday from datetime columns."""
        try:
            datetime_cols = df.select_dtypes(include=["datetime64[ns]", "datetime64[ns, UTC]"]).columns

            for col in datetime_cols:
                df[f"{col}_year"] = df[col].dt.year
                df[f"{col}_month"] = df[col].dt.month
                df[f"{col}_day"] = df[col].dt.day
                df[f"{col}_weekday"] = df[col].dt.weekday

            df = df.drop(columns=datetime_cols)  # Drop original datetime cols
            return df
        except Exception as e:
            raise ProjectXecption(e, sys)

    def fit(self, df: pd.DataFrame, target_col: str = None):
        try:
            self.target_col = target_col
            df = self.extract_datetime_features(df)

            # ✅ Remove target column (if provided) before processing
            if self.target_col and self.target_col in df.columns:
                df_no_target = df.drop(columns=[self.target_col])
            else:
                df_no_target = df

            # Identify numeric columns
            self.num_cols = df_no_target.select_dtypes(include=[np.number]).columns.tolist()

            if self.add_polynomial and len(self.num_cols) > 0:
                clean_df = df_no_target[self.num_cols].fillna(self.fill_na)
                self.poly = PolynomialFeatures(
                    degree=self.degree,
                    include_bias=False,
                    interaction_only=not self.include_interaction
                )
                self.poly.fit(clean_df)

            self.fitted = True
            print("✅ FeatureEngineering: Fitted successfully.")
        except Exception as e:
            raise ProjectXecption(e, sys)

    def transform(self, df: pd.DataFrame, target_col: str = None):
        if not self.fitted:
            raise ProjectXecption("You must call fit() before transform()", sys)

        try:
            target_col = target_col or self.target_col
            df = self.extract_datetime_features(df)

            # ✅ Separate target column
            target_series = None
            if target_col and target_col in df.columns:
                target_series = df[target_col]
                df = df.drop(columns=[target_col])

            # Ensure consistency with training columns
            current_num_cols = [col for col in self.num_cols if col in df.columns]

            if self.add_polynomial and self.poly is not None and len(current_num_cols) > 0:
                clean_df = df[current_num_cols].fillna(self.fill_na)
                poly_features = self.poly.transform(clean_df)

                poly_df = pd.DataFrame(
                    poly_features,
                    columns=self.poly.get_feature_names_out(current_num_cols),
                    index=df.index
                )

                df = pd.concat([df.drop(columns=current_num_cols), poly_df], axis=1)

            # ✅ Add target column back
            if target_series is not None:
                df[target_col] = target_series

            return df
        except Exception as e:
            raise ProjectXecption(e, sys)

    def fit_transform(self, df: pd.DataFrame, target_col: str = None):
        self.fit(df, target_col=target_col)
        return self.transform(df, target_col=target_col)
