"""

Generator of TALib Wrapper Class code

"""
from jinja2 import Template

indicatorTmp = Template("""
class {{IndicatorClass}}(Indicator):
    __slots__ = (
        {% for i in params %}'{{i}}'{% if not loop.last %},{% endif %}{% endfor %}
    )

    def __init__(self, input, input_key=None, {% for i in params %}{{i}}, {% endfor %} desc="{{description}}"):
        super({{IndicatorClass}}, self).__init__(Indicator.get_name({{IndicatorClass}}.__name__, input, input_key, length), input, input_key, desc)
        self.length = int(length)
        {% for p in params %}self.{{p}} = {{p}}
        {% endfor %}
        super({{IndicatorClass}}, self).update_all()

    def on_update(self, data):

        result = {}
        result['timestamp'] = data['timestamp']
        if self.input.size() >= self.length:
            value = talib.{{IndicatorClass}}(
                np.array(
                    self.input.get_by_idx(keys=self.input_keys,
                                     idx=slice(-self.length, None, None))), {% for p in params %} {{p}}=self.{{p}}{% if not loop.last %},{% endif %}{% endfor %})

            result[Indicator.VALUE] = value[-1]
        else:
            result[Indicator.VALUE] = np.nan

        self.add(result)
""")

print indicatorTmp.render({"IndicatorClass": "APO",
                           "description": "apo test",
                           "params": ["fastperiod", "slowperiod", "matype"]})

single_ds_list = ["APO", "BBANDS", "CMO", "DEMA", "EMA", "HT_DCPERIOD", "HT_DCPHASE", "HT_PHASOR", "HT_SINE",
                  "HT_TRENDLINE", "HT_TRENDMODE", "KAMA", "LINEARREG", "LINEARREG_ANGLE", "LINEARREG_INTERCEPT"]
