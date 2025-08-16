import pickle
from exception.exception import ProjectXecption

# ✅ Save the entire fitted pipeline
class utils:
    def __init__(self):
        return None

    def save(self, file_path: str):
        try:
            with open(file_path, "wb") as f:
                pickle.dump(self, f)
            print(f"✅ Pipeline saved successfully to: {file_path}")
        except Exception as e:
            raise ProjectXecption(e, sys)

    # ✅ Load a saved pipeline
    @staticmethod
    def load(file_path: str):
        try:
            with open(file_path, "rb") as f:
                pipeline = pickle.load(f)
            print(f" Pipeline loaded successfully from: {file_path}")
            return pipeline
        except Exception as e:
            raise ProjectXecption(e, sys)
