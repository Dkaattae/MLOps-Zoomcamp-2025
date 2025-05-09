# week 2 experiment tracking

## 1, install mlflow   
launch codespace in vscode, in terminal   
```
cd 02-experement-tracking   
pip install mlflow   
mlflow --version
```   
it will print out 2.22.0

## 2, download and process data   
in terminal, 
```
wget -P ./taxi_data https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-01.parquet
wget -P ./taxi_data https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-02.parquet
wget -P ./taxi_data https://d37ci6vzurychx.cloudfront.net/trip-data/green_tripdata_2023-03.parquet
```
or run code in homework2.ipynb   
to download data into taxi_data folder.   
```
python preprocess_data.py --raw_data_path ./taxi_data --dest_path ./output
```
to proprocess data   
i have four files inside output folder, which are [dv.pkl, test.pkl, train.pkl, val.pkl]   
inside preprocess_data, we dump the dictVectorizer from training dataset, and transformed training, validation and test data into pickle.  

## 3, train a model  
```
python train.py
```
it will train the model and log params model into mlflow   
min_samples_split = 2

## 4, launch the tracking server
to launch mlflow server, run   
```
mlflow server \
  --backend-store-uri sqlite:///mlflow.db \
  --default-artifact-root ./artifacts
```
host and port are optional. 
default-artifact-root is optional, the default is folder ./mlartifacts.    
if the artifact store is remote, we should use `--artifacts-destination` instead, 
client will send artifacts to server who proxy artifacts, and let server handle the rest.   

## 5, tune model hyperparameters  
run hpo.py   
go to mlflow ui, inside evalutation tab, order experiments by rmse.   
the best rmse is 5.335 

## 6, promote best model   
run register_model.py
go to mlflow ui, there is one model registered, the test rmse is 5.567




