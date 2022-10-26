import sys
import cupy as np
import json

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# input_data in this format:
# {"a": [[0.5, 1, 2, 3], [0, 1, 2, 3], [0.5, 1, 2, 3], [0, 1, 2, 3]], "b": [[..],[..],[..],[..]]}
def run_mm_task(input_data):
    a = np.array(input_data["a"])
    b = np.array(input_data["b"])
    res = np.matmul(a,b)
    np.cuda.Stream.null.synchronize()
    json_dump = json.dumps(res, cls=NumpyEncoder)
    return json_dump


if __name__ == '__main__':
    if len(sys.argv) != 2:
       print("needs input_data as arg")
       sys.exit(1)

    # https://stackoverflow.com/questions/64409663/why-is-my-gpu-slower-than-cpu-in-matrix-operations
    a = np.random.random([10000,10000], dtype=np.float32)
    b = np.random.random([10000,10000], dtype=np.float32)
    run_mm_task({"a":a, "b":b})

    # code to generate matrix input in json format:
    # a = np.ones(50000,50000)
    # b = np.ones(50000,50000)
    # print(json.dumps({"a": a, "b": b}, cls=NumpyEncoder))

