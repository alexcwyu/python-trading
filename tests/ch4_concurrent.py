import time

import concurrent.futures

number_list = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


def evaluate(x):
    result = count(x)
    print "item %s result %s" % (x, result)


def count(x):
    for i in range(0, 10000000):
        i += 1
    return i * x


if __name__ == "__main__":
    # Seq execution
    start_time = time.clock()
    for i in number_list:
        evaluate(i)
    print "seq execution in %s" % (time.clock() - start_time)

    # Thread execution
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
        start_time = time.clock()
        for i in number_list:
            executor.submit(evaluate, i)
    print "threadpool execution in %s" % (time.clock() - start_time)

    # ProcessPool execution

    with concurrent.futures.ProcessPoolExecutor(max_workers=4) as executor:
        start_time = time.clock()
        for i in number_list:
            executor.submit(evaluate, i)
    print "processpool execution in %s" % (time.clock() - start_time)
