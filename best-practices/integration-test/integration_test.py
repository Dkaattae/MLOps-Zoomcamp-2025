import os
import pandas as pd
import pandas.testing as pdt

S3_ENDPOINT_URL = "http://localhost:4566"

# os.system("python ../batch.py")
options = {
    'client_kwargs': {
        'endpoint_url': S3_ENDPOINT_URL
    }
}
filepath = os.getenv('OUTPUT_FILE_PATTERN').format(year=2023, month=1)
actual_result = pd.read_parquet(filepath, storage_options=options)
expected_result = pd.DataFrame([['2023/01_0', 23.20], ['2023/01_1', 13.08]], 
                               columns=['ride_id', 'predicted_duration'])

print(actual_result)

pdt.assert_frame_equal(actual_result, expected_result, atol=0.01)