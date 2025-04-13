import os
import sys
import signal
import queue
import threading
from io import BytesIO
from urllib.parse import urlparse

import requests
from ds_store import DSStore


class Color:
    OK = '\033[92m'
    INFO = '\033[96m'
    WARN = '\033[93m'
    FAIL = '\033[91m'
    END = '\033[0m'


class DSStoreWorker:
    def __init__(self, target_url, output_base='output'):
        self.url_queue = queue.Queue()
        self.url_queue.put(target_url)
        self.visited = set()
        self.mutex = threading.Lock()
        self.active_threads = 0
        self.stop_flag = threading.Event()
        self.output_base = os.path.abspath(output_base)
        os.makedirs(self.output_base, exist_ok=True)

    def run(self):
        threads = []
        for _ in range(10):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
            threads.append(t)

        try:
            for t in threads:
                t.join()
        except KeyboardInterrupt:
            self.stop_flag.set()
            print(f"\n{Color.INFO}🛑 Interrupted. Exiting cleanly...{Color.END}")

    def _worker(self):
        while not self.stop_flag.is_set():
            try:
                url = self.url_queue.get(timeout=1)
                with self.mutex:
                    self.active_threads += 1
            except queue.Empty:
                if self.active_threads == 0:
                    break
                continue

            try:
                if url in self.visited:
                    continue
                self.visited.add(url)

                if not url.startswith('http'):
                    url = 'http://' + url

                response = requests.get(url, timeout=10, allow_redirects=False)
                if response.status_code != 200:
                    self._log(f"⚠️ [{response.status_code}] Skipped: {url}", Color.WARN)
                    continue

                self._save_response(url, response.content)

                if url.endswith('.DS_Store'):
                    self._parse_ds_store(url, response.content)

                self._log(f"✅ [{response.status_code}] Downloaded: {url}", Color.OK)

            except Exception as err:
                self._log(f"❌ [ERROR] {err}", Color.FAIL)
            finally:
                with self.mutex:
                    self.active_threads -= 1

    def _parse_ds_store(self, base_url, content):
        try:
            stream = BytesIO(content)
            ds = DSStore.open(stream)
            base = base_url.rstrip('.DS_Store')
            found = set()

            for record in ds._traverse(None):
                if self._valid_name(record.filename):
                    found.add(record.filename)

            for item in found:
                if item == '.':
                    continue
                self.url_queue.put(base + item)
                if '.' not in item or not item.split('.')[-1]:
                    self.url_queue.put(base + item + '/.DS_Store')

            ds.close()

        except Exception as e:
            self._log(f"🧠 [PARSE FAIL] {e}", Color.FAIL)

    def _save_response(self, url, content):
        parsed = urlparse(url)
        domain_folder = parsed.netloc.replace(':', '_')
        base_path = os.path.dirname(parsed.path)
        full_dir = os.path.join(self.output_base, domain_folder, base_path.lstrip('/'))
        os.makedirs(full_dir, exist_ok=True)

        filename = os.path.basename(parsed.path)
        if not filename:
            filename = 'index.html'
        filepath = os.path.join(full_dir, filename)

        with open(filepath, 'wb') as f:
            f.write(content)

    def _valid_name(self, name):
        full_path = os.path.abspath(name)
        if '..' in name or name.startswith('/') or name.startswith('\\'):
            return False
        if not full_path.startswith(os.getcwd()):
            return False
        return True

    def _log(self, message, color=Color.INFO):
        print(f"{color}{message}{Color.END}")


def signal_handler(sig, frame):
    print(f"\n{Color.INFO}🛑 Interrupted. Exiting...{Color.END}")
    sys.exit(0)


def main():
    signal.signal(signal.SIGINT, signal_handler)

    if len(sys.argv) != 2:
        print(f"{Color.INFO}📘 Made by IndonesiaCodeParty{Color.END}")
        print(f"{Color.INFO}📘 Usage: python {sys.argv[0]} https://target.com/.DS_Store{Color.END}")
        sys.exit(1)

    input_url = sys.argv[1]
    runner = DSStoreWorker(input_url)
    runner.run()


if __name__ == '__main__':
    main()
