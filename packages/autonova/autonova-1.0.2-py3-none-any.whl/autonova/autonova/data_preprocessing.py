import pandas as pd
import numpy as np
from sklearn.impute import KNNImputer
from exception.exception import ProjectXecption
import sys

class Preprocess:
    def __init__(self, n_neighbors=10, knn_thres=1000, z_thresh=3,
                 rare_threshold=0.03, small_data_thres=30, drop_duplicates=False):
        self.n_neighbors = n_neighbors
        self.knn_thres = knn_thres
        self.z_thresh = z_thresh
        self.rare_threshold = rare_threshold
        self.small_data_thres = small_data_thres
        self.drop_duplicates = drop_duplicates

        self.num_imputer = None
        self.num_fill_values = {}
        self.cat_fill_values = {}
        self.outlier_bounds = {}
        self.rare_categories = {}

        self.target_col = None

    def fit(self, df: pd.DataFrame, target_col: str = None):
        try:
            df = df.copy()
            self.target_col = target_col

            # ✅ Separate target column
            if self.target_col and self.target_col in df.columns:
                df = df.drop(columns=[self.target_col])

            num_cols = df.select_dtypes(include=[np.number]).columns
            cat_cols = df.select_dtypes(include=["object", "category"]).columns

            # --- Imputation ---
            if df.shape[0] >= self.knn_thres:
                self.num_imputer = KNNImputer(n_neighbors=self.n_neighbors)
                self.num_imputer.fit(df[num_cols])
                self.cat_fill_values = {c: df[c].mode()[0] for c in cat_cols if df[c].notna().any()}
            else:
                for col in num_cols:
                    if df[col].isna().any():
                        self.num_fill_values[col] = (
                            df[col].median() if abs(df[col].skew()) > 1 else df[col].mean()
                        )
                for col in cat_cols:
                    if df[col].isna().any():
                        self.cat_fill_values[col] = df[col].mode()[0]

            # --- Outliers ---
            if df.shape[0] >= self.small_data_thres:
                for col in num_cols:
                    if df[col].notna().any():
                        if abs(df[col].skew()) < 1:
                            mean, std = df[col].mean(), df[col].std()
                            self.outlier_bounds[col] = (mean - self.z_thresh * std, mean + self.z_thresh * std)
                        else:
                            Q1, Q3 = df[col].quantile([0.25, 0.75])
                            IQR = Q3 - Q1
                            self.outlier_bounds[col] = (Q1 - 1.5 * IQR, Q3 + 1.5 * IQR)

            # --- Rare Categories ---
            for col in cat_cols:
                freqs = df[col].value_counts(normalize=True)
                self.rare_categories[col] = freqs[freqs < self.rare_threshold].index.tolist()

            print("✅ Preprocessor fitted successfully!")
        except Exception as e:
            raise ProjectXecption(e, sys)

    def transform(self, df: pd.DataFrame, target_col: str = None):
        try:
            df = df.copy()
            target_col = target_col or self.target_col

            # ✅ Separate target column
            target_series = None
            if target_col and target_col in df.columns:
                target_series = df[target_col]
                df = df.drop(columns=[target_col])

            num_cols = df.select_dtypes(include=[np.number]).columns
            cat_cols = df.select_dtypes(include=["object", "category"]).columns

            # --- Imputation ---
            if self.num_imputer:
                df[num_cols] = self.num_imputer.transform(df[num_cols])
            else:
                for col, val in self.num_fill_values.items():
                    if col in df.columns:
                        df[col].fillna(val, inplace=True)
                for col, val in self.cat_fill_values.items():
                    if col in df.columns:
                        df[col].fillna(val, inplace=True)

            # --- Outliers ---
            for col, (low, high) in self.outlier_bounds.items():
                if col in df.columns:
                    df[col] = np.clip(df[col], low, high)

            # --- Rare Categories ---
            for col, rare_list in self.rare_categories.items():
                if col in df.columns:
                    df[col] = df[col].apply(lambda x: "Other" if x in rare_list else x)

            # --- Safer Date Conversion ---
            for col in cat_cols:
                try:
                    parsed = pd.to_datetime(df[col], errors="coerce")
                    if parsed.notna().sum() > 0:
                        df[col] = parsed.fillna(parsed.mode()[0])
                except:
                    pass

            # --- Convert low-cardinality objects to categories ---
            for col in df.select_dtypes(include=["object"]).columns:
                if df[col].nunique() / len(df[col]) < 0.5:
                    df[col] = df[col].astype("category")

            # --- Duplicates (optional) ---
            if self.drop_duplicates:
                before = df.shape[0]
                df = df.drop_duplicates().reset_index(drop=True)
                print(f"[INFO] Duplicates removed: {before - df.shape[0]}")

            # ✅ Add back target column
            if target_series is not None:
                df[target_col] = target_series

            return df
        except Exception as e:
            raise ProjectXecption(e, sys)

    def fit_transform(self, df: pd.DataFrame, target_col: str = None):
        self.fit(df, target_col=target_col)
        return self.transform(df, target_col=target_col)
