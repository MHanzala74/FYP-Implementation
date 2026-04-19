import os
import sys 
import numpy as np
import pandas as pd
import joblib
from src.logger import logging
from src.exception import MyException

from sklearn.feature_selection import VarianceThreshold, SelectKBest, f_classif

class FeatureSelection:
    @staticmethod
    def show_selected_features(selector, feature_names):
        """
        Show selected and removed features after VarianceThreshold
        """
        try:
            logging.info("Displaying selected features...")

            mask = selector.get_support()

            selected = [f for f, s in zip(feature_names, mask) if s]
            removed  = [f for f, s in zip(feature_names, mask) if not s]

            logging.info(f"Selected Features ({len(selected)}): {selected[:10]}...")
            logging.info(f"Removed Features ({len(removed)}): {removed[:10]}...")

            return selected

        except Exception as e:
            logging.error("Error in feature display")
            raise MyException(e, sys)