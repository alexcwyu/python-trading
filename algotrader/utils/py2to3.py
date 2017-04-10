##
# import to make code compatibility with both python2 and python3
##


try:
    range = xrange  # Python 2
except NameError:
    pass  # Python 3
