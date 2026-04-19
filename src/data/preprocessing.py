import os 
import sys
import pandas as pd 
import numpy as np 
import joblib 
from sklearn.preprocessing import LabelEncoder
from sklearn.utils import resample
from src.logger import logging
from src.exception import MyException

SEED = 42 

class DataPreprocessing:
    @staticmethod
    def clean_cic2017(df: pd.DataFrame) -> pd.DataFrame:
        try:
            """
            - Normalize column names (replace spaces with underscores)
            - Drop unnecessary columns (e.g., IP, Port, Timestamp, etc.)
            - Clean the label column
            - Convert data to numeric format and remove inf/NaN values
            """
            logging.info("Starting CIC2017 data cleaning...")
            dfc = df.copy()

            # Columns name normalize 
            logging.info("Normalizing column names...")
            dfc.columns = [c.strip().replace(" ","_") for c in dfc.columns]
            
            drop_cols = [c for c in [
            "Timestamp", "Flow_ID",
            "Source_IP", "Destination_IP", "Source_Port", "Destination_Port",
            "Src_IP", "Dst_IP", "Src_Port", "Dst_Port"
            ] if c in dfc.columns]
            
            if drop_cols:
                dfc.drop(columns=drop_cols, inplace=True, errors="ignore")
                logging.info(f"Dropped columns: {drop_cols}")

            if "Label" not in dfc.columns:
                logging.error("Label column not found!")
            
            assert "Label" in dfc.columns, "Label column not found!"
            

            # Label basic clean
            logging.info("Cleaning label column...")
            dfc["Label"] = (
                dfc["Label"]
                .astype(str)
                .str.strip()
                .str.lower()
                .replace({"normal": "benign"}))
            
            # numeric conversion
            logging.info("Converting features to numeric...")
            feats = [c for c in dfc.columns if c != "Label"]
            for c in feats:
                dfc[c] = pd.to_numeric(dfc[c], errors="coerce")

            dfc.replace([np.inf, -np.inf], np.nan, inplace=True)
            dfc[feats] = dfc[feats].fillna(0)

            logging.info(f"Data cleaning completed. Shape: {dfc.shape}")
            return dfc
        except Exception as e:
            raise MyException(e,sys)
        
    @staticmethod   
    def normalize_label(s: str) -> str:
        """
        Convert different label variants of the CIC-IDS-2017 dataset
        into 8 standardized classes.
        """
        try:
            original = s

            s = s.lower().strip()

            # Normalize special characters in web attack labels
            s = (s.replace('web attack \u2013', 'web attack -')
                .replace('web attack \u2014', 'web attack -')
                .replace('web attack \ufffd', 'web attack -'))

            # Mapping logic
            if any(k in s for k in ['hulk', 'goldeneye', 'slowloris', 'slowhttptest']):
                label = 'dos'
            elif 'ddos' in s:
                label = 'ddos'
            elif any(k in s for k in ['ftp-patator', 'ssh-patator', 'brute force']):
                label = 'bruteforce'
            elif 'portscan' in s or 'port scan' in s:
                label = 'portscan'
            elif 'web attack' in s or 'xss' in s or 'sql injection' in s:
                label = 'webattack'
            elif 'bot' in s:
                label = 'bot'
            elif 'infiltration' in s:
                label = 'infiltration'
            elif 'benign' in s:
                label = 'benign'
            else:
                label = s  # fallback

            # 🔹 Debug logging (optional but useful)
            if original != label:
                logging.debug(f"Label normalized: '{original}' → '{label}'")

            return label
        except Exception as e:
            logging.error(f"Error in normalize_label for input: {s}")
            raise e
        
    @staticmethod
    def balance_classes(
        df: pd.DataFrame,
        max_per_class: int = 30000,
        min_per_class: int = 5000
    ) -> pd.DataFrame:
        """
        - Undersample large classes to max_per_class
        - Oversample small classes to min_per_class
        """
        try:
            logging.info("Starting class balancing...")

            parts = []

            for label, group in df.groupby("Label"):
                n = len(group)

                if n < min_per_class:
                    group = resample(
                        group,
                        replace=True,
                        n_samples=min_per_class,
                        random_state=SEED
                    )
                    logging.info(f"Oversampled '{label}': {n} → {min_per_class}")

                else:
                    new_n = min(n, max_per_class)
                    group = group.sample(n=new_n, random_state=SEED)
                    logging.info(f"Undersampled '{label}': {n} → {new_n}")

                parts.append(group)

            df_bal = pd.concat(parts).reset_index(drop=True)

            logging.info(f"Balanced dataset shape: {df_bal.shape}")
            logging.info(f"Class distribution:\n{df_bal['Label'].value_counts()}")

            return df_bal

        except Exception as e:
            logging.error("Error during class balancing")
            raise e
        
    @staticmethod
    def encode_labels(
        df: pd.DataFrame,
        art_dir: str = "artifacts"
    ) -> tuple[pd.DataFrame, LabelEncoder, list]:
        """
        Encode label column into numeric values and save the encoder.
        Returns: (df_encoded, label_encoder, classes)
        """
        try:
            logging.info("Starting label encoding...")

            os.makedirs(art_dir, exist_ok=True)

            le = LabelEncoder()
            df = df.copy()

            df["Label"] = le.fit_transform(df["Label"])

            classes = list(le.classes_)
            logging.info(f"Classes encoded: {classes}")

            save_path = os.path.join(art_dir, "label_encoder.pkl")
            joblib.dump(le, save_path)

            logging.info(f"Label encoder saved at: {save_path}")

            return df, le, classes

        except Exception as e:
            logging.error("Error during label encoding")
            raise e