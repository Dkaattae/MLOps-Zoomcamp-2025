from experiment_tracking import preprocess_data
from experiment_tracking import train
from experiment_tracking import hpo
from experiment_tracking import register_model
import mlflow
from prefect import flow, task


@task(retries=3, retry_delay_seconds=2)
def preprocess_task() -> None:
    '''
    dump four pickle files into output folder 
    dictVectorizer from training, X_train, X_val, X_test
    '''
    preprocess_data.run_data_prep()

@task()
def train_task():
    '''
    load pickles, run model on validation set, autolog in mlflow
    '''
    run_train()

@task()
def hyperopt_task():
    '''
    start mlflow server, searching best pamameters based on val rmse, logging in mlflow
    '''
    run_optimization()

@task()
def register_task():
    '''
    find top models from hyperopt, run model on test dataset, logging in mlflow, register the best on test set.
    '''
    run_register_model()

@flow()
def main_flow():
    """The main training pipeline"""

    # MLflow settings
    mlflow.set_tracking_uri("sqlite:///mlflow.db")
    mlflow.set_experiment("nyc-taxi-experiment")

    preprocess_task()
    # train_task()
    hyperopt_task()
    register_task()



if __name__ == "__main__":
    main_flow()