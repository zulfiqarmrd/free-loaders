import json
import numpy as np

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
    json_dump = json.dumps(res, cls=NumpyEncoder)
    return json_dump

if __name__ == '__main__':
    a = np.random.rand(1000,1000)
    b = np.random.rand(1000,1000)
    # code to generate matrix input in json format:
    print(run_mm_task({"a": a, "b": b}))
