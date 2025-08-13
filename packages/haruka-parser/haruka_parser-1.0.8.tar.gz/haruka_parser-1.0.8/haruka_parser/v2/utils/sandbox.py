import platform
import time
import json
import traceback
from multiprocessing import Pipe, Process
from haruka_parser.v2.extractors.auto_extractor import AutoExtractor

class Sandbox:
    def __init__(self, timeout):
        self.timeout = timeout
        self.process = None
        self.parent_conn = None
        self.child_conn = None

    def _cleanup_process(self):
        if self.process is not None:
            self.parent_conn.close()
            self.child_conn.close()
            self.process.terminate()
            self.process.join(timeout=0.1)  # small clean up window
            if self.process.is_alive():
                self.process.kill()
            self.process = None
            self.parent_conn = None
            self.child_conn = None

    def _set_oom_score_adj(self, score):
        # Only for linux
        if platform.system() == "Linux":
            if not -1000 <= score <= 1000:
                raise ValueError("Score must be between -1000 and +1000")
            with open("/proc/self/oom_score_adj", "w") as f:
                f.write(f"{score}\n")

    def _worker(self, conn, extract_fn):
        # Ensure that the child process is killed first on oom
        self._set_oom_score_adj(1000)

        extractor = AutoExtractor()

        conn.send(None)  # ready
        while True:
            try:
                text = conn.recv()
                data = json.loads(text)
                try:
                    output = extractor.extract(**data)
                except:
                    output = {"error": traceback.format_exc()}
                conn.send(json.dumps(output, ensure_ascii=False))
            except EOFError:
                break

    def process_document(self, text, extract_fn):
        self._ensure_process(extract_fn)
        try:
            self.parent_conn.send(text)

            deadline = time.monotonic() + self.timeout
            # loop with short sleeps instead of one big poll()
            while True:
                # 5 seconds is small enough not to take cpu time too much but not big enough so that we return quikly
                # on child process death, so that we indeed after the return (not sure if needed)
                poll_timeout = max(0, min(5, deadline - time.monotonic() + 0.1))
                if self.parent_conn.poll(poll_timeout):
                    result = self.parent_conn.recv()
                    if isinstance(result, Exception):
                        raise result
                    return result

                # 2) Has the child died?
                if not self.process.is_alive():
                    self._cleanup_process()
                    raise EOFError("Child process died (likely OOM-killed)")

                # 3) Has our deadline passed?
                if time.monotonic() >= deadline:
                    self._cleanup_process()
                    raise TimeoutError("Document extraction timed out")
        except (TimeoutError, EOFError):
            self._cleanup_process()
            raise

    def _ensure_process(self, extract_fn):
        if self.process is None or not self.process.is_alive():
            if self.process is not None:
                self._cleanup_process()

            self.parent_conn, self.child_conn = Pipe()
            self.process = Process(target=self._worker, args=(self.child_conn, extract_fn))
            self.process.start()
            self.parent_conn.recv()

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self._cleanup_process()
        return False