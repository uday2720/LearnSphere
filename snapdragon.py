import platform,time

def system_summary():
    return {'platform':platform.platform(),'machine':platform.machine(),'processor':platform.processor() or 'Unknown','python':platform.python_version()}
def benchmark_callable(fn,runs=10):
    start=time.perf_counter()
    for _ in range(runs):fn()
    elapsed=time.perf_counter()-start
    return {'runs':runs,'total_seconds':elapsed,'average_ms':elapsed/runs*1000}
def acceleration_status():
    return ('Snapdragon acceleration is a deployment target. This build reports hardware facts instead of fabricating NPU results. ONNX Runtime/QNN and Qualcomm AI Hub integration should be benchmarked on the target Snapdragon PC.')
