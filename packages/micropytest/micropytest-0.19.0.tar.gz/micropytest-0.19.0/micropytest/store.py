"""Interface for storing test results on a remote server implementing the MicroPyTest Store REST API."""
from typing import Optional, Union
from dataclasses import dataclass
from datetime import datetime, timezone
import os
import sys
import subprocess
import logging
import json
from pydantic import BaseModel, JsonValue, Base64Bytes, Field
from typing import Literal, Annotated, Any
import threading
import _thread
from time import sleep
import requests
from requests.exceptions import HTTPError
from .types import Test, Args, TestResult, TestAttributes
from .core import SkipTest, load_test_module_by_path, TestContext, format_exception
from .vcs_helper import VCSHelper
from .types import TestStatus

ArtifactValue = Union[JsonValue, bytes]
TestRunStatus = Literal["pass", "fail", "skip", "queued", "running", "cancelled"]
LogLevel = Literal["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]


class TestDefinition(BaseModel):
    repository_name: str
    file_path: str
    name: str
    tags: set[str]
    args: str


class TestJobData(BaseModel):
    id: int
    repository_name: str
    commit: str
    branch: str
    platform: str


class NumLogs(BaseModel):
    DEBUG: int
    INFO: int
    WARNING: int
    ERROR: int
    CRITICAL: int


class ArtifactInfo(BaseModel):
    type: Literal["json", "bytes"]
    size: int  # size in bytes for bytes type or -1 for json type


class TestRunData(BaseModel):
    test: TestDefinition
    run_number: int
    run_id: int
    status: TestRunStatus
    exception: Optional[str]
    duration: Optional[float]
    job: TestJobData
    num_logs: NumLogs
    num_artifacts: int
    artifact_keys: Optional[dict[str, ArtifactInfo]]  # None means artifact keys were not requested
    queued_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    finish_reason: Optional[str]


class CreateJobRequestData(BaseModel):
    repository_name: str
    commit: str
    branch: str
    platform: str


class CreateJobResponseData(BaseModel):
    job_id: int


class EnqueueRequestData(BaseModel):
    test: TestDefinition
    job_id: int


class EnqueueResponseData(BaseModel):
    run_number: int
    run_id: int


class StartRequestData(BaseModel):
    job_id: int


class StartResponseData(BaseModel):
    test_run: Optional[TestRunData]


class TypedJson(BaseModel):
    type: Literal["json"]
    value: JsonValue

    @staticmethod
    def wrap(value: JsonValue) -> "TypedJson":
        return TypedJson(type="json", value=value)

    def unwrap(self) -> JsonValue:
        return self.value


class TypedBytes(BaseModel):
    type: Literal["bytes"]
    value: Base64Bytes

    @staticmethod
    def wrap(value: bytes) -> "TypedBytes":
        if not isinstance(value, bytes):
            raise ValueError("value must be bytes")
        t = TypedBytes(type="bytes", value=b"")
        t.value = value
        return t

    def unwrap(self) -> bytes:
        return self.value


JsonOrBytes = Annotated[Union[TypedJson, TypedBytes], Field(discriminator="type")]


class AddArtifactRequestData(BaseModel):
    key: str
    value: JsonOrBytes


class LogEntry(BaseModel):
    time: datetime
    level: LogLevel
    message: str

    @staticmethod
    def from_record(record: logging.LogRecord) -> "LogEntry":
        return LogEntry(
            time=datetime.fromtimestamp(record.created, tz=timezone.utc),
            level=record.levelname,
            message=record.getMessage(),
        )


class AddLogsRequestData(BaseModel):
    logs: list[LogEntry]


class RunningAliveResponseData(BaseModel):
    cancel: bool  # test was cancelled on the server and should be stopped on runner


class FinishTestRequestData(BaseModel):
    status: TestStatus
    exception: Optional[str]
    duration: float
    finish_reason: str


class CancelTestRequestData(BaseModel):
    cancel: bool


class GetTestRunsRequestData(BaseModel):
    test: TestDefinition
    min: Annotated[int, Field(ge=0)]
    max: Optional[Annotated[int, Field(ge=0)]]
    limit: Annotated[int, Field(ge=0, le=100)]
    order: Literal[1, -1]
    status: list[str]
    job: list[int]
    branch: list[str]
    platform: list[str]
    commit: list[str]
    artifact_keys: bool


class GetTestRunsResponseData(BaseModel):
    test_runs: list[TestRunData]


class GetArtifactsRequestData(BaseModel):
    keys: list[str]


class GetArtifactsResponseData(BaseModel):
    artifacts: dict[str, JsonOrBytes]


class GetLogsRequestData(BaseModel):
    levels: list[LogLevel]


class GetLogsResponseData(BaseModel):
    logs: list[LogEntry]


class GetTestsRequestData(BaseModel):
    repository_name: str
    file_path: str
    name: str


class GetTestsResponseData(BaseModel):
    test_definitions: list[TestDefinition]


class ErrorData(BaseModel):
    type: str
    message: str
    traceback: list[str]


class ErrorResponseData(BaseModel):
    error: ErrorData


@dataclass
class TestRun:
    # Note: this differs from the TestRunData class only in the data type of the test field
    test: Test
    run_number: int
    run_id: int
    status: TestRunStatus
    exception: Optional[str]
    duration: Optional[float]
    job: TestJobData
    num_logs: NumLogs
    num_artifacts: int
    artifact_keys: Optional[dict[str, ArtifactInfo]]  # None means artifact keys were not requested
    queued_at: datetime
    started_at: Optional[datetime]
    finished_at: Optional[datetime]
    finish_reason: Optional[str]


@dataclass
class LocalRepository:
    """A local version control repository."""
    name: str
    commit: str
    branch: str
    root_path: str  # local path to the repository root directory

    @staticmethod
    def get(name: Optional[str] = None, path: str = ".") -> "LocalRepository":
        """Get the current repository."""
        path = os.path.abspath(path)
        vcs = VCSHelper().get_vcs_handler(path)
        repo_root = os.path.abspath(vcs.get_repo_root(path))
        if name is None:
            name = os.path.basename(repo_root)
        return LocalRepository(
            name=name,
            commit=vcs.get_last_commit(repo_root).revision,
            branch=vcs.get_branch(repo_root),
            root_path=repo_root,
        )

    def relative_path(self, path: str) -> str:
        """Get relative path with respect to the repository root path."""
        return os.path.relpath(os.path.abspath(path), os.path.abspath(self.root_path)).replace('\\', '/')

    def test_path(self, relative_path: str) -> str:
        """Get path relative to the current working directory (as stored in Test)."""
        return os.path.relpath(os.path.abspath(os.path.join(self.root_path, relative_path)), os.getcwd())


class TestStore:
    def __init__(self,
        url: str,
        headers: Optional[dict[str, str]] = None,
        repository: Optional[LocalRepository] = None,
        platform: Optional[str] = None,
        job: Optional[int] = None,
        timeout: float = 10.0,
    ):
        self.url: str = url
        self.headers: dict[str, str] = headers or {}
        self.repository: LocalRepository = repository or LocalRepository.get()
        self.platform: str = platform or get_current_platform()
        self.job: Optional[int] = job  # job ID for the set of tests to be run
        self.timeout: float = timeout
        self._test_alive_daemon = TestAliveDaemon(url, headers)
        self._session = requests.Session()
        self._session_lock = threading.Lock()
        self._artifact_transmitter = AsyncArtifactTransmitter(self, transmit_interval=0.0)
        self._log_transmitter = AsyncLogTransmitter(self, transmit_interval=5.0)
        self._disable_request_logging()

    def test_definition(self, test: Test) -> TestDefinition:
        return TestDefinition(
            repository_name=self.repository.name,
            file_path=self.repository.relative_path(test.file),
            name=test.name,
            tags=test.tags,
            args=test.args.to_json(),
        )

    def to_test(self, test_definition: TestDefinition) -> Test:
        file = self.repository.test_path(test_definition.file_path)
        mod = load_test_module_by_path(file)
        return Test(
            file=file,
            name=test_definition.name,
            function=getattr(mod, test_definition.name),
            tags=test_definition.tags,
            args=Args.from_json(test_definition.args),
        )

    def to_test_run(self, test_run_data: TestRunData) -> TestRun:
        return TestRun(
            test=self.to_test(test_run_data.test),
            run_number=test_run_data.run_number,
            run_id=test_run_data.run_id,
            status=test_run_data.status,
            exception=test_run_data.exception,
            duration=test_run_data.duration,
            job=test_run_data.job,
            num_logs=test_run_data.num_logs,
            num_artifacts=test_run_data.num_artifacts,
            artifact_keys=test_run_data.artifact_keys,
            queued_at=test_run_data.queued_at,
            started_at=test_run_data.started_at,
            finished_at=test_run_data.finished_at,
            finish_reason=test_run_data.finish_reason,
        )

    def create_job(self) -> int:
        """Create a new job for the set of tests to be run using this TestStore instance."""
        url = f"{self.url}/jobs"
        d = CreateJobRequestData(
            repository_name=self.repository.name,
            commit=self.repository.commit,
            branch=self.repository.branch,
            platform=self.platform,
        )
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        return CreateJobResponseData.model_validate(response.json()).job_id

    def enqueue_test(self, test: Test) -> EnqueueResponseData:
        """Add a test to the queue to be run later."""
        if self.job is None:
            self.job = self.create_job()
        d = EnqueueRequestData(
            test=self.test_definition(test),
            job_id=self.job,
        )
        url = f"{self.url}/enqueue"
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        return EnqueueResponseData.model_validate(response.json())

    def start_test(self) -> Optional[TestRun]:
        """Get the next test from the queue to start execution (or None if there are no more tests to run)."""
        # gets the next test matching the store's test job in the order of enqueueing
        url = f"{self.url}/start"
        d = StartRequestData(job_id=self.job)
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        response_data = StartResponseData.model_validate(response.json())
        if response_data.test_run is None:
            return None
        return self.to_test_run(response_data.test_run)

    def add_artifact(self, run_id: int, key: str, value: ArtifactValue):
        """Add an artifact to a running test."""
        # This can be called by the TestContext
        url = f"{self.url}/runs/{run_id}/artifacts/add"
        d = AddArtifactRequestData(
            key=key,
            value=TypedBytes.wrap(value) if isinstance(value, bytes) else TypedJson.wrap(value),
        )
        response = self._post(url, d)
        self._raise_for_status(response, url)

    def add_logs(self, run_id: int, logs: list[logging.LogRecord]) -> None:
        """Add logs to a running test."""
        # This can be called by the TestContext
        url = f"{self.url}/runs/{run_id}/logs/add"
        d = AddLogsRequestData(
            logs=[LogEntry.from_record(record) for record in logs],
        )
        response = self._post(url, json=d)
        self._raise_for_status(response, url)

    def push_artifact(self, run_id: int, key: str, value: ArtifactValue):
        """Push an artifact to be transmitted asynchronously."""
        self._artifact_transmitter.push(run_id, (key, value))

    def push_log(self, run_id: int, log: logging.LogRecord):
        """Push a log to be transmitted asynchronously."""
        self._log_transmitter.push(run_id, log)

    def finish_logs_and_artifacts(self) -> None:
        """Finish transmitting logs and artifacts (blocks until transmission is complete)."""
        transmit_error = None
        try:
            self._artifact_transmitter.finish()
        except Exception as e:
            transmit_error = RuntimeError(f"Error while finishing: during add_artifact: {e.__class__.__name__}: {e}")
        try:
            self._log_transmitter.finish()
        except Exception as e:
            transmit_error = RuntimeError(f"Error while finishing: during add_logs: {e.__class__.__name__}: {e}")
        if transmit_error is not None:
            raise transmit_error

    def finish_test(self, run_id: int, result: TestResult) -> None:
        """Finish a test run, reporting the result.

        This does not include artifacts and logs, which are reported separately during the test is running.
        """
        d = FinishTestRequestData(
            status=result.status,
            exception=format_exception(result.exception) if result.exception is not None else None,
            duration=result.duration_s,
            finish_reason=_to_finish_reason(result.exception),
        )
        url = f"{self.url}/runs/{run_id}/finish"
        response = self._put(url, json=d)
        self._raise_for_status(response, url)

    def cancel_test(self, run_id: int) -> None:
        """Cancel a test run."""
        url = f"{self.url}/runs/{run_id}/cancel"
        d = CancelTestRequestData(cancel=True)
        response = self._put(url, json=d)
        self._raise_for_status(response, url)

    def cancel_all(self) -> None:
        """Cancel all test runs in the current job."""
        if self.job is None:
            raise ValueError("No job set")
        url = f"{self.url}/jobs/{self.job}/cancel"
        d = CancelTestRequestData(cancel=True)
        response = self._put(url, json=d)
        self._raise_for_status(response, url)

    def get_test_runs(
        self,
        test: Test,
        num: Optional[int] = None,  # run number
        min: int = 0,  # minimum run number
        max: Optional[int] = None,  # maximum run number
        limit: int = 100,
        order: Literal[1, -1] = 1,  # 1 for ascending, -1 for descending (by run number)
        status: Optional[Union[str, list[str]]] = None,
        job: Optional[Union[int, list[int]]] = None,
        branch: Optional[Union[str, list[str]]] = None,
        platform: Optional[Union[str, list[str]]] = None,
        commit: Optional[Union[str, list[str]]] = None,
        artifact_keys: bool = False  # request to include artifact keys in response
    ) -> list[TestRun]:
        """Get test runs from the server.
        
        Parameters status, job, branch, platform and commit are used to filter test runs. If multiple values
        are provided for a parameter the test run must match at least one of them. Empty list means no
        filtering for that parameter. None means filter by default values. Default values are:
        - status: ["pass", "fail"]
        - job: self.job if set, otherwise no filtering
        - branch: self.repository.branch
        - platform: self.platform
        - commit: no filtering

        Parameters num (exact value), min (run number >= min) and max (run number <= max) refer to the run number.

        Result is ordered by run number, either ascending (1) or descending (-1), according to the order parameter.
        """

        if num is not None:
            min = num
            max = num

        d = GetTestRunsRequestData(
            test=self.test_definition(test),
            min=min,
            max=max,
            limit=limit,
            order=order,
            status=_to_list(status, ["pass", "fail"]),
            job=_to_list(job, [self.job] if self.job is not None else []),
            branch=_to_list(branch, [self.repository.branch]),
            platform=_to_list(platform, [self.platform]),
            commit=_to_list(commit, []),
            artifact_keys=artifact_keys,
        )
        url = f"{self.url}/runs/get"
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        response_data = GetTestRunsResponseData.model_validate(response.json())
        return [self.to_test_run(run) for run in response_data.test_runs]

    def get_last_test_run(
        self,
        test: Test,
        status: Optional[Union[str, list[str]]] = None,
        artifact_keys: bool = False,
    ) -> Optional[TestRun]:
        """Return the last test run for a test, optionally filtered by status, for this branch and platform (and
        job if self.job is set), or None if no matching run exists."""
        runs = self.get_test_runs(test, order=-1, limit=1, status=status, artifact_keys=artifact_keys)
        if len(runs) == 0:
            return None
        return runs[0]

    def get_artifacts(self, run_id: int, key: Optional[Union[str, list[str]]] = None) -> dict[str, ArtifactValue]:
        """Get artifacts of a test run.

        If key is None or an empty list, all artifacts are returned.
        """
        keys = _to_list(key, [])
        d = GetArtifactsRequestData(keys=keys)
        url = f"{self.url}/runs/{run_id}/artifacts/get"
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        response_data = GetArtifactsResponseData.model_validate(response.json())
        return {key: value.unwrap() for key, value in response_data.artifacts.items()}

    def get_logs(self, run_id: int, level: Optional[Union[LogLevel, list[LogLevel]]] = None) -> list[LogEntry]:
        """Get logs of a test run.

        If level is None or an empty list, all logs are returned.
        """
        levels = _to_list(level, [])
        d = GetLogsRequestData(levels=levels)
        url = f"{self.url}/runs/{run_id}/logs/get"
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        response_data = GetLogsResponseData.model_validate(response.json())
        return response_data.logs

    def get_tests(self, test_attributes: TestAttributes) -> list[Test]:
        """Get tests (including arguments) for a given TestAttributes (ignoring tags)."""
        d = GetTestsRequestData(
            repository_name=self.repository.name,
            file_path=self.repository.relative_path(test_attributes.file),
            name=test_attributes.name,
        )
        url = f"{self.url}/tests/get"
        response = self._post(url, json=d)
        self._raise_for_status(response, url)
        response_data = GetTestsResponseData.model_validate(response.json())
        return [self.to_test(td) for td in response_data.test_definitions]

    def _request(self, method: str, url: str, json: Optional[BaseModel] = None) -> requests.Response:
        json_data = dump_json(json) if json is not None else None
        with self._session_lock:
            res = self._session.request(method, url, json=json_data, headers=self.headers, timeout=self.timeout)
        return res

    def _post(self, url: str, json: Optional[BaseModel] = None) -> requests.Response:
        return self._request("POST", url, json=json)

    def _put(self, url: str, json: Optional[BaseModel] = None) -> requests.Response:
        return self._request("PUT", url, json=json)

    def _get(self, url: str) -> requests.Response:
        return self._request("GET", url, json=None)

    def _raise_for_status(self, response: requests.Response, url: str):
        if not response.ok:
            try:
                error_data = ErrorResponseData.model_validate(response.json())
            except Exception:
                error_data = None
            msg = f"HTTP error (status code {response.status_code} for {response.request.method} {url}):\n"
            if error_data is None:
                msg += f"- Response text: {response.text}"
            else:
                info = error_data.error
                msg += "\n".join([
                    f"- Type: {info.type}",
                    f"- Message: {info.message}",
                ])
                if len(info.traceback) > 0:
                    msg += "\n" + "\n".join([
                        f"- Traceback:",
                        *(f"  - {line}" for line in info.traceback),
                    ])
            raise HTTPError(msg, response=response)

    def _disable_request_logging(self):
        # Disable logging for the requests and urllib3 libraries, as this might cause infinite recursion
        # (because every log triggers a request and every request might trigger additional logs)
        loggers = [logging.getLogger()] + [logging.getLogger(name) for name in logging.root.manager.loggerDict]
        for logger in loggers:
            if logger.name.startswith("urllib3") or logger.name.startswith("requests"):
                logger.setLevel(logging.CRITICAL + 1)


class AsyncTransmitter:
    """Transmits items to the server asynchronously."""
    def __init__(self, store: 'TestStore', transmit_interval: float = 5.0):
        self._store: TestStore = store
        self._transmit_interval = transmit_interval
        self._pending_items: list[Any] = []
        self._lock = threading.Lock()
        self._current_run_id: Optional[int] = None
        self._finish = False
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()
        self._error = None  # error that occurred in the thread

    def push(self, run_id: int, item: Any):
        """Push an item to be transmitted (non-blocking call that returns immediately)."""
        with self._lock:
            if self._is_ready():
                self._current_run_id = run_id
            if self._current_run_id != run_id:
                # We could end up here if a KeyboardInterrupt happened and finish() was not called -> reset silently.
                self._current_run_id = run_id
                self._pending_items = []
            self._pending_items.append(item)

    def finish(self):
        """Send all pending items to the server (blocks until all items were sent) and finishes current run."""
        with self._lock:
            self._finish = True
        while True:
            with self._lock:
                if self._is_ready():
                    break
            sleep(0.05)
        with self._lock:
            self._finish = False
            e = self._error
            self._error = None
        if e is not None:
            raise e  # re-raise the error that occurred in the thread

    def _is_ready(self) -> bool:
        """Ready to accept items for a new run."""
        return self._current_run_id is None and len(self._pending_items) == 0

    def _run(self):
        slept = 0.0
        sleep_interval = 0.05
        transmit_interval = self._transmit_interval
        while True:
            with self._lock:
                finish = self._finish
            if slept >= transmit_interval or finish:
                slept = 0.0
                with self._lock:
                    current_run_id = self._current_run_id
                    pending_items = self._pending_items.copy()
                    self._pending_items = []
                error = None
                if current_run_id is not None and len(pending_items) > 0:
                    try:
                        self._transmit(current_run_id, pending_items)
                    except Exception as e:
                        error = e
                with self._lock:
                    self._error = error
                    if finish:
                        self._current_run_id = None
            sleep(sleep_interval)
            slept += sleep_interval

    def _transmit(self, run_id: int, items: list[Any]):
        """Transmit items to the server."""
        raise NotImplementedError("Subclass must implement _transmit method")


class AsyncLogTransmitter(AsyncTransmitter):
    """Transmits logs to the server asynchronously."""
    def _transmit(self, run_id: int, items: list[logging.LogRecord]):
        max_items = 1000
        for i in range(0, len(items), max_items):
            items_batch = items[i:i+max_items]
            self._store.add_logs(run_id, items_batch)


class AsyncArtifactTransmitter(AsyncTransmitter):
    """Transmits artifacts to the server asynchronously."""
    def _transmit(self, run_id: int, items: list[tuple[str, ArtifactValue]]):
        for key, value in items:
            self._store.add_artifact(run_id, key, value)


class TestContextStored(TestContext):
    """A test context that stores artifacts and logs in the test store."""
    def __init__(self, store: TestStore, run_id: Optional[int] = None):
        super().__init__()
        self.store: TestStore = store
        self.run_id: int = run_id

    def add_artifact(self, key: str, value: Any):
        super().add_artifact(key, value)
        self.store.push_artifact(self.run_id, key, value)

    def add_log(self, record: logging.LogRecord):
        super().add_log(record)
        self.store.push_log(self.run_id, record)

    def finish(self):
        super().finish()
        self.store.finish_logs_and_artifacts()


def _to_list(value, default):
    if value is None:
        value = default
    if isinstance(value, str):
        value = [value]
    return value


def _to_finish_reason(exception: Optional[Exception]) -> str:
    if exception is None:
        finish_reason = "finished normally"
    else:
        if isinstance(exception, SkipTest):
            finish_reason = f"skipped: {exception}"
        else:
            exception_type = exception.__class__.__name__
            finish_reason = f" finished with exception: {exception_type}: {exception}"
    return finish_reason


def get_current_platform() -> Literal["windows", "linux", "macos"]:
    """Get the current platform."""
    platform = sys.platform
    if platform.startswith("win"):
        return "windows"
    elif platform.startswith("linux"):
        return "linux"
    elif platform.startswith("darwin"):  # macOS
        return "macos"
    else:
        raise ValueError(f"Unknown platform: {platform}")


class KeepAlive:
    def __init__(self, store: TestStore, run_id: int):
        self.store = store
        self.run_id = run_id

    def __enter__(self):
        # report to daemon that test run id is running
        self.store._test_alive_daemon.start(self.run_id)

    def __exit__(self, exc_type, exc_value, traceback):
        # report to daemon that test run id is finished
        self.store._test_alive_daemon.stop()


class TestAliveDaemon:
    """Persistent subprocess that sends keep-alive messages to the server periodically.
    The subprocess is terminated when the TestStore object goes out of scope.
    """
    def __init__(self, api_endpoint, headers):
        daemon_file = os.path.join(os.path.dirname(__file__), "utils", "daemon.py")
        env = os.environ.copy()
        env["HTTP_HEADERS"] = json.dumps(headers)
        self.proc = subprocess.Popen(
            [sys.executable, daemon_file, api_endpoint],
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.DEVNULL,
            bufsize=1,
            universal_newlines=True,
            env=env,
        )
        self.thread = threading.Thread(target=self._read_child_output, daemon=True)
        self.thread.start()

    def _read_child_output(self):
        """Monitor child's stdout for cancel signal"""
        for line in self.proc.stdout:
            line = line.strip()
            if line == "cancel":
                # Trigger KeyboardInterrupt in main thread
                _thread.interrupt_main()

    def _write(self, line: str):
        if self.proc.poll() is not None:
            raise RuntimeError("Keep-alive daemon process is not running")
        self.proc.stdin.write(line)
        self.proc.stdin.flush()

    def start(self, run_id: int):
        self._write(f"start {run_id}\n")

    def stop(self):
        self._write("stop\n")

    def close(self):
        # closing stdin will cause the child process to exit
        self.proc.stdin.close()
        self.proc.wait()  # wait for child to actually exit
        self.thread.join()

    def __del__(self):
        self.close()


def dump_json(obj: BaseModel) -> Any:
    """Helper to dump JSON-compatible data."""
    return obj.model_dump(mode="json")
