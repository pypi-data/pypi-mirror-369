import time
import inspect
import functools

def _print_cost(name, elapsed):
    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)
    if hours >= 1:
        print(f"function [{name}] execution elapsed: {int(hours)}h {int(minutes)}m {seconds:.3f}s")
    elif minutes >= 1:
        print(f"function [{name}] execution elapsed: {int(minutes)}m {seconds:.3f}s")
    else:
        print(f"function [{name}] execution elapsed: {seconds:.3f}s")
        
def get_time(func):
    if inspect.iscoroutinefunction(func):
        # 适配异步函数
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return await func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                _print_cost(func.__name__, end_time - start_time)
        return async_wrapper
    else:
        # 适配同步函数
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            start_time = time.perf_counter()
            try:
                return func(*args, **kwargs)
            finally:
                end_time = time.perf_counter()
                _print_cost(func.__name__, end_time - start_time)
        return sync_wrapper

    return wrapper
