#!/usr/bin/env python3

import signal
import threading
import random
import string
import time 
try:
    import requests
except ModuleNotFoundError:
    print("[!] Requests module Not Found!")
    exit()

# global counter (race condition prone!)
COUNTER: int = 0
COOLDOWN_TIMER: int = 2

exit_flag = threading.Event()
cooldown_event = threading.Event()

def deviceId() -> str:
    characters: str = string.ascii_lowercase + ''.join([str(i) for i in range(0, 10)])
    id: list[str] = [
        ''.join([random.choice(characters) for _ in range(0, 8)]),
        ''.join([random.choice(characters) for _ in range(0, 4)]),
        ''.join([random.choice(characters) for _ in range(0, 4)]),
        ''.join([random.choice(characters) for _ in range(0, 12)]),
    ]

    return '-'.join(id)

def trigger_cooldown() -> None:
    if not cooldown_event.is_set():
        cooldown_event.set()
        threading.Thread(target=count_cooldown, daemon=True).start()

def count_cooldown() -> None:
    time.sleep(COOLDOWN_TIMER)
    cooldown_event.clear()

def post_requests(user: str, text: str) -> None:
    global COUNTER
    url: str = "https://ngl.link/api/submit"

    data: dict[str, str] = {
        'username': user,
        'question': text, 
        'gameSlug': '' ,
        'referrer': '',
    }

    while not exit_flag.is_set():
        while cooldown_event.is_set() and not exit_flag.is_set():
            time.sleep(2)

        data['deviceId'] = deviceId()

        try:
            resp = requests.post(url, data=data)
            COUNTER += 1
            # if u get a timer
            print(f"\r[$] Message's sent to {user}: {COUNTER}", end="")
            if resp.status_code != 200:
                trigger_cooldown()
        except Exception as e:
            print(f"\n[!] Error: {e}")

        time.sleep(0.8)

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
    
    print(f"[*] All threads were killed gracefully")

if __name__ == "__main__":
    main()
