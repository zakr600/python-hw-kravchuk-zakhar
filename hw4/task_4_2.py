import math
import time
import os
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor


def integrate(f, a, b, *, n_jobs=1, n_iter=10000000):
    acc = 0
    step = (b - a) / n_iter
    for i in range(n_iter):
        acc += f(a + i * step) * step
    return acc


def integrate_chunk(f, a, b, start_iter, end_iter, n_iter):
    acc = 0
    step = (b - a) / n_iter
    for i in range(start_iter, end_iter):
        acc += f(a + i * step) * step
    return acc


def integrate_parallel(f, a, b, *, n_jobs=1, n_iter=10000000, executor_class=None):
    if n_jobs == 1:
        return integrate(f, a, b, n_jobs=1, n_iter=n_iter)
    
    chunk_size = n_iter // n_jobs
    chunks = []
    
    for i in range(n_jobs):
        start = i * chunk_size
        end = (i + 1) * chunk_size if i < n_jobs - 1 else n_iter
        chunks.append((start, end))
    
    with executor_class(max_workers=n_jobs) as executor:
        futures = [
            executor.submit(integrate_chunk, f, a, b, start, end, n_iter)
            for start, end in chunks
        ]
        results = [future.result() for future in futures]
    
    return sum(results)


def main():
    cpu_count = os.cpu_count()
    max_jobs = cpu_count * 2
    
    print(f"Количество CPU: {cpu_count}")
    print(f"Максимальное количество воркеров: {max_jobs}")
    print("=" * 60)
    
    f = math.cos
    a = 0
    b = math.pi / 2
    n_iter = 10000000
    
    results = []
    
    print("\nThreadPoolExecutor:")
    print("-" * 60)
    for n_jobs in range(1, max_jobs + 1):
        start_time = time.time()
        result = integrate_parallel(f, a, b, n_jobs=n_jobs, n_iter=n_iter, executor_class=ThreadPoolExecutor)
        elapsed_time = time.time() - start_time
        results.append(("ThreadPoolExecutor", n_jobs, elapsed_time, result))
        print(f"n_jobs={n_jobs:2d}: {elapsed_time:.4f} секунд, результат={result:.10f}")
    
    print("\nProcessPoolExecutor:")
    print("-" * 60)
    for n_jobs in range(1, max_jobs + 1):
        start_time = time.time()
        result = integrate_parallel(f, a, b, n_jobs=n_jobs, n_iter=n_iter, executor_class=ProcessPoolExecutor)
        elapsed_time = time.time() - start_time
        results.append(("ProcessPoolExecutor", n_jobs, elapsed_time, result))
        print(f"n_jobs={n_jobs:2d}: {elapsed_time:.4f} секунд, результат={result:.10f}")
    
    with open("artifacts/4_2_results.txt", "w", encoding="utf-8") as f:
        f.write("Сравнение времени выполнения integrate с различными executor'ами\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"Функция: math.cos\n")
        f.write(f"Интервал: [{a}, {b}]\n")
        f.write(f"Количество итераций: {n_iter}\n")
        f.write(f"Количество CPU: {cpu_count}\n")
        f.write(f"Максимальное количество воркеров: {max_jobs}\n\n")
        
        f.write("ThreadPoolExecutor:\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'n_jobs':<10} {'Время (сек)':<15} {'Результат':<20}\n")
        f.write("-" * 60 + "\n")
        for executor_type, n_jobs, elapsed_time, result in results:
            if executor_type == "ThreadPoolExecutor":
                f.write(f"{n_jobs:<10} {elapsed_time:<15.4f} {result:<20.10f}\n")
        
        f.write("\nProcessPoolExecutor:\n")
        f.write("-" * 60 + "\n")
        f.write(f"{'n_jobs':<10} {'Время (сек)':<15} {'Результат':<20}\n")
        f.write("-" * 60 + "\n")
        for executor_type, n_jobs, elapsed_time, result in results:
            if executor_type == "ProcessPoolExecutor":
                f.write(f"{n_jobs:<10} {elapsed_time:<15.4f} {result:<20.10f}\n")
        
        thread_results = [(n_jobs, time) for t, n_jobs, time, _ in results if t == "ThreadPoolExecutor"]
        process_results = [(n_jobs, time) for t, n_jobs, time, _ in results if t == "ProcessPoolExecutor"]
        
        best_thread = min(thread_results, key=lambda x: x[1])
        best_process = min(process_results, key=lambda x: x[1])
        
        f.write("\n" + "=" * 60 + "\n")
        f.write("Анализ:\n")
        f.write(f"- Лучший результат ThreadPoolExecutor: n_jobs={best_thread[0]}, время={best_thread[1]:.4f} сек\n")
        f.write(f"- Лучший результат ProcessPoolExecutor: n_jobs={best_process[0]}, время={best_process[1]:.4f} сек\n")
        f.write(f"- ProcessPoolExecutor быстрее в {best_thread[1]/best_process[1]:.2f} раз\n")
    
    print("\nРезультаты сохранены в artifacts/4_2_results.txt")


if __name__ == "__main__":
    main()

