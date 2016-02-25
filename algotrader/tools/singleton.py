# class Singleton(type):
#     def __init__(cls, name, bases, dic):
#         super(Singleton, cls).__init__(name, bases, dic)
#         cls.instance = None
#
#     def __call__(cls, *args, **kwargs):
#         print "please use get_instance function to get the instance"
#
#     def get_instance(cls, *args, **kw):
#         if cls.instance is None:
#             cls.instance = super(Singleton, cls).__call__(*args, **kw)
#         return cls.instance



def singleton(class_):
    class class_w(class_):
        _instance = None

        def __new__(class_, *args, **kwargs):
            if class_w._instance is None:
                class_w._instance = super(class_w,
                                          class_).__new__(class_,
                                                          *args,
                                                          **kwargs)
                class_w._instance._sealed = False
            return class_w._instance

        def __init__(self, *args, **kwargs):
            if self._sealed:
                return
            super(class_w, self).__init__(*args, **kwargs)
            self._sealed = True

    class_w.__name__ = class_.__name__
    return class_w
