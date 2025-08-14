from datetime import datetime, timedelta
from pathlib import Path
import time
import threading
from typing import Dict
from pam.utils import log
from pam.api import API
from pam.service import Service
from pam.models.request_command import RequestCommand
from pam.interface_task_manager import ITaskManager
from pam.temp_file_utils import TempfileUtils

class ServiceHolder:
    def __init__(self, service: Service):
        self.service = service
        self.last_activity = datetime.now()

    def update_timestamp(self):
        self.last_activity = datetime.now()

    def has_timed_out(self, timeout=2):
        """Check if the service has been inactive longer than the timeout (in hours)."""
        return datetime.now() - self.last_activity > timedelta(hours=timeout)


class TaskManager(ITaskManager):
    """
    Manages service threads.
    """

    def __init__(self, server, monitoring_interval=600, timeout=2):
        self.services: Dict[str, ServiceHolder] = {}
        self.api = API()
        self.server = server
        self.thread_lock = threading.Lock()
        self.monitoring_interval = monitoring_interval
        self.timeout = timeout
        self.stop_event = threading.Event()

    # ==== Service Management ====
    def _add_service(self, token, service):
        with self.thread_lock:
            self.services[token] = ServiceHolder(service)

    def _get_service_holder(self, token):
        with self.thread_lock:
            return self.services.get(token)

    def _update_service(self, token):
        with self.thread_lock:
            if token in self.services:
                self.services[token].update_timestamp()

    def _check_timeout(self, token):
        with self.thread_lock:
            if token in self.services:
                return self.services[token].has_timed_out(self.timeout)
        return False

    def _remove_service(self, token):
        with self.thread_lock:
            if token in self.services:
                service_holder = self.services[token]
                log(f"Service Exit: {service_holder.service.request.service_name}, {service_holder.service.request.token}")
                service_holder.service.on_destroy()
                del self.services[token]

    # ==== Monitoring ====
    def start_service_monitoring_schedul(self):
        """
        Starts the service monitoring thread.
        """
        self.stop_event.clear()
        schedule_thread = threading.Thread(
            target=self._monitor_services, args=(self.monitoring_interval, self.stop_event)
        )
        schedule_thread.daemon = True
        schedule_thread.start()

    def stop_service_monitoring(self):
        """
        Stops the service monitoring thread.
        """
        self.stop_event.set()

    def _monitor_services(self, interval, stop_event):
        """
        Periodically checks for services that have timed out.
        """
        while not stop_event.is_set():
            time.sleep(interval)
            log("Service Monitor running.")
            tokens_to_remove = [
                token for token in self.services if self._check_timeout(token)
            ]
            log(f"Found: {len(tokens_to_remove)} services timed out.")
            for token in tokens_to_remove:
                log(f"Service {token} has timed out. Removing...")
                self._remove_service(token)

    # ==== Command Handlers ====
    def on_dataset_input(self, req: RequestCommand):
        """
        Handles cmd=dataset for an existing service.
        """
        service_holder = self._get_service_holder(req.token)
        if service_holder is not None:
            service_holder.update_timestamp()
            service_holder.service.on_data_input(req)

    def start_service(self, service_class, req: RequestCommand, service_name):
        """
        Starts a new service.
        """
        log(f"Start Service: {service_name}, Token: {req.token}")
        service_instance = service_class(self, req)
        service_instance.on_start()
        self._add_service(req.token, service_instance)

    def terminate_service(self, token):
        """
        Terminates a service by token.
        """
        service_holder = self._get_service_holder(token)
        if service_holder is not None:
            service_holder.service.on_terminate()
            self._remove_service(token)

    # ==== Service Callbacks ====
    def service_request_data(self, service: Service, page):
        """
        Makes an asynchronous request for data from a service.
        Logs the response without blocking the main thread.
        """
        endpoint = service.request.data_api
        token = service.request.token
        json_data = {"page": page, "token": token}

        def handle_response(response):
            """Logs the response from the API."""
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            log(f"Response from {endpoint}: {response_data}")

        def api_call_wrapper():
            """Wrapper for the API call to handle response."""
            response = self.api.http_post(endpoint, json_data)
            handle_response(response)

        log(f"Requesting Data from: {endpoint}, page: {page}, token={token}")
        http_thread = threading.Thread(target=api_call_wrapper)
        http_thread.start()

    def service_request_sqlite(self, service: Service, file_name="", is_shared=False):
        """Requests last sqlite file that this plugin has uploaded from the last time.
        Returns:
            The file path to the downloaded SQLite file, or None if the download failed.
        """
    
        log(f"{service.request.service_name}: Requesting sqlite for file_name={file_name}")
        
        endpoint = service.request.sqlite_download
        token = service.request.token
        json_data = {"file_name": file_name, "is_shared": is_shared, "token": token}

        # Create a unique suffix using current datetime
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        unique_file_name = f"{file_name or 'latest'}_{timestamp}"

        # Create a temp file path for the downloaded .sqlite file
        output_path = TempfileUtils.get_temp_file_name(
            service.request.service_name,
            token,
            f"sqlite_{unique_file_name}_",
            ".sqlite"
        )

        # Download SQLite file
        success = self.api.download_sqlite_from_post(endpoint, json_data, output_path)

        if success:
            log(f"{service.request.service_name}: Successfully downloaded SQLite file to {output_path}")
            return output_path
        else:
            log(f"{service.request.service_name}: Failed to download SQLite file.")
            return output_path

    def service_upload_sqlite(self, service: Service, file_name: str = "", is_shared: bool = False, sqlite_file: str = "") -> str:
        """
        Uploads the result SQLite file to CDP.

        :param file_name: The logical file name being uploaded.
        :param is_shared: Whether this file should be treated as shared.
        :param sqlite_file: Path to the SQLite file to upload.
        :return: The uploaded file name if successful, or empty string if failed.
        """
        if not sqlite_file:
            log(f"{service.request.service_name}: No sqlite file provided for upload.")
            return ""

        if not Path(sqlite_file).is_file():
            log(f"{service.request.service_name}: SQLite file does not exist: {sqlite_file}")
            return ""

        endpoint = service.request.sqlite_upload
        payload = {
            "file_name": file_name,
            "is_shared": str(is_shared).lower(),  # form data values must be string
            "token": service.request.token
        }

        try:
            log(f"{service.request.service_name}: Uploading sqlite file: {sqlite_file} with payload: {payload}")
            response = self.api.http_upload(endpoint, sqlite_file, payload)

            if response and response.ok:
                log(f"{service.request.service_name}: SQLite file uploaded successfully.")
                return file_name or Path(sqlite_file).name
            else:
                log(f"{service.request.service_name}: Failed to upload sqlite. Status: {response.status_code if response else 'N/A'}")
                return ""
        except Exception as e:
            log(f"{service.request.service_name}: Exception while uploading sqlite: {e}")
            return ""

    def service_upload_result(self, service: Service, file_path):
        """
        Uploads a result file asynchronously and logs the response.
        """
        endpoint = service.request.response_api

        def handle_upload_response(response):
            """Logs the response after the upload completes."""
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            log(f"Response from upload to {endpoint}: {response_data}")

        def upload_wrapper():
            """Wrapper for the upload to handle response logging."""
            response = self.api.http_upload(endpoint, file_path)
            handle_upload_response(response)

        log(f"Uploading Result to: {endpoint}")
        http_thread = threading.Thread(target=upload_wrapper)
        http_thread.start()

    def service_upload_report(self, service: Service, file_path):
        """
        Uploads a report file asynchronously and logs the response.
        """
        endpoint = service.request.response_api

        def handle_report_response(response):
            """Logs the response after the report upload completes."""
            try:
                response_data = response.json()
            except ValueError:
                response_data = response.text
            log(f"Response from report upload to {endpoint}: {response_data}")

        def upload_wrapper():
            """Wrapper for the report upload to handle response logging."""
            response = self.api.http_upload(endpoint, file_path)
            handle_report_response(response)

        log(f"Uploading Report to: {endpoint}")
        http_thread = threading.Thread(target=upload_wrapper)
        http_thread.start()

    def service_exit(self, service: Service):
        """
        Removes a service from the manager and handles cleanup.
        """
        self._remove_service(service.request.token)
