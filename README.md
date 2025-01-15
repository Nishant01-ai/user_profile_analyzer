Setup Instructions
1.	Update OpenAI API Key:
    o	Modify the config.yaml file with your OpenAI API key.
2.  Put the users and transaction excel files in src/data folder (create "data" folder inside src).
3.	Install Dependencies:
4.	pip install -r requirements.txt
5.	Run the Application:
6.	uvicorn main:app --reload
7.	Access the API Documentation:
    Open your browser and visit: http://127.0.0.1:8000/cba/api/docs#/
8. Get into /cba/ml/get_user_insights endpoint
9. Enter client_id and run Execute 

