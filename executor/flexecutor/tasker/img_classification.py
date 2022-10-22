# TODO add img_classification code
# import sys
#
# # task_id: 0 -> 49
# def run_loop_task(task_id, input_data):
#     print(f"[loop] running task {task_id}")
#     loop_end = task_id * 1000000 + 5000
#     sum = input_data
#     for i in range(loop_end):
#         sum += 1
#     return sum
#
# if __name__ == '__main__':
#     if len(sys.argv) != 3:
#         print("needs task_id, input as arg")
#         sys.exit(1)
#
#     run_loop_task(int(sys.argv[1]), int(sys.argv[2]))
