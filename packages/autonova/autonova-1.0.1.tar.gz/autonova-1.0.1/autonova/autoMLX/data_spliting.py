import pandas as pd
from sklearn.model_selection import train_test_split
from exception.exception import ProjectXecption
import sys

class Spliting:
    def __init__(self, test_size: float = 0.2, random_state: int = 42):
        self.test_size = test_size
        self.random_state = random_state
        self.X_train, self.X_test, self.y_train, self.y_test = None, None, None, None

    def detect_problem_type(self, y: pd.Series):
        """Detect classification vs regression."""
        if pd.api.types.is_numeric_dtype(y):
            return "regression" if y.nunique() > 20 else "classification"
        return "classification"

    def fit(self, df: pd.DataFrame, target_col: str):
        try:
            X = df.drop(columns=[target_col])
            y = df[target_col]
            problem_type = self.detect_problem_type(y)

            if problem_type == "classification":
                # Check if stratification is possible
                if y.value_counts().min() >= 2:
                    print("✅ Classification problem detected → Using stratified split.")
                    self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                        X, y, test_size=self.test_size, stratify=y, random_state=self.random_state
                    )
                else:
                    print("⚠️ Too few samples in some classes → Falling back to normal split.")
                    self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                        X, y, test_size=self.test_size, random_state=self.random_state
                    )
            else:
                print("✅ Regression problem detected → Using normal split.")
                self.X_train, self.X_test, self.y_train, self.y_test = train_test_split(
                    X, y, test_size=self.test_size, random_state=self.random_state
                )

            print(f"✅ Data Split: Train → {self.X_train.shape[0]} rows, Test → {self.X_test.shape[0]} rows")
            return self

        except Exception as e:
            raise ProjectXecption(e, sys)

    def transform(self, df: pd.DataFrame):
        """Splitting is only done during training."""
        return df

    def fit_transform(self, df: pd.DataFrame, target_col: str):
        self.fit(df, target_col)
        return self.X_train, self.X_test, self.y_train, self.y_test
