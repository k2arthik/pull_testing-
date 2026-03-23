import threading
import time
import requests

TARGET_URL = "http://127.0.0.1:8001/"
NUM_THREADS = 10
REQUESTS_PER_THREAD = 10

def make_requests(thread_id, results):
    success = 0
    failed = 0
    total_time = 0
    
    for _ in range(REQUESTS_PER_THREAD):
        try:
            start_time = time.time()
            response = requests.get(TARGET_URL, timeout=5)
            duration = time.time() - start_time
            
            if response.status_code == 200:
                success += 1
                total_time += duration
            else:
                failed += 1
        except Exception:
            failed += 1
            
    results[thread_id] = {
        'success': success,
        'failed': failed,
        'total_time': total_time
    }

def run_load_test():
    print(f"Starting Load Test on {TARGET_URL}...")
    print(f"Simulating {NUM_THREADS} concurrent users making {REQUESTS_PER_THREAD} requests each.\n")
    
    threads = []
    results = {}
    
    start_time = time.time()
    for i in range(NUM_THREADS):
        t = threading.Thread(target=make_requests, args=(i, results))
        threads.append(t)
        t.start()
        
    for t in threads:
        t.join()
        
    total_duration = time.time() - start_time
    
    total_success = sum(r['success'] for r in results.values())
    total_failed = sum(r['failed'] for r in results.values())
    
    all_times = [r['total_time'] for r in results.values() if r['success'] > 0]
    avg_response_time = (sum(all_times) / total_success * 1000) if total_success > 0 else 0
    
    req_per_sec = total_success / total_duration if total_duration > 0 else 0
    
    print("-" * 30)
    print("RESULTS:")
    print(f"Total Requests Completed: {total_success + total_failed}")
    print(f"Successful Responses (200 OK): {total_success}")
    print(f"Failed Responses: {total_failed}")
    print(f"Total Time Taken: {total_duration:.2f} seconds")
    print(f"Average Response Time: {avg_response_time:.2f} ms")
    print(f"Requests Per Second (RPS): {req_per_sec:.2f}")
    print("-" * 30)

if __name__ == "__main__":
    run_load_test()
