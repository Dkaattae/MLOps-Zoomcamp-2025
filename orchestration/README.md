# week3 orchestration

first install prefect   
`pip install prefect`

`prefect --version`

`prefect server start`

then start mlflow server    
`mlflow ui --backend-store-uri sqlite:///mlflow.db`

run python script   
`python duration_prediction.py --color yellow --year 2023 --month 3`

go to localhost:5000 to see the mlflow ui   
go to the port printed on screen to see prefect ui

after running, make sure to 
`prefect server stop`

