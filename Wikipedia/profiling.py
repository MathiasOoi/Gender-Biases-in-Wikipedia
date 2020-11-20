import collections
import contextlib
import time

times = collections.defaultdict(float)
@contextlib.contextmanager
def timer(name):
    start = time.time()
    yield
    times[name] += time.time() - start

def print_times():
    print('=======================================')
    for k,v in times.items():
        print(f'{k} = {v}')


if __name__ == '__main__':
    with timer("sleep"):
        time.sleep(2.5)
    print_times()
