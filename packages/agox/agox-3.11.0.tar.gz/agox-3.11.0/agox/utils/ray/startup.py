import atexit
import os
import shutil
from time import sleep
from typing import Optional

import numpy as np
import ray


def get_cpu_count(cpu_count):
    if cpu_count is None:
        try:
            cpu_count = int(os.environ["SLURM_NTASKS"])
        except:
            cpu_count = len(os.sched_getaffinity(0))
    return cpu_count


def get_memory(memory, cpu_count):
    if memory is None:
        try:
            memory = int(os.environ["SLURM_MEM_PER_NODE"] * 1e6)
        except:
            memory = cpu_count * int(2 * 1e9)
    return memory


def get_tmp_dir(tmp_dir: Optional[str]) -> str:
    """Get a suitable directory to use as Ray logging directory.

    Parameters
    ----------
    tmp_dir : Optional[str]
        Temporary directory to attempt to use. If None, a subdirectory of the
        current working directory is used.

    Returns
    -------
    str
        Ray logging directory path.
    """
    if tmp_dir is None:
        tmp_dir = os.path.join(os.getcwd(), "ray")

    if not check_tmp_dir_length(tmp_dir):
        tmp_dir = os.path.expanduser("~") + "/tmp/ray"
        print(f"Using {tmp_dir} as Ray temporary folder because the given or " "generated path is too long.")

    return tmp_dir


def check_tmp_dir_length(tmp_dir: str) -> bool:
    """Check whether the directory path is short enough to be used as Ray
    logging directory.

    Ray opens a Unix socket in this directory, and the maximum path length for
    a Unix socket on Linux is 107 bytes. The path to this Unix socket is
    determined as follows, with below each field the (maximum) length of that
    field:
    `[tmp_dir]/session_%Y-%m-%d_%H-%M-%S_%F_[pid]/sockets/plasma_store`
                        4  2  2  2  2  2  6   7*
    * The pid is limited by PID_MAX_LIMIT = 4194304.

    Hence, the additional part after `tmp_dir` is 64 characters long:
    `/session_xxxx-xx-xx_xx-xx-xx_xxxxxx_xxxxxxx/sockets/plasma_store`
     1234567890123456789012345678901234567890123456789012345678901234

    Parameters
    ----------
    tmp_dir : str
        Directory path to check.

    Returns
    -------
    bool
        Whether the directory path is short enough.
    """
    return len(tmp_dir.encode("utf-8")) + 64 <= 107


def ray_startup(
    cpu_count: int = None,
    memory: int = None,
    tmp_dir: str = None,
    include_dashboard: bool = False,
    max_grace_period: float = 0.0,
    keep_log_files: bool = False,
):
    """
    Start a Ray instance on Slurm.

    Parameters
    ----------
    cpu_count : int, optional
        Number of CPU cores to use, by default None in which case defaults are
        read from SLURM.
    memory : int, optional
        Amount of memeory to use in bits, by default None in which case environment
        variables are used to guess a suitable amount.
    tmp_dir : str, optional
        Temporary directory for Ray to use, by default None in which case a
        directory is created in the current working directory.
    include_dashboard : bool, optional
        Whether or not to include the Ray dashboard, by default False.
    keep_log_files : bool, optional
        Whether to keep the Ray log files after the task is terminated, by
        default False.
    """

    if ray.is_initialized():
        return ray.cluster_resources()

    # CPU Count:
    cpu_count = get_cpu_count(cpu_count)
    memory = get_memory(memory, cpu_count)
    tmp_dir = get_tmp_dir(tmp_dir)

    if max_grace_period > 0:
        grace = np.random.uniform(0, max_grace_period)
        print(f"Sleeping {grace} s", flush=True)
        sleep(grace)
    ray_context = ray.init(
        address="local",
        object_store_memory=int(memory / 4),
        num_cpus=cpu_count,
        ignore_reinit_error=True,
        include_dashboard=include_dashboard,
        _temp_dir=tmp_dir,
        _memory=memory,
    )

    ray_stats = ray.cluster_resources()
    print("Ray Resources")
    for key, value in ray_stats.items():
        print(f"\t{key} = {value}")

    if not keep_log_files:
        atexit.register(ray_cleanup, path=ray_context.address_info.get("session_dir"))

    return ray_stats


def ray_cleanup(path: str):
    """Shut down Ray and (try to) delete the log directory.

    Parameters
    ----------
    path : str
        Path to the log directory.
    """
    ray.shutdown()

    if os.path.exists(path):
        try:
            shutil.rmtree(path)
        except Exception as e:
            print("Exception occurred when cleaning up the Ray log directory:")
            print(str(e))
