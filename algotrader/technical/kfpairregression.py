"""
Created on 7/7/16
Author = jchan
"""
__author__ = 'jchan'

import numpy as np
from pykalman import KalmanFilter
from typing import Dict

from algotrader.technical import Indicator


class KalmanFilteringPairRegression(Indicator):
    SLOPE = 'slope'
    INTERCEPT = 'intercept'

    __slots__ = (
        'length'
    )

    def __init__(self, time_series=None, inputs=None, input_keys=None, desc="Kalman Filter Regression", length=10):
        super(KalmanFilteringPairRegression, self).__init__(time_series=time_series, inputs=inputs,
                                                            input_keys=input_keys, desc=desc,
                                                            keys=['slope', 'intercept'],
                                                            default_key='slope',
                                                            length=length)
        self.length = self.get_int_config("length", 10)
        delta = 1e-5
        self.trans_cov = delta / (1 - delta) * np.eye(2)
        # super(KalmanFilteringPairRegression, self)._update_from_inputs()

    def _process_update(self, source: str, timestamp: int, data: Dict[str, float]):
        result = {}

        if input.size() >= self.length:

            independent_var = self.first_input.get_by_idx_range(key=None, start_idx=0, end_idx=-1)
            symbol_set = set(self.first_input.keys)
            depend_symbol = symbol_set.difference(self.first_input.default_key)
            depend_var = self.first_input.get_by_idx_range(key=depend_symbol, start_idx=0, end_idx=-1)

            obs_mat = np.vstack([independent_var.values, np.ones(independent_var.values.shape)]).T[:, np.newaxis]
            model = KalmanFilter(n_dim_obs=1, n_dim_state=2,
                                 initial_state_mean=np.zeros(2),
                                 initial_state_covariance=np.ones((2, 2)),
                                 transition_matrices=np.eye(2),
                                 observation_matrices=obs_mat,
                                 observation_covariance=1.0,
                                 transition_covariance=self.trans_cov)

            state_means, state_covs = model.filter(depend_var.values)
            slope = state_means[:, 0][-1]
            result[Indicator.VALUE] = slope
            result[KalmanFilteringPairRegression.SLOPE] = slope
            result[KalmanFilteringPairRegression.SLOPE] = state_means[:, 1][-1]
            self.add(timestamp=timestamp, data=result)

        else:
            result[Indicator.VALUE] = np.nan
            result[KalmanFilteringPairRegression.SLOPE] = np.nan
            result[KalmanFilteringPairRegression.SLOPE] = np.nan
            self.add(timestamp=timestamp, data=result)
