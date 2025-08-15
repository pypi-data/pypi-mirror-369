def get_gpus_info():
    info = []
    try:
        from pynvml_utils import nvidia_smi
        nvsmi = nvidia_smi.getInstance()
        gpus = nvsmi.DeviceQuery('gpu_name,memory.used,memory.free,memory.total')['gpu']
        info = [(i['product_name'], i['fb_memory_usage']['used'], i['fb_memory_usage']['free'],
                 i['fb_memory_usage']['total'])
                for i in gpus]
    except Exception as e:
        print('Run `pip install pynvml`')
    return info


def gpu_task_maximum(task_usage_size: int, reserve_size: int = 1024):
    """各GPU可创建的任务数
    @param task_usage_size: 任务使用的显存大小(MiB)
    @param reserve_size: 预留的显存大小(MiB)
    @return: 各GPU可创建的任务数
    """
    return [(i[2] - reserve_size) // task_usage_size for i in get_gpus_info()]
