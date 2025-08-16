import math
import os
from concurrent.futures import ProcessPoolExecutor, ThreadPoolExecutor
from itertools import islice
from multiprocessing import Pipe, Pool, Process, cpu_count
from sys import modules
from threading import active_count
from typing import Callable, List

import torch
from tqdm import tqdm

from .logging import logger

__all__ = ['multi_process_thread', 'multiprocess_exe']


def process_worker_wrapper(args):
    _args = (args[0], [args[1]]) if not isinstance(args[1], list) else args
    return _args[0](*_args[1])


def multi_process_thread(
    func: Callable,
    mpargs: List,
    nprocess: int = -1,
    pool_func: str = 'Pool',
    map_func: str = 'imap',
    progress_bar: bool = True,
) -> List:
    """
    Create process / thread pool

    @param func: process / thread function
    @param kwargs: process / thread keyword argument list
    @param nprocess: number of process / thread
    @param pool_func: [Pool(multi process), ThreadPoolExecutor(multi thread)]
    @param map_func: [map, imap]
    """
    if nprocess == -1:
        if pool_func == 'Pool':
            nprocess = cpu_count()
        if pool_func == 'ThreadPoolExecutor':
            nprocess = active_count()

    assert nprocess > 0, f'invalid process num {nprocess}'
    if nprocess > 1:
        logger.debug(f'multi {"process" if pool_func == "Pool" else "thread"} with proc {nprocess}')
        with getattr(modules[__name__], pool_func)(nprocess) as pool:
            return list(tqdm(getattr(pool, map_func)(
                process_worker_wrapper, [(func, args) for args in mpargs]),
                total=len(mpargs), disable=(not progress_bar)))
    else:
        return list([func(*(args if isinstance(args, list) else [args]))
            for args in tqdm(mpargs, disable=(not progress_bar))])


def list_split(data_list, split_num):
    it = iter(data_list)
    chunk_size = math.ceil(len(data_list) / split_num)
    return list(iter(lambda: tuple(islice(it, chunk_size)), ()))


def task_worker(func, sub_arg_list, child_conn=None):
    results = []
    for args in tqdm(sub_arg_list, total=len(sub_arg_list), desc="[{}]".format(os.getpid())):
        results.append(func(*args))
    if child_conn is not None:
        child_conn.send(results)
        child_conn.close()
    else:
        return results


def init_process(func, arg_list):
    pipe_list = []
    process_list = []
    for arg in arg_list:
        conns = Pipe()
        args = (*arg, conns[1])
        p = Process(target=func, args=args)
        pipe_list.append(conns)
        process_list.append(p)
    return pipe_list, process_list


def start_processes(pipe_list, process_list):
    res = []
    for p in process_list:
        p.start()
    for conn in pipe_list:
        res.extend(conn[0].recv())
    for process in process_list:
        process.join()
        process.close()
    return res


def multiprocess_exe(func, arg_list, processes_num, daemon_process=True):
    split_arg_list = list_split(arg_list, processes_num)
    wrappered_arg_list = []
    for seq, sub_arg_list in enumerate(split_arg_list):
        wrappered_arg_list.append([func, sub_arg_list])
    if daemon_process:
        flatten_results = []
        with Pool(processes=processes_num) as p:
            nested_results = p.starmap(task_worker, wrappered_arg_list)
        for result in nested_results:
            flatten_results.extend(result)
        return flatten_results
    else:
        pipe_list, process_list = init_process(task_worker, wrappered_arg_list)
        return start_processes(pipe_list, process_list)


def gpu_task_worker(func, sub_arg_list, device):
    os.environ["TASK_DEVICE"] = device
    results = []
    for args in tqdm(sub_arg_list, total=len(sub_arg_list), desc="[{}]".format(os.getpid())):
        results.append(func(*args))
    return results


def multiprocess_exe_gpu(func, arg_list, processes_num):
    processes_num = min(processes_num, torch.cuda.device_count())
    split_arg_list = list_split(arg_list, processes_num)
    wrappered_arg_list = []
    for seq, sub_arg_list in enumerate(split_arg_list):
        wrappered_arg_list.append([func, sub_arg_list, "cuda:{}".format(seq)])
    ctx = torch.multiprocessing.get_context("spawn")
    flatten_results = []
    with ctx.Pool(processes=processes_num) as p:
        nested_results = p.starmap(gpu_task_worker, wrappered_arg_list)
        for result in nested_results:
            flatten_results.extend(result)
    return flatten_results
