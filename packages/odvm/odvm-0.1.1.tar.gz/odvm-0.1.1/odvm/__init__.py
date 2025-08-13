"""
ODVM - Open, Dynamic, and Versatile Modeling AutoML System
=========================================================

ODVM is a powerful and flexible Python package for automated data analysis, 
preprocessing, modeling, and reporting. Designed to handle both small-scale 
(Pandas) and large-scale (Dask) datasets, ODVM simplifies the entire 
machine learning workflow — from raw data to deployable models.

Key Features
------------
1. **Automated Data Profiling & EDA**  
   - Summarizes datasets with descriptive statistics, correlations, and distributions.
   - Detects missing values, outliers, and duplicate records automatically.

2. **Smart Preprocessing**  
   - Handles missing data, categorical encoding, scaling, and outlier removal.
   - Automatically adapts methods based on task type (classification, regression, clustering, etc.).

3. **Dynamic Task Detection**  
   - Identifies task type (e.g., binary classification, regression, time series).
   - Determines learning mode (supervised vs unsupervised).

4. **Model Selection & Training**  
   - Automatically selects suitable models for the detected task type.
   - Supports multiple algorithms: XGBoost, LightGBM, CatBoost, Scikit-learn models.
   - Hyperparameter tuning and cross-validation included.

5. **Performance Evaluation & Reporting**  
   - Generates evaluation metrics in tables and visual charts.
   - Creates HTML/PDF reports summarizing workflow results.

6. **Extensible & Modular Design**  
   - Well-structured architecture for easy customization.
   - Supports future plugins, deployment, and monitoring modules (In future).

Planned Extensions
------------------
- Support for anomaly detection.
- Integrated deployment pipelines with FastAPI.
- Real-time monitoring of deployed models.
"""
__version__ = "0.1.1"

from .assistant.task_detector import TaskDetector

from .utils.detect_backend import detect_backend

from .core.runner import ODVM

from .eda.analyzer import EDAAnalyzer
from .eda.visualizer import EDAVisualizer

from .modeling.evaluator import ModelEvaluator
from .modeling.model_selector import ModelSelector
from .modeling.trainer import ModelTrainer
from .modeling.tuner import ModelTuner
from .modeling.explainer import ModelExplainer

from .preprocess.cleaner import DataCleaner
from .preprocess.encoder import Encoder
from .preprocess.scaler import Scaler
from .preprocess.splitter import DataSplitter


from .reporting.report_builder import ReportBuilder



