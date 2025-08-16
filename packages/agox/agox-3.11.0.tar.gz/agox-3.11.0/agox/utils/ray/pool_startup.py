import traceback


from agox.utils.ray.pool import Pool
from agox.utils.ray.startup import ray_startup


class PoolFailedtoStartError(Exception):
    def __init__(self, attempts, message="Failed to start pool after {} attempts."):
        message = message.format(attempts)
        super().__init__(message)


def make_ray_pool(ray_stats, attempt=0, max_attempts=10, verbose: bool = False, **kwargs):
    try:
        # Make the pool:
        ray_pool_instance = Pool(num_actors=int(ray_stats["CPU"]), verbose=verbose)

        print(f"Attempt {attempt}: Pool started successfully.")
        return ray_pool_instance

    except Exception as e:
        print(f"Attempt {attempt}: Failed to correctly start pool.")
        print(f"Error: \n\t{ e}")
        print(f"Traceback: \n{traceback.format_exc()}")

        if attempt < max_attempts:
            return make_ray_pool(ray_stats, attempt=attempt + 1, max_attempts=max_attempts, **kwargs)
        else:
            raise PoolFailedtoStartError(attempt)


global ray_pool_instance
ray_pool_instance = None


def get_ray_pool(verbose: bool = False, **kwargs):
    # Start Ray - this doesn't do anything if Ray is already started.
    ray_stats = ray_startup(**kwargs)

    # Make the Pool if it doesn't exist already.
    global ray_pool_instance
    if ray_pool_instance is None:
        ray_pool_instance = make_ray_pool(ray_stats, verbose=verbose, **kwargs)
    return ray_pool_instance, ray_stats


def configure_ray_pool(
    cpu_count: int = None,
    memory: int = None,
    tmp_dir: str = None,
    include_dashboard: bool = False,
    max_grace_period: float = 0.0,
    keep_log_files: bool = False,
    verbose: bool = False,
):
    """
    Configure the settings for the Ray pool.

    Parameters:
    -----------
    cpu_count: int = None,
    memory: int = None,
    tmp_dir: str = None,
    include_dashboard: bool = False,
    max_grace_period: float = 15.0,
    """
    global ray_pool_instance
    if ray_pool_instance is not None:
        raise ValueError("Pool already started. Cannot reconfigure.")

    pool, _ = get_ray_pool(
        cpu_count=cpu_count,
        memory=memory,
        tmp_dir=tmp_dir,
        include_dashboard=include_dashboard,
        max_grace_period=max_grace_period,
        keep_log_files=keep_log_files,
        verbose=verbose,
    )
    return None


def reset_ray_pool(**kwargs):
    """
    Should only be used for testing.
    """
    pool, _ = get_ray_pool(**kwargs)
    pool.reset_pool()
