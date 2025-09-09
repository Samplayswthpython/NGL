#!/usr/bin/env python3

import signal
import threading
try:
    import requests
except ModuleNotFoundError:
    print("[!] Requests module Not Found!")
    exit()

# global counter (race condition prone!)
COUNTER: int = 0
exit_flag = threading.Event()

def post_requests(user: str, text: str) -> None:
    global COUNTER
    url: str = "https://ngl.link/api/submit"
    
    data: dict[str, str] = {
        'username': user,
        'question': text, 
        'deviceId': '5adh65ye-b542-48g5-b76a-33765y242e59',
        'gameSlug': '' ,
        'referrer': '',
    }

    while not exit_flag.is_set():
        try:
            resp = requests.post(url, data=data)
            COUNTER += 1
            print(f"\r[$] Message's sent to {user}: {COUNTER}", end="")
        except Exception as e:
            print(f"\n[!] Error: {e}")

def exit_prog(sig: int, frame) -> None:
    print(f"\n[-] CTRL+c pressed killing all threads")
    exit_flag.set()

def main() -> None:
    user: str = input("[*] Enter the username: ")
    text: str = input("[*] Enter the text: ")
    
    signal.signal(signal.SIGINT, exit_prog)

    threads = []
    for _ in range(20):
        thread = threading.Thread(target=post_requests, args=(user, text))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    printf(f"[*] All threads were killed gracefully")

if __name__ == "__main__":
    main()
