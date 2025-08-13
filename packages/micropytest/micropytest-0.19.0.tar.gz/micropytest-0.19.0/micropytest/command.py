import subprocess
import threading
import os
import time
from typing import List, Dict, Optional, Callable, Union
import psutil

class Command:
    """
    A simple command executor with stdout/stderr callbacks and output collection.
    """

    def __init__(
        self,
        cmd: Union[str, List[str]],
        cwd: Optional[str] = None,
        env: Optional[Dict[str, str]] = None,
        stdout_callback: Optional[Callable] = None,  # only used with context manager
        stderr_callback: Optional[Callable] = None,  # only used with context manager
        timeout: Optional[float] = None,             # only used with context manager
    ):
        self.cmd = cmd
        self.cwd = cwd
        self.env = env or os.environ.copy()
        self.process = None
        self.stdout_callback = stdout_callback
        self.stderr_callback = stderr_callback
        self.timeout = timeout
        self._stdout_thread = None
        self._stderr_thread = None
        self.stdout_lines = []
        self.stderr_lines = []

    def _read_stream(self, stream, callback, output_list):
        """Read from stream, store lines, and call callback for each line."""
        for line in iter(stream.readline, b''):
            line_str = line.decode('utf-8', errors='replace').rstrip()
            output_list.append(line_str)
            if callback:
                callback(line_str)
        stream.close()

    def run(self, stdout_callback: Optional[Callable[[str], None]] = None, 
            stderr_callback: Optional[Callable[[str], None]] = None):
        """
        Start the command with the given callbacks.

        Args:
            stdout_callback: Function called for each line of stdout
            stderr_callback: Function called for each line of stderr
        """
        self.stdout_lines = []
        self.stderr_lines = []

        self.process = subprocess.Popen(
            self.cmd,
            cwd=self.cwd,
            env=self.env,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            stdin=subprocess.PIPE,
            bufsize=0,
            universal_newlines=False
        )

        self._stdout_thread = threading.Thread(
            target=self._read_stream,
            args=(self.process.stdout, stdout_callback, self.stdout_lines)
        )
        self._stdout_thread.daemon = True
        self._stdout_thread.start()

        self._stderr_thread = threading.Thread(
            target=self._read_stream,
            args=(self.process.stderr, stderr_callback, self.stderr_lines)
        )
        self._stderr_thread.daemon = True
        self._stderr_thread.start()
        
        return self

    def write(self, data: str):
        """Write to the process's stdin."""
        if not self.process:
            raise RuntimeError("Process not started")
        self.process.stdin.write(data.encode('utf-8'))
        self.process.stdin.flush()

    def get_stdout(self):
        """Get all stdout lines collected so far."""
        return self.stdout_lines.copy()

    def get_stderr(self):
        """Get all stderr lines collected so far."""
        return self.stderr_lines.copy()

    def terminate(self):
        """Terminate the process."""
        if self.process and self.process.poll() is None:
            self._terminate_children()
            self.process.terminate()
            try:
                self.process.wait(timeout=2)
            except subprocess.TimeoutExpired:
                self.process.kill()

    def _terminate_children(self):
        """Terminate all child processes."""
        parent = psutil.Process(self.process.pid)
        children = parent.children(recursive=True)
        for child in children:
            child.kill()

    def wait(self, timeout=None):
        """Wait for the process to complete and return exit code."""
        if not self.process:
            raise RuntimeError("Process not started")
        try:
            code = self._wait_internal(timeout=timeout)
        except BaseException as e:
            self.terminate()
            raise e
        finally:
            # Wait for the threads to finish reading the streams
            self._stdout_thread.join()
            self._stderr_thread.join()
        return code

    def _wait_internal(self, timeout=None):
        """Implementation of wait that uses non-blocking calls to be responsive to KeyboardInterrupt."""
        if self.process.returncode is not None:
            return self.process.returncode
        if timeout is not None:
            endtime = time.monotonic() + timeout
        else:
            endtime = None
        while self.process.poll() is None:
            time.sleep(0.5)
            if endtime is not None and time.monotonic() > endtime:
                raise subprocess.TimeoutExpired(self.process.args, timeout)
        return self.process.returncode

    def __enter__(self):
        if not self.process:
            self.run(stdout_callback=self.stdout_callback, stderr_callback=self.stderr_callback)
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is None:
            self.wait(timeout=self.timeout)
        else:
            self.terminate()
            self._stdout_thread.join()
            self._stderr_thread.join()


# Simple helper for use with microPyTest
def run_command(ctx, cmd, **kwargs):
    """Run a command with stdout/stderr logged to the test context."""
    command = Command(cmd, **kwargs)
    return command.run(
        stdout_callback=lambda line: ctx.debug(f"[stdout] {line}"),
        stderr_callback=lambda line: ctx.debug(f"[stderr] {line}")
    )
