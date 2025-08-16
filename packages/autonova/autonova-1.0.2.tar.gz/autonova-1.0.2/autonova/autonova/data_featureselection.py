import pandas as pd
import numpy as np
from sklearn.feature_selection import VarianceThreshold, mutual_info_classif, mutual_info_regression
from sklearn.decomposition import PCA
# from xgboost import XGBClassifier, XGBRegressor
from exception.exception import ProjectXecption
import sys

class FeatureSelection:
    def __init__(self,):
        """
        target_col: Name of the target column
        problem_type: "classification" or "regression"
        """
        

        # Stores fitted objects
        self.variance_selector = None
        self.correlated_features_to_drop = []
        self.mutual_info_selected = []
        self.xgb_selected = []
        self.pca = None

        # Final selected features (after full pipeline)
        self.selected_features_ = []

    #  Fit the Feature Selection logic
    def fit(self, df: pd.DataFrame, target_col : str, top_k: int = 10, use_pca: bool = False,
            var_threshold: float = 0.01, corr_threshold: float = 0.9):
        try:
            self.target_col = target_col
            df = df.copy()
            X = df.drop(columns=[self.target_col], axis=1)
            y = df[self.target_col]

            # 1. Variance Threshold
            self.variance_selector = VarianceThreshold(threshold=var_threshold)
            self.variance_selector.fit(X)
            X = X[X.columns[self.variance_selector.get_support()]]

            # 2. High Correlation Removal
            corr_matrix = X.corr().abs()
            upper = corr_matrix.where(np.triu(np.ones(corr_matrix.shape), k=1).astype(bool))
            self.correlated_features_to_drop = [col for col in upper.columns if any(upper[col] > corr_threshold)]
            X = X.drop(columns=self.correlated_features_to_drop)

            
            # Automatically detect problem type
            if y.nunique() <= 20 and y.dtype in ["int", "int64", "category"]:
                # Classification → few unique discrete labels
                mi = mutual_info_classif(X, y)
            else:
                # Regression → continuous values
                mi = mutual_info_regression(X, y)

            mi_series = pd.Series(mi, index=X.columns).sort_values(ascending=False)
            self.mutual_info_selected = mi_series.head(top_k).index.tolist()
            X = X[self.mutual_info_selected]

            # 4. PCA (Optional)
            if use_pca:
                self.pca = PCA(n_components=min(top_k, X.shape[1]))
                self.pca.fit(X)
                # PCA replaces selected features entirely
                self.selected_features_ = [f"PCA_{i+1}" for i in range(self.pca.n_components_)]
            else:
                self.selected_features_ = self.mutual_info_selected

            print(" Feature Selection Fitted Successfully!")
        except Exception as e:
            raise ProjectXecption(e, sys)

    #  Transform based on fitted logic
    def transform(self, df: pd.DataFrame):
        try:
            df = df.copy()
            X = df.drop(columns=[self.target_col])
            y = df[self.target_col]

            # Apply Variance Threshold
            if self.variance_selector:
                X = X[X.columns[self.variance_selector.get_support()]]

            # Drop correlated features
            if self.correlated_features_to_drop:
                X = X.drop(columns=[c for c in self.correlated_features_to_drop if c in X.columns], errors="ignore")

            # Select only mutual_info-selected features
            if self.mutual_info_selected and not self.pca:
                X = X[[c for c in self.mutual_info_selected if c in X.columns]]

            # PCA Transform
            if self.pca:
                X = pd.DataFrame(
                    self.pca.transform(X),
                    columns=[f"PCA_{i+1}" for i in range(self.pca.n_components_)],
                    index=df.index
                )

            X[self.target_col] = y
            return X
        except Exception as e:
            raise ProjectXecption(e, sys)

    #  Fit + Transform in one go
    def fit_transform(self, df: pd.DataFrame,target_col:str , top_k: int = 10, use_pca: bool = False,
                      var_threshold: float = 0.01, corr_threshold: float = 0.9):
        self.target_col = target_col
        self.fit(df=df,target_col=target_col, top_k=top_k, use_pca=use_pca, var_threshold=var_threshold, corr_threshold=corr_threshold)

        return self.transform(df)
