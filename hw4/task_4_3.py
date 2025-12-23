import multiprocessing
import sys
import time
import threading
import codecs


def rot13(text):
    return codecs.encode(text, 'rot13')


def process_a(input_queue, output_queue):
    while True:
        try:
            message = input_queue.get()
            if message is None:
                output_queue.put(None)
                break
            
            lower_message = message.lower()
            
            time.sleep(5)
            output_queue.put(lower_message)
        except Exception as e:
            print(f"Ошибка в процессе A: {e}", file=sys.stderr)
            break


def process_b(input_queue, output_queue):
    while True:
        try:
            message = input_queue.get()
            if message is None:
                output_queue.put(None)
                break
            
            encoded_message = rot13(message)
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            print(f"[{timestamp}] Процесс B получил: {message} -> {encoded_message}")
            sys.stdout.flush()
            
            output_queue.put(encoded_message)
        except Exception as e:
            print(f"Ошибка в процессе B: {e}", file=sys.stderr)
            break


def input_reader(input_queue, log_file, log_lock):
    with log_lock:
        with open(log_file, "w", encoding="utf-8") as log:
            log.write("Лог взаимодействия с программой\n")
            log.write("=" * 60 + "\n\n")
    
    print("Введите сообщения:")
    
    while True:
        try:
            line = input()
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            
            with log_lock:
                with open(log_file, "a", encoding="utf-8") as log:
                    if line.lower() == 'quit':
                        log.write(f"[{timestamp}] Пользователь: {line}\n")
                        log.write(f"[{timestamp}] Завершение работы...\n")
                        input_queue.put(None)
                        break
                    
                    log.write(f"[{timestamp}] Пользователь отправил: {line}\n")
            
            if line.lower() != 'quit':
                input_queue.put(line)
            else:
                break
        except EOFError:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            with log_lock:
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[{timestamp}] EOF получен, завершение...\n")
            input_queue.put(None)
            break
        except KeyboardInterrupt:
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            with log_lock:
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[{timestamp}] Прервано пользователем\n")
            input_queue.put(None)
            break


def result_collector(result_queue, log_file, log_lock):
    while True:
        try:
            result = result_queue.get()
            if result is None:
                break
            
            timestamp = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
            with log_lock:
                with open(log_file, "a", encoding="utf-8") as log:
                    log.write(f"[{timestamp}] Главный процесс получил от процесса B: {result}\n")
            print(f"[{timestamp}] Результат получен: {result}")
        except Exception as e:
            print(f"Ошибка при сборе результатов: {e}", file=sys.stderr)
            break


def main():
    queue_a_to_b = multiprocessing.Queue()
    queue_b_to_main = multiprocessing.Queue()
    queue_main_to_a = multiprocessing.Queue()
    
    log_file = "artifacts/4_3_interaction.txt"
    log_lock = threading.Lock()
    
    process_a_instance = multiprocessing.Process(
        target=process_a,
        args=(queue_main_to_a, queue_a_to_b)
    )
    process_b_instance = multiprocessing.Process(
        target=process_b,
        args=(queue_a_to_b, queue_b_to_main)
    )
    
    process_a_instance.start()
    process_b_instance.start()
    
    input_thread = threading.Thread(
        target=input_reader,
        args=(queue_main_to_a, log_file, log_lock),
        daemon=True
    )
    result_thread = threading.Thread(
        target=result_collector,
        args=(queue_b_to_main, log_file, log_lock),
        daemon=True
    )
    
    input_thread.start()
    result_thread.start()
    
    try:
        input_thread.join()
        time.sleep(10)
        result_thread.join(timeout=1)
    except KeyboardInterrupt:
        print("\nПрерывание...")
        queue_main_to_a.put(None)
    
    process_a_instance.join(timeout=5)
    process_b_instance.join(timeout=5)
    
    if process_a_instance.is_alive():
        process_a_instance.terminate()
    if process_b_instance.is_alive():
        process_b_instance.terminate()
    
    print(f"\nЛог сохранен в {log_file}")


if __name__ == "__main__":
    main()

