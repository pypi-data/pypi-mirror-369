
class MetaLearn:
    def __init__(self):
        return None

    def task_type_check(self, df, target):
        """Detect whether it's a classification or regression problem."""
        if df[target].dtype in ["object", "category"] or df[target].nunique() <= 10:
            return "classification"
        return "regression"


    def extract_meta_features(self, df, target):
        """Extract meta-features for meta-learning."""
        n_rows, n_cols = df.shape
        num_cols = df.select_dtypes(include=["int64", "float64"]).columns
        cat_cols = df.select_dtypes(include=["object", "category", "bool"]).columns
        missing_ratio = df.isna().sum().sum() / (n_rows * n_cols)

        imbalance = 0.5
        if df[target].dtype in ["object", "category"] or df[target].nunique() <= 10:
            imbalance = df[target].value_counts(normalize=True).min()

        return {
            "n_rows": n_rows,
            "n_cols": n_cols,
            "num_ratio": len(num_cols) / n_cols,
            "cat_ratio": len(cat_cols) / n_cols,
            "missing_ratio": missing_ratio,
            "imbalance": imbalance,
        }


    def suggest_top_models(self, df, target, top_n=3):
        meta = self.extract_meta_features(df, target)
        problem_type = self.task_type_check(df, target)

        if problem_type == "classification":
            models = [
                "LogisticRegression", "RandomForest", "XGBoost", "LightGBM",
                "CatBoost", "SVC", "KNN", "GradientBoosting", "NaiveBayes"
            ]
        else:
            models = [
                "LinearRegression", "Ridge", "Lasso", "RandomForestRegressor",
                "XGBRegressor", "LGBMRegressor", "CatBoostRegressor", "SVR", "KNeighborsRegressor"
            ]

        # Initialize scores
        scores = {m: 0 for m in models}

        # --- Heuristic scoring ---
        for m in models:
            # Large dataset → tree/boosting models
            if meta["n_rows"] > 100_000 and any(x in m for x in ["XGB", "LGBM", "CatBoost", "RandomForest"]):
                scores[m] += 3
            elif meta["n_rows"] > 10_000 and any(x in m for x in ["XGB", "LGBM", "CatBoost", "RandomForest", "GradientBoosting"]):
                scores[m] += 2

            # High categorical ratio → CatBoost/NaiveBayes
            if meta["cat_ratio"] > 0.5 and any(x in m for x in ["CatBoost", "NaiveBayes", "RandomForest"]):
                scores[m] += 2

            # Mostly numeric → linear/SVR
            if meta["num_ratio"] > 0.7 and any(x in m for x in ["Linear", "Ridge", "Lasso", "SVR"]):
                scores[m] += 2

            # Imbalanced classification
            if problem_type == "classification" and meta["imbalance"] < 0.3 and any(x in m for x in ["XGB", "LGBM", "CatBoost", "LogisticRegression"]):
                scores[m] += 2

            # Missing values tolerance
            if meta["missing_ratio"] > 0.1 and any(x in m for x in ["CatBoost", "XGB", "RandomForest"]):
                scores[m] += 1

        # Sort by score and return top N
        sorted_models = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        best_models = [m for m, s in sorted_models if s > 0][:top_n]
        return best_models, problem_type, meta
