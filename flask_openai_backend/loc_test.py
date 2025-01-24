import requests
import threading
import time

# 测试目标接口
TARGET_URL = "http://127.0.0.1:8080/"

# 并发参数
CONCURRENT_USERS = 50  # 并发用户数
REQUEST_COUNT = 100    # 总请求数

success_count = 0
error_count = 0

def send_request():
    global success_count, error_count
    try:
        response = requests.get(TARGET_URL, timeout=10)
        if response.status_code == 200:
            success_count += 1
        else:
            error_count += 1
    except Exception as e:
        error_count += 1

# 记录测试时间
start_time = time.time()

# 创建线程池
threads = []
for _ in range(REQUEST_COUNT):
    thread = threading.Thread(target=send_request)
    threads.append(thread)
    thread.start()

# 等待所有线程完成
for thread in threads:
    thread.join()

# 输出结果
total_time = time.time() - start_time
print(f"总请求数: {REQUEST_COUNT}")
print(f"成功数: {success_count}")
print(f"失败数: {error_count}")
print(f"总耗时: {total_time:.2f}秒")
print(f"平均响应时间: {total_time / REQUEST_COUNT:.2f}秒/请求")
print(f"吞吐量: {REQUEST_COUNT / total_time:.2f}请求/秒")