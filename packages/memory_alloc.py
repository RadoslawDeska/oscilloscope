import tracemalloc


def profile_in_main_thread(func, *args, **kwargs):
    tracemalloc.start()
    first_snapshot = tracemalloc.take_snapshot()
    func(*args, **kwargs)
    end_snapshot = tracemalloc.take_snapshot()
    print("Memory Profile in Main Thread:")
    print_memory_stats(first_snapshot, end_snapshot)

def print_memory_stats(start_snapshot, end_snapshot):
    print("[Memory Usage]")
    stats = end_snapshot.compare_to(start_snapshot, 'traceback')  # More detailed tracing
    for index, stat in enumerate(stats[:10], 1):
        print(f"{index}: {stat}")
        for line in stat.traceback.format():
            print(line)