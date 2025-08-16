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

from projectX.auto import autonova


df = pd.read_csv(r"C:\Users\sanjay\Desktop\Project-X\star_classification.csv")
target_col = "class"


mode = autonova(data=df, target_col=target_col)
mode.go(use_gpu=False, fast_mode=False, cv_splits=5, n_trials=50)

print("Best Model:", mode.best_model)
print("Preprocessing Steps:", mode.preprocess_logic)
print("Score:", mode.score)
print("Train Data Shapes:", [x.shape for x in mode.train_data])
print("Test Data Shapes:", [x.shape for x in mode.test_data])





