import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from sklearn.preprocessing import StandardScaler, MinMaxScaler, LabelEncoder, OneHotEncoder
from exception.exception import ProjectXecption
import sys

class Transformation:
    def __init__(self):
        self.num_cols = None
        self.cat_cols = None
        self.scalers = {}   # Store StandardScaler/MinMaxScaler per column
        self.encoders = {}  # Store LabelEncoder or OneHotEncoder per column
        self.fitted = False
        self.target_col = None
        self.target_encoder = None  # For categorical targets

    def fit(self, df: pd.DataFrame, target_col: str = None):
        try:
            cardinality_threshold: int = 10
            self.target_col = target_col

            # ✅ Separate target column if provided
            if self.target_col and self.target_col in df.columns:
                target_series = df[self.target_col]
                df = df.drop(columns=[self.target_col])
            else:
                target_series = None

            self.num_cols = df.select_dtypes(include=[np.number]).columns
            self.cat_cols = df.select_dtypes(include=["object", "category"]).columns

            # ✅ Fit scalers
            for col in self.num_cols:
                skew = df[col].skew()
                scaler = StandardScaler() if abs(skew) < 1 else MinMaxScaler()
                scaler.fit(df[[col]])
                self.scalers[col] = scaler

            # ✅ Fit encoders for features
            for col in self.cat_cols:
                unique_vals = df[col].nunique()
                if unique_vals <= cardinality_threshold:
                    ohe = OneHotEncoder(sparse_output=False, drop='first', handle_unknown="ignore")
                    ohe.fit(df[[col]])
                    self.encoders[col] = ohe
                else:
                    le = LabelEncoder()
                    le.fit(df[col])
                    self.encoders[col] = le

            # ✅ Fit target encoder (only if categorical target)
            if target_series is not None and target_series.dtype == 'object':
                self.target_encoder = LabelEncoder()
                self.target_encoder.fit(target_series)

            self.fitted = True
            print("✅ DataTransformation: Fitted scalers and encoders successfully.")
        except Exception as e:
            raise ProjectXecption(e, sys)

    def transform(self, df: pd.DataFrame, target_col: str = None):
        if not self.fitted:
            raise ProjectXecption("You must call fit() before transform()", sys)

        try:
            target_col = target_col or self.target_col
            df = df.copy()

            # ✅ Separate target column
            target_series = None
            if target_col and target_col in df.columns:
                target_series = df[target_col]
                df = df.drop(columns=[target_col])

            # ✅ Apply scaling
            for col, scaler in self.scalers.items():
                if col in df.columns:
                    df[[col]] = scaler.transform(df[[col]])

            # ✅ Apply encoding for features
            for col, encoder in self.encoders.items():
                if col not in df.columns:
                    continue

                if isinstance(encoder, OneHotEncoder):
                    encoded = pd.DataFrame(
                        encoder.transform(df[[col]]),
                        columns=[f"{col}_{cat}" for cat in encoder.categories_[0][1:]],
                        index=df.index
                    )
                    df = pd.concat([df.drop(columns=[col]), encoded], axis=1)
                else:  # LabelEncoder
                    df[col] = encoder.transform(df[col])

            # ✅ Add back target column (encoded if needed)
            if target_series is not None:
                if self.target_encoder is not None:
                    df[target_col] = self.target_encoder.transform(target_series)
                else:
                    df[target_col] = target_series

            return df
        except Exception as e:
            raise ProjectXecption(e, sys)

    def fit_transform(self, df: pd.DataFrame, target_col: str = None):
        self.fit(df, target_col=target_col)
        return self.transform(df, target_col=target_col)
