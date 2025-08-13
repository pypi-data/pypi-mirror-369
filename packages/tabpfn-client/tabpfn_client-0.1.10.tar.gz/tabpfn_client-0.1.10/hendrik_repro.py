from unittest.mock import patch
import pandas as pd
import numpy as np
from tabpfn_time_series import TabPFNTimeSeriesPredictor, TabPFNMode
from tabpfn_client import set_access_token
from autogluon.timeseries import TimeSeriesDataFrame
from tabpfn_time_series import FeatureTransformer, DefaultFeatures
import json

from tabpfn_client.config import get_access_token
 
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyIjoiM2ZkOThjNDgtNWJiMi00ZWQ2LTljNjYtMDgyMDI3ZjA4NzA1IiwiZXhwIjoxNzg1ODYyNDgyfQ.c2hKKSN0hZnSQOtejlyi_Rh8xA30vydyRTpQzo2c-4E'
set_access_token(token)

with patch("webbrowser.open", return_value=False):
    for i in range(2):
        dates = pd.date_range('2024-01-01', periods=50, freq='D')
        train_df = pd.DataFrame({'timestamp': dates, 'target': np.random.randn(50), 'item_id': 'series1'})
        test_df = pd.DataFrame({
            'timestamp': pd.date_range(dates[-1] + pd.Timedelta(days=1), periods=10, freq='D'),
            'target': np.nan,  # target-Spalte hinzugefügt
            'item_id': 'series1'
        })
    
        train_feat, test_feat = FeatureTransformer.add_features(
            TimeSeriesDataFrame(train_df),
            TimeSeriesDataFrame(test_df),
            [DefaultFeatures.add_running_index, DefaultFeatures.add_calendar_features]
    
        )
    
        predictor = TabPFNTimeSeriesPredictor(tabpfn_mode=TabPFNMode.CLIENT)
        pred = predictor.predict(train_feat, test_feat)
