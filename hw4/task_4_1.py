import time
import threading
import multiprocessing


def fibonacci(n):
    if n <= 1:
        return n
    a, b = 0, 1
    for _ in range(2, n + 1):
        a, b = b, a + b
    return b


def run_sync(n, iterations=10):
    start_time = time.perf_counter()
    results = []
    for _ in range(iterations):
        results.append(fibonacci(n))
    end_time = time.perf_counter()
    return end_time - start_time, results


def run_threading(n, iterations=10):
    results = []
    lock = threading.Lock()
    
    def worker():
        result = fibonacci(n)
        with lock:
            results.append(result)
    
    start_time = time.perf_counter()
    threads = []
    for _ in range(iterations):
        thread = threading.Thread(target=worker)
        threads.append(thread)
        thread.start()
    
    for thread in threads:
        thread.join()
    end_time = time.perf_counter()
    return end_time - start_time, results


def run_multiprocessing(n, iterations=10):
    def worker(n, result_queue):
        result = fibonacci(n)
        result_queue.put(result)
    
    start_time = time.perf_counter()
    processes = []
    result_queue = multiprocessing.Queue()
    
    for _ in range(iterations):
        process = multiprocessing.Process(target=worker, args=(n, result_queue))
        processes.append(process)
        process.start()
    
    for process in processes:
        process.join()
    
    results = []
    while not result_queue.empty():
        results.append(result_queue.get())
    
    end_time = time.perf_counter()
    return end_time - start_time, results


def main():
    with open("artifacts/4_1_results.txt", "w", encoding="utf-8") as f:
        for n in [10000, 60000]:
            iterations = 10
            
            sync_time, _ = run_sync(n, iterations)
            threading_time, _ = run_threading(n, iterations)
            multiprocessing_time, _ = run_multiprocessing(n, iterations)
        
        
            f.write("=" * 60 + "\n\n")
            f.write("Сравнение времени выполнения функции подсчета чисел Фибоначчи\n")
            f.write(f"Параметры: n={n}, количество запусков={iterations}\n\n")
            if sync_time > 0:
                f.write(f"- Синхронный запуск: {sync_time:.6f} секунд (последовательное выполнение)\n")
                f.write(f"- Threading: {threading_time:.6f} секунд\n")
                f.write(f"- Multiprocessing: {multiprocessing_time:.6f} секунд\n")
            else:
                f.write("- Время выполнения слишком мало для точного измерения\n")
    
    print("\nРезультаты сохранены в artifacts/4_1_results.txt")


if __name__ == "__main__":
    main()

