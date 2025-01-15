import pandas as pd
import os
import time
import math
import statistics
from fastapi import APIRouter, status, HTTPException, Depends, FastAPI, File, UploadFile
from fastapi.responses import JSONResponse

from src.utils.process_files import DataLoader, DataPreprocessor, UserInsights
from src.utils.clustering_data import ClusterModel
from src.utils.llm_process import create_marketing_content
from src.config import CONFIG
from src.utils.log_file import logger

file_path = CONFIG["FILE_USER_TRXN_PATH"]

router = APIRouter()

@router.get("/hello")
def hello():
    """
    Endpoint to check if the API is up and running correctly.
    """
    logger.info("Health Check")
    start_time = time.time()
    end_time = time.time()
    return {"status":"hello", "execution_time": str(math.floor(end_time-start_time))+"s"}



@router.get("/get_user_insights")
def get_user_details(client_id:str)->dict:
    """
    Endpoint to get user Insights.

    Args:
        client_id (str): user input

    Returns:
        response (dict): output  
    """

    logger.info(f"execution started for fetching client info : {client_id}")
    try:
        client_id = int(client_id)
        data_loader = DataLoader(file_path)
        users, transactions, mapped = data_loader.read_files()
        preprocessor = DataPreprocessor()
        users, transactions, mapped = preprocessor.preprocess(users, transactions, mapped)
        insights = UserInsights(users, transactions, mapped, client_id)
        output = insights.generate_insights()
        logger.info("client info fetch completed")
    except Exception as err:
        output={}
        logger.error(f"Something went wrong in user info fetch {err}")
    
    """cluster user"""
    try:
        logger.info(f"getting cluser info {client_id}")
        userclustering_model = ClusterModel(mapped)
        output_clusters = userclustering_model.predict_cluster_gmm()
        user_cluster_id = output_clusters["cluster"][output_clusters["client_id"]==client_id].to_list()
        mode_user_cluster_id = statistics.mode(user_cluster_id)
        logger.info(f"user belongs to {mode_user_cluster_id}")
    except Exception as er:
        mode_user_cluster_id = "NA"
        logger.error(f"Something went wrong in getting cluster id {er}")

    user_profile = {
            "client_id": client_id,
            "sum_amount_spent": str(output.get("sum_amount_spent", "NA")),
            "count_amount_spent": str(output.get("count_amount_spent", "NA")),
            "avg_amount_spent": str(output.get("avg_amount_spent", "NA")),
            "mode_spent": output.get("mode_spent", "NA"),
            "mode_count": output.get("mode_count", "NA"),
            "top_n_merchants": output.get("top_5_merchants", "NA"),
            "quarterly_spent": output.get("quarterly_spent","NA"),
            "top_n_trnxn_qtr": output.get("top_3_trnxn_qtr", "NA"),
            "top_n_store_visits": output.get("top_5_store_visits", "NA"),
            "spending_summary": output.get("spending_summary", "NA"),
            "cluster_user": mode_user_cluster_id
        }
    
    """generate custom content as per user profile"""
    try:
        logger.info("starting process for cutomised content for user")
        profile_specific_mkt_content, tagline = create_marketing_content(user_profile)
        logger.info("cutomised content for user generated")
    except Exception as err:
        logger.error(f"Error occured {err}")

    response={
        "response": user_profile, 
        "marketing_advise_email": profile_specific_mkt_content,
        "tag_line": tagline

    }

    return {"Response":response}