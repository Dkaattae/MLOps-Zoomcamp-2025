import pickle
import pandas as pd
import argparse


def read_data(filename, categorical):
    df = pd.read_parquet(filename)

    df['duration'] = df.tpep_dropoff_datetime - df.tpep_pickup_datetime
    df['duration'] = df.duration.dt.total_seconds() / 60

    df = df[(df.duration >= 1) & (df.duration <= 60)].copy()

    df[categorical] = df[categorical].fillna(-1).astype('int').astype('str')
    print(f'reading data from {filename}...')
    return df


def predict_data(df, categorical, dv, model):
    dicts = df[categorical].to_dict(orient='records')
    X_val = dv.transform(dicts)
    y_pred = model.predict(X_val)
    print('prediction standard deviation is: ', y_pred.std())
    return y_pred

# y_pred.std()

def save_results(df, year, month, y_pred, output_file):
    df['ride_id'] = f'{year:04d}/{month:02d}_' + df.index.astype('str')
    df_result = pd.DataFrame()
    df_result['ride_id'] = df['ride_id']
    df_result['predicted_duration'] = y_pred
    print(f'saving results to {output_file}')
    df_result.to_parquet(
        output_file,
        engine='pyarrow',
        compression=None,
        index=False
    )


# get_ipython().system('mkdir -p ./output/yellow')


def run(year, month):
    categorical = ['PULocationID', 'DOLocationID']
    with open('model.bin', 'rb') as f_in:
        dv, model = pickle.load(f_in)
    df = read_data(f'https://d37ci6vzurychx.cloudfront.net/trip-data/yellow_tripdata_{year:04d}-{month:02d}.parquet', categorical)
    output_file = f'output/yellow/{year:04d}-{month:02d}.parquet'
    y_pred = predict_data(df, categorical, dv, model)
    print('mean of y predicted is: ', y_pred.mean())
    save_results(df, year, month, y_pred, output_file)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--year', required=True, help='year')
    parser.add_argument('--month', required=True, help='month')
    args = parser.parse_args()
    year = int(args.year)
    month = int(args.month)
    run(year, month)





