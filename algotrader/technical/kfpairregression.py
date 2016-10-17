"""
Created on 7/7/16
Author = jchan
"""
__author__ = 'jchan'

import numpy as np
from pykalman import KalmanFilter

from algotrader.technical import Indicator


class KalmanFilteringPairRegression(Indicator):
    SLOPE = 'slope'
    INTERCEPT = 'intercept'

    __slots__ = (
        'length'
    )

    @staticmethod
    def get_name(input, length):
        return "KalmanFilteringPairRegression(%s,%s)" % (Indicator.get_input_name(input), length)

    def __init__(self, input=None, length=10, description="Kalman Filter Regression"):
        super(KalmanFilteringPairRegression, self) \
            .__init__(KalmanFilteringPairRegression.get_name(input, length),
                      input=input,
                      keys=['slope', 'intercept'],
                      default_key='slope',
                      description=description)
        self.length = int(length)
        delta = 1e-5
        self.trans_cov = delta / (1 - delta) * np.eye(2)
        super(KalmanFilteringPairRegression, self).update_all()

    def on_update(self, data):
        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:

            independent_var = self.input.get_by_idx_range(key=None, start_idx=0, end_idx=-1)
            symbol_set = set(self.input.keys)
            depend_symbol = symbol_set.difference(self.input.default_key)
            depend_var = self.input.get_by_idx_range(key=depend_symbol, start_idx=0, end_idx=-1)

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
            self.add(result)

        else:
            result[Indicator.VALUE] = np.nan
            result[KalmanFilteringPairRegression.SLOPE] = np.nan
            result[KalmanFilteringPairRegression.SLOPE] = np.nan
            self.add(result)
