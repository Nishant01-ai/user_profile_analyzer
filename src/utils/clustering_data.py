 # GMM
import pandas as pd
import os
from fastapi import APIRouter, status, HTTPException, Depends, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse
import pickle
from sklearn.mixture import GaussianMixture
from kmodes.kmodes import KModes

from src.utils.process_files import DataLoader, DataPreprocessor
from src.config import CONFIG



file_path = CONFIG["FILE_USER_TRXN_PATH"]
model_file_path = CONFIG["MODEL_PATH"]

data_loader = DataLoader(file_path)
users, transactions, mapped = data_loader.read_files()
preprocessor = DataPreprocessor()
users, transactions, mapped = preprocessor.preprocess(users, transactions, mapped)

    
class ClusterModel:
    def __init__(self, mapped):
        self.mapped_file = mapped
        
    def train_cluster_gmm(self):
        input_data=self.mapped_file[['current_age', 'yearly_income', 'total_debt', 'amount']]
        # Create and train the GMM model
        gmm = GaussianMixture(n_components=3, random_state=8)
        gmm.fit(input_data)  # Assume X is your training data
        # Save the GMM model to a file using pickle
        with open(model_file_path, 'wb') as f:
            pickle.dump(gmm, f)
        return {"status":"Sucess"}
    
    
    def predict_cluster_gmm(self):
        # Load the GMM model from the file
        with open(model_file_path, 'rb') as f:
            gmm_loaded = pickle.load(f)

        X_test = self.mapped_file[['current_age', 'yearly_income', 'total_debt', 'amount']]
        # Use the loaded model to predict new data
        predictions = gmm_loaded.predict(X_test)
        self.mapped_file['cluster'] = predictions
        # print("CLUSTER_DATA : ", self.mapped_file)
        return self.mapped_file


    # def predict_cluster_kmode(self):
    #     # Assuming 'df' is your DataFrame
    #     categorical_columns = ['gender', 'use_chip', 'merchant_category', 'amount']
    #     self.mapped_file[categorical_columns] = self.mapped_file[categorical_columns].astype(str)

    #     # Convert DataFrame to numpy array
    #     test_X = self.mapped_file.to_numpy()

    #     # Apply K-Prototypes
    #     kproto = KModes(n_clusters=4, random_state=42)
    #     clusters = kproto.fit_predict(X, categorical=[sample_data_cluster.columns.get_loc(col) for col in categorical_columns])

    #     sample_data_cluster['Cluster'] = clusters

        
    
