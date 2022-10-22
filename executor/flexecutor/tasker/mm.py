import sys
import numpy as np
import json

class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)

# input_data in this format:
# {"a": [[0.5, 1, 2, 3], [0, 1, 2, 3], [0.5, 1, 2, 3], [0, 1, 2, 3]], "b": [[..],[..],[..],[..]]}
def run_mm_task(input_data):
    print("in mm_task")
    print(input_data)
    a = np.array(input_data["a"])
    b = np.array(input_data["b"])
    res = np.matmul(a, b)
    json_dump = json.dumps(res, cls=NumpyEncoder)
    return json_dump

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print("needs input_data as arg")
        sys.exit(1)
    # a = np.random.rand(4,4)
    # b = np.random.rand(4,4)
    run_mm_task(sys.argv[1])
