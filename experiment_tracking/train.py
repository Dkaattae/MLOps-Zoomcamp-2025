import os
import pickle
import click

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error

import mlflow
from mlflow.models.signature import infer_signature


mlflow.set_tracking_uri("http://127.0.0.1:5000")
mlflow.set_experiment("nyc-taxi-experiment")


def load_pickle(filename: str):
    with open(filename, "rb") as f_in:
        return pickle.load(f_in)


@click.command()
@click.option(
    "--data_path",
    default="./output",
    help="Location where the processed NYC taxi trip data was saved"
)
def run_train(data_path: str):

    X_train, y_train = load_pickle(os.path.join(data_path, "train.pkl"))
    X_val, y_val = load_pickle(os.path.join(data_path, "val.pkl"))

    with mlflow.start_run():

        mlflow.set_tag("developer", "KateChen")

        mlflow.log_param("train-data-path", "./taxi_data/green_tripdata_2023-01.parquet")
        mlflow.log_param("valid-data-path", "./taxi_data/green_tripdata_2023-02.parquet")

        max_depth = 10
        random_state = 0

        mlflow.log_param("max_depth", max_depth)
        mlflow.log_param("random_state", random_state)
        rf = RandomForestRegressor(max_depth=max_depth, random_state=random_state)
        rf.fit(X_train, y_train)
        y_pred = rf.predict(X_val)

        rmse = (mean_squared_error(y_val, y_pred)) ** 0.5
        mlflow.log_metric("rmse", rmse)

        mlflow.log_artifact(local_path=os.path.join(data_path, "train.pkl"), artifact_path="models_pickle")

        input_example = X_train[:5].toarray()  
        signature = infer_signature(X_train.toarray(), rf.predict(X_train))
        mlflow.sklearn.log_model(rf, artifact_path="models_pickle", input_example=input_example, signature=signature)

        print('min_samples_split: ', rf.min_samples_split)

if __name__ == '__main__':
    run_train()
