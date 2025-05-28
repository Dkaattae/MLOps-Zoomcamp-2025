import pandas as pd
import numpy as np
import pickle
import yaml
import os
import mlflow
from prefect import flow, task
from sklearn.feature_extraction import DictVectorizer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import root_mean_squared_error
import sklearn
import scipy

@task(retries=3, retry_delay_seconds=2)
def read_dataframe(color: str, year: int, month: int) -> pd.DataFrame:
    url = f'https://d37ci6vzurychx.cloudfront.net/trip-data/{color}_tripdata_{year}-{month:02d}.parquet'
    df = pd.read_parquet(url)
    print('download raw data file, record count: ', len(df))
    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df.duration = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)]

    categorical = ['PULocationID', 'DOLocationID']
    df[categorical] = df[categorical].astype(str)
    print('prepare dataframe, record count: ', len(df))
    return df

@task()
def create_X(
    df: pd.DataFrame, 
    categorical: list, 
    numerical: list, 
    dv: sklearn.feature_extraction.DictVectorizer = None) -> tuple(
        [
            scipy.sparse._csr.csr_matrix, 
            sklearn.feature_extraction.DictVectorizer
        ]):
    dicts = df[categorical + numerical].to_dict(orient='records')

    if dv is None:
        dv = DictVectorizer(sparse=True)
        X = dv.fit_transform(dicts)
    else:
        X = dv.transform(dicts)

    return X, dv

@task()
def training_linear_regression(
    X_train: scipy.sparse._csr.csr_matrix, 
    y_train: np.ndarray, 
    X_val: scipy.sparse._csr.csr_matrix, 
    y_val: np.ndarray, 
    dv: sklearn.feature_extraction.DictVectorizer
    ) -> str:
    with mlflow.start_run() as run:
        run_id = run.info.run_id
        lr = LinearRegression()
        lr.fit(X_train, y_train)
        print("linear regression intercept: ", lr.intercept_)
        mlflow.log_param("fit_intercept", lr.intercept_)
        y_pred = lr.predict(X_val)
        rmse = root_mean_squared_error(y_val, y_pred)
        mlflow.log_metric("val_rmse", rmse)
        mlflow.sklearn.log_model(lr, "model")
    return run_id

@task()
def register_model(run_id, EXPERIMENT_NAME):
    model_uri = f'runs:/{run_id}/model'
    mlflow.register_model(model_uri=model_uri, name=EXPERIMENT_NAME)
    
    local_path = mlflow.artifacts.download_artifacts(run_id=run_id, artifact_path="model/MLmodel")
    with open(local_path, "r") as f:
        mlmodel_data = yaml.safe_load(f)
    model_size_bytes = mlmodel_data.get("model_size_bytes")
    print(model_size_bytes)
    return model_size_bytes

@flow()
def run(color: str, year: int, month: int) -> None:
    # mlflow setting
    EXPERIMENT_NAME = "nyc-taxi-experiment"
    mlflow.set_tracking_uri("http://localhost:5000")
    mlflow.set_experiment(EXPERIMENT_NAME)

    # load data
    df_train = read_dataframe(color, year, month)

    next_year = year if month < 12 else year + 1
    next_month = month + 1 if month < 12 else 1
    df_val = read_dataframe(color=color, year=next_year, month=next_month)

    # transform
    X_train, dv = create_X(df=df_train, categorical=['PULocationID', 'DOLocationID'], numerical=[])
    X_val, _ = create_X(df=df_val, categorical=['PULocationID', 'DOLocationID'], numerical=[], dv=dv)

    target = 'duration'
    y_train = df_train[target].values
    y_val = df_val[target].values

    # train
    run_id = training_linear_regression(X_train, y_train, X_val, y_val, dv)

    # register
    model_size = register_model(run_id, EXPERIMENT_NAME)

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--color", type=str, required=True, choices=["yellow", "green"],
        help="Choose one of the predefined colors")
    parser.add_argument("--year", type=int, required=True)
    parser.add_argument("--month", type=int, required=True)
    args = parser.parse_args()
    run(args.color, args.year, args.month)