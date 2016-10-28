from collections import namedtuple

OrderAttribute = namedtuple('TimeInForce',
                            ['DAY', 'GTC', 'OPG', 'IOC', 'GTD', 'FOK', 'DTC'])

time_in_force = OrderAttribute('DAY', 'GTC', 'OPG', 'IOC', 'GTD', 'FOK', 'DTC')
