import os
import sys
import numpy as np
import pandas as pd
import joblib
from src.logger import logging
from src.exception import MyException

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import RobustScaler
from sklearn.utils.class_weight import compute_class_weight
from tensorflow.keras.utils import to_categorical

SEED = 42

class FeatureEngineering:
    @staticmethod
    def split_data(df, test_size=0.2):
        """
        Split dataset into train and test sets
        Returns: X_train, X_test, y_train, y_test
        """
        try:
            logging.info("Starting train-test split...")

            if "Label" not in df.columns:
                logging.error("Label column not found!")
                raise MyException("Label column not found!", sys)

            X = df.drop(columns=["Label"])
            y = df["Label"].astype(int)

            X_train, X_test, y_train, y_test = train_test_split(
                X, y,
                test_size=test_size,
                stratify=y,
                random_state=42
            )

            logging.info(f"Split completed")
            logging.info(f"X_train: {X_train.shape}, X_test: {X_test.shape}")

            return X_train, X_test, y_train, y_test

        except Exception as e:
            logging.error("Error during train-test split")
            raise MyException(e, sys)
        
    @staticmethod
    def scale_features(X_train, X_test, art_dir="artifacts"):
        """
        Scale features using RobustScaler
        Returns: X_train_scaled, X_test_scaled
        """
        try:
            logging.info("Starting feature scaling...")

            os.makedirs(art_dir, exist_ok=True)

            scaler = RobustScaler(quantile_range=(5, 95))

            X_train_scaled = scaler.fit_transform(X_train)
            X_test_scaled = scaler.transform(X_test)

            save_path = os.path.join(art_dir, "scaler.pkl")
            joblib.dump(scaler, save_path)

            logging.info(f"Scaling completed. Scaler saved at: {save_path}")

            return X_train_scaled, X_test_scaled

        except Exception as e:
            logging.error("Error during feature scaling")
            raise MyException(e, sys)
        
    @staticmethod
    def make_cnn_shape(X_train_scaled, X_test_scaled):
        """
        Convert 2D arrays into 3D for CNN input
        (samples, features) → (samples, features, 1)
        """
        try:
            logging.info("Converting data to CNN shape...")

            X_train_cnn = X_train_scaled[..., np.newaxis]
            X_test_cnn  = X_test_scaled[..., np.newaxis]

            logging.info(f"CNN Train shape: {X_train_cnn.shape}")
            logging.info(f"CNN Test shape: {X_test_cnn.shape}")

            return X_train_cnn, X_test_cnn

        except Exception as e:
            logging.error("Error in CNN reshaping")
            raise MyException(e, sys)
        
    @staticmethod
    def one_hot_labels(y_train, y_test, num_classes):
        """
        Convert labels to one-hot encoding for CNN
        """
        try:
            logging.info("Applying one-hot encoding...")

            y_train_oh = to_categorical(y_train, num_classes)
            y_test_oh  = to_categorical(y_test, num_classes)

            logging.info(f"y_train shape: {y_train_oh.shape}")
            logging.info(f"y_test shape: {y_test_oh.shape}")

            return y_train_oh, y_test_oh

        except Exception as e:
            logging.error("Error in one-hot encoding")
            raise MyException(e, sys)
        
    @staticmethod
    def get_class_weights(y_train):
        """
        Compute class weights for imbalanced dataset
        """
        try:
            logging.info("Calculating class weights...")

            classes = np.unique(y_train)

            cw_values = compute_class_weight(
                class_weight="balanced",
                classes=classes,
                y=y_train
            )

            class_weight = {int(c): float(w) for c, w in zip(classes, cw_values)}

            logging.info(f"Class weights: {class_weight}")

            return class_weight

        except Exception as e:
            logging.error("Error in computing class weights")
            raise MyException(e, sys)
        
    @staticmethod
    def save_prepared_data(
        X_train_ml, X_test_ml,
        y_train_idx, y_test_idx,
        X_train_cnn, X_test_cnn,
        y_train_cnn, y_test_cnn,
        art_dir="artifacts"
    ):
        """
        Save all prepared datasets into a compressed file
        """
        try:
            logging.info("Saving prepared datasets...")

            os.makedirs(art_dir, exist_ok=True)

            path = os.path.join(art_dir, "prepared_train_test.npz")

            np.savez_compressed(
                path,
                X_train_ml=X_train_ml,
                X_test_ml=X_test_ml,
                y_train_idx=y_train_idx,
                y_test_idx=y_test_idx,
                X_train_cnn=X_train_cnn,
                X_test_cnn=X_test_cnn,
                y_train_cnn=y_train_cnn,
                y_test_cnn=y_test_cnn,
            )

            logging.info(f"Data saved at: {path}")

        except Exception as e:
            logging.error("Error saving prepared data")
            raise MyException(e, sys)