import mlflow
import subprocess
from prefect import flow, task


@task(retries=3, retry_delay_seconds=2)
def preprocess_task(raw_data_path, dest_path) -> None:
    '''
    dump four pickle files into output folder 
    dictVectorizer from training, X_train, X_val, X_test
    '''
    subprocess.run([
        "python",
        "experiment_tracking/preprocess_data.py",
        "--raw_data_path", raw_data_path,
        "--dest_path", dest_path
    ], check=True)

@task()
def train_task():
    '''
    load pickles, run model on validation set, autolog in mlflow
    '''
    subprocess.run(["python", "experiment_tracking/train.py"], check=True)

@task()
def hyperopt_task(data_path):
    '''
    start mlflow server, searching best pamameters based on val rmse, logging in mlflow
    '''
    # add data_path to experiment_tracking/output instead of default ./output
    subprocess.run(["python", "experiment_tracking/hpo.py", "--data_path", data_path], check=True)

@task()
def register_task(data_path):
    '''
    find top models from hyperopt, run model on test dataset, logging in mlflow, register the best on test set.
    '''
    subprocess.run(["python", "experiment_tracking/register_model.py", "--data_path", data_path], check=True)

@flow()
def main_flow(raw_data_path, dest_path):
    """The main training pipeline"""

    preprocess_task(raw_data_path, dest_path)
    # train_task()
    hyperopt_task(dest_path)
    register_task(dest_path)



if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--raw_data_path", required=True)
    parser.add_argument("--dest_path", default='./experiment_tracking/output')
    args = parser.parse_args()
    main_flow(args.raw_data_path, args.dest_path)