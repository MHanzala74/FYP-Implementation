from src.logger import logging

# logging.debug("This is a debug message")
# logging.info("This is a info message")
# logging.warning("This is a warning message")
# logging.error("This is a error message")
# logging.critical("This is a critical message")


# from src.logger import logging
# from src.exception import MyException
# import sys

# try:
#     a = 1+'Z'
# except Exception as e:
#     logging.info(e)
#     raise MyException(e, sys) from e


# from src.data.ingestion import run_ingestion
# df = run_ingestion("src/data/mydata.csv")
# print(df.head())

# from src.data.ingestion import DataIngestion
# from src.data.preprocessing import DataPreprocessing

# def main():

#     # Step 1: Load Data
    
#     df = DataIngestion.load_data(filepath="notebooks/mydata.csv")
#     DataIngestion.show_info(df)
#     # Step 2: Cleaning
    
#     df = DataPreprocessing.clean_cic2017(df)

#     # Step 3: Normalize Labels
#     df["Label"] = df["Label"].apply(DataPreprocessing.normalize_label)

#     # Step 4: Balance Classes
#     df = DataPreprocessing.balance_classes(df)

#     # Step 5: Encode Labels
#     df, le, classes = DataPreprocessing.encode_labels(df)

#     print("Pipeline Completed Successfully")
#     print(df.head())


# if __name__ == "__main__":
#     main()






from src.data.ingestion import DataIngestion
from src.data.preprocessing import DataPreprocessing
from src.features.feature_engineering import FeatureEngineering

def main():

    # 1. Load Data
    df = DataIngestion.load_data("notebooks/mydata.csv")

    # 2. Clean Data
    df = DataPreprocessing.clean_cic2017(df)

    # 3. Normalize Labels
    df["Label"] = df["Label"].apply(DataPreprocessing.normalize_label)

    # 4. Encode Labels
    df, le, classes = DataPreprocessing.encode_labels(df)

    # ==============================
    # FEATURE ENGINEERING START
    # ==============================

    # 5. Split
    X_train, X_test, y_train, y_test = FeatureEngineering.split_data(df)

    # 6. Scale
    X_train_scaled, X_test_scaled = FeatureEngineering.scale_features(X_train, X_test)

    # 7. CNN Shape
    X_train_cnn, X_test_cnn = FeatureEngineering.make_cnn_shape(X_train_scaled, X_test_scaled)

    # 8. One Hot
    y_train_oh, y_test_oh = FeatureEngineering.one_hot_labels(
        y_train, y_test, num_classes=len(classes)
    )

    # 9. Class Weights
    class_weights = FeatureEngineering.get_class_weights(y_train)

    # 10. Save Everything
    FeatureEngineering.save_prepared_data(
        X_train_scaled, X_test_scaled,
        y_train, y_test,
        X_train_cnn, X_test_cnn,
        y_train_oh, y_test_oh
    )

    print("✅ FULL PIPELINE COMPLETED SUCCESSFULLY")

if __name__ == "__main__":
    main()




