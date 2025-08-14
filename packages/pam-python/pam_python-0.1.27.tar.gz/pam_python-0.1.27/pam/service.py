from abc import abstractmethod
from pathlib import Path
from datetime import datetime
import json
from typing import TYPE_CHECKING, Union
import pandas as pd
import dask.dataframe as dd
from pam.utils import log, deep_convert_numbers_to_strings, get_adapter_id
from pam.models.request_command import RequestCommand
from pam.temp_file_utils import TempfileUtils

if TYPE_CHECKING:
    from pam.task_manager import TaskManager


class Service:
    """
    Service base class
    """

    def __init__(self, task_manager: 'TaskManager', req: RequestCommand):
        self.request = req
        self.task_manager = task_manager

    def get_adapter_id(self) -> str:
        """
        Returns the adapter ID for the service based on the request's response API.
        """
        return get_adapter_id(self.request.response_api)
    
    # == REQUEST DATA ===
    def _request_data(self, page: str = "") -> None:
        """Requests data for the specified page."""
        log(f"{self.request.service_name}: Requesting data for page={page}")
        self.task_manager.service_request_data(self, page)

    # == UPLOAD RESULT ===
    def _upload_result(self, df: Union[pd.DataFrame, dd.DataFrame]) -> str:
        """
        Uploads the result DataFrame to a temporary file and notifies the task manager.
        """
        if isinstance(df, dd.DataFrame):
            df = df.compute()
        elif not isinstance(df, pd.DataFrame):
            raise ValueError("The input must be a Pandas or Dask DataFrame")

        tmp_file_name = TempfileUtils.get_temp_file_name(
            self.request.service_name, self.request.token, "result_", ".csv"
        )

        dry_run = self.request.runtime_parameters.get("dry_run", "false")
        if dry_run is not None and dry_run.lower() == "true":
            log("Dry run mode will not upload results.")
            return tmp_file_name

        try:
            df.to_csv(tmp_file_name, index=False)
            log(f"{self.request.service_name}: Uploading result file: {tmp_file_name}")
            self.task_manager.service_upload_result(self, tmp_file_name)
        except Exception as e:
            log(f"Failed to upload result file: {e}")
            raise

        return tmp_file_name

    def _upload_report(self, report_name: str, report_json: dict, tracker_name: str = "") -> str:
        """
        Uploads a report in JSON format to a temporary file and notifies the task manager.
        Args:
            report_name (str): Name of the report.
            report_json (dict): The report content as a dictionary.
            tracker_name (str, optional): Tracker name to include in the report. Defaults to empty string.
        Returns:
            str: Path to the uploaded report CSV file.
        """
        if not isinstance(report_json, dict):
            raise ValueError("report_json must be a dictionary")

        adapter_id = get_adapter_id(self.request.response_api)
        service_name = self.request.service_name
        token = self.request.token

        report_json = deep_convert_numbers_to_strings(report_json)
        json_string = json.dumps(report_json)

        formatted_report_name = f"data_{report_name}_no_index"
        df = pd.DataFrame({
            'customer': [adapter_id],
            '_tracker_name': [tracker_name],
            formatted_report_name: [json_string]
        })

        report_csv_path = TempfileUtils.get_temp_file_name(
            service_name, token, f"report_{report_name}_", '.csv'
        )

        dry_run = self.request.runtime_parameters.get("dry_run", "false")
        if dry_run is not None and dry_run.lower() == "true":
            log("Dry run mode will not upload report.")
            return report_csv_path

        try:
            df.to_csv(report_csv_path, index=False)
            log(f"{self.request.service_name}: Uploading report file: {report_csv_path}")
            self.task_manager.service_upload_report(self, report_csv_path)
        except Exception as e:
            log(f"Failed to upload report: {e}")
            raise
        
        return report_csv_path

    def _request_sqlite(self, file_name: str = "", is_shared: bool = False) -> str:
        """Requests last sqlite file that this plugin has uploaded from the last time.
        Returns:
            The file path to the downloaded SQLite file, or None if the download failed.
        """
        return self.task_manager.service_request_sqlite(self, file_name, is_shared)

    def _upload_sqlite(self, file_name: str = "", is_shared: bool = False, sqlite_file: str = "") -> str:
        """
        Uploads the result SQLite file to CDP.

        :param file_name: The logical file name being uploaded.
        :param is_shared: Whether this file should be treated as shared.
        :param sqlite_file: Path to the SQLite file to upload.
        :return: The uploaded file name if successful, or empty string if failed.
        """
        return self.task_manager.service_upload_sqlite(self, file_name, is_shared, sqlite_file)

    def _exit(self) -> None:
        """Signals the task manager to exit the service."""
        self.task_manager.service_exit(self)

    # Abstract methods to be implemented by subclasses
    @abstractmethod
    def on_start(self) -> None:
        """
        Define the behavior when the service starts.
        """
        pass

    @abstractmethod
    def on_data_input(self, req: RequestCommand) -> None:
        """
        Define the behavior for handling data input.
        """
        pass

    @abstractmethod
    def on_destroy(self) -> None:
        """
        Define the behavior when the service is destroyed.
        """
        pass

    @abstractmethod
    def on_terminate(self) -> None:
        """
        Define the behavior when the service is terminated.
        """
        pass

    @abstractmethod
    def get_status(self) -> str:
        """
        Define the behavior for retrieving the service status.
        """
        pass
