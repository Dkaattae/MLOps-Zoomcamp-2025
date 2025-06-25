
import pandas as pd
from datetime import datetime
import pandas.testing as pdt

import batch

def dt(hour, minute, second=0):
    return datetime(2023, 1, 1, hour, minute, second)

data = [
    (None, None, dt(1, 1), dt(1, 10)),
    (1, 1, dt(1, 2), dt(1, 10)),
    (1, None, dt(1, 2, 0), dt(1, 2, 59)),
    (3, 4, dt(1, 2, 0), dt(2, 2, 1)),      
]

columns = ['PULocationID', 'DOLocationID', 'tpep_pickup_datetime', 'tpep_dropoff_datetime']
df = pd.DataFrame(data, columns=columns)

categorical = ['PULocationID', 'DOLocationID']
actual_result = batch.prepare_data(df, categorical)
expected_result = pd.DataFrame([
    ('-1', '-1', dt(1,1), dt(1,10), 9.0),
    ('1', '1', dt(1, 2), dt(1, 10), 8.0),
], columns=columns+['duration'])

pdt.assert_frame_equal(actual_result, expected_result, atol=0.01)



