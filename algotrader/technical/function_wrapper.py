from algotrader.utils.data_series import iterable_to_np_array


class FunctionWithPeriodsName(object):
    def __init__(self, func, periods, name=None, feedback=False, output_columns=None, array_utils=iterable_to_np_array):
        self.periods = periods
        self.func = func
        self.array_utils = array_utils
        self.feedback = feedback
        self.output_columns = output_columns
        if not name:
            self.name = func.__name__
        else:
            self.name = name

    def __call__(self, *args, **kwargs):
        return self.func(periods=self.periods, *args, **kwargs)


class TALibFunction(FunctionWithPeriodsName):
    def __init__(self, periods, func, name=None, array_utils=iterable_to_np_array):
        super(TALibFunction, self).__init__(periods=periods, func=func, name=name, array_utils=array_utils)

    def __call__(self, *args, **kwargs):
        return self.func(timeperiod=self.periods, *args, **kwargs)


class ModelAsFunction(FunctionWithPeriodsName):
    def __init__(self, model, periods, name, array_utils):
        super(ModelAsFunction, self).__init__(periods=periods, func=None, name=name, array_utils=array_utils)
        self.model = model

    def __call__(self, *args, **kwargs):
        raise NotImplementedError


class SKLearnTransformer(ModelAsFunction):
    def __init__(self, model, periods, name, array_utils):
        super(SKLearnTransformer, self).__init__(periods=periods, func=model, name=name, array_utils=array_utils)

    def __call__(self, *args, **kwargs):
        return self.model.fit_transform(*args, **kwargs)


class SKLearnPredictor(ModelAsFunction):
    def __init__(self, periods, model, name, array_utils):
        super(SKLearnTransformer, self).__init__(periods=periods, func=model, name=name, array_utils=array_utils)

    def __call__(self, *args, **kwargs):
        return self.model.predict(*args, **kwargs)


class DigitalFeedbackFilter(FunctionWithPeriodsName):
    def __init__(self, func, periods, phase_periods, feedback_periods, name=None, array_utils=iterable_to_np_array):
        """
        filter_series = func * input_series

        :param func:
        :param periods:
        :param phase_periods:
        :param feedback_periods:
        :param name:
        :param array_utils:
        """
        super(DigitalFeedbackFilter, self).__init__(periods=periods, func=func, name=name, array_utils=array_utils)
        self.phase_periods = phase_periods
        self.feeback_periods = feedback_periods

    def __call__(self, *args, **kwargs):
        return self.func(phase_periods=self.phase_periods, *args, **kwargs)


def periods_function(periods, name=None):
    def function_wrapper(f):
        return FunctionWithPeriodsName(func=f, periods=periods, name=name)

    return function_wrapper


def talib_function(periods, name):
    def function_wrapper(f):
        return TALibFunction(func=f, periods=periods, name=name)

    return function_wrapper


def sklearn_trasformer_function(periods, name):
    def function_wrapper(model):
        return SKLearnTransformer(model=model, periods=periods, name=name)

    return function_wrapper



