# coding: utf-8

"""
    DB Analytics Tools: Airflow REST API Client

    This module provides a class for interacting with the Apache Airflow REST API.
"""

import urllib
import datetime
import requests
from requests.auth import HTTPBasicAuth
import pandas as pd


class AirflowRESTAPI:
    """
    A client for interacting with the Apache Airflow REST API.
    Supports retrieving DAGs, fetching DAG details, and triggering DAG runs.
    """

    headers = {"Content-Type": "application/json"}

    def __init__(self, api_url, username, password):
        """
        Initializes the AirflowRESTAPI instance with API credentials.

        :param api_url: Base URL of the Airflow API.
        :param username: Airflow API username.
        :param password: Airflow API password.
        """
        self.api_url = api_url
        self.username = username
        self.password = password
        self.auth = HTTPBasicAuth(username, password)

    def get(self, endpoint):
        """
        Sends a GET request to the specified API endpoint.

        :param endpoint: API endpoint to query.
        :return: Parsed JSON response or an empty dictionary on failure.
        """
        url = urllib.parse.urljoin(self.api_url, endpoint)
        response = requests.get(url, headers=self.headers, auth=self.auth)

        if response.status_code == 200:
            return response.json()

        print(f"Error {response.status_code}: {response.text}")
        return {}

    def post(self, endpoint, data):
        """
        Sends a POST request to the specified API endpoint.

        :param endpoint: API endpoint to send data to.
        :param data: Dictionary containing the request payload.
        :return: Parsed JSON response or an empty dictionary on failure.
        """
        url = urllib.parse.urljoin(self.api_url, endpoint)
        response = requests.post(url, json=data, headers=self.headers, auth=self.auth)

        if response.status_code in [200, 201]:
            return response.json()

        print(f"Error {response.status_code}: {response.text}")
        return {}

    def get_dags_list(self, include_all=False):
        """
        Retrieves the list of DAGs from the Airflow API.

        :param include_all: If True, returns all DAGs; otherwise, filters by the current user.
        :return: Pandas DataFrame containing DAG details.
        """
        columns = [
            "dag_id", "description", "fileloc", "owners", "is_active", "is_paused",
            "timetable_description", "last_parsed_time", "next_dagrun", "tags"
        ]

        endpoint = "dags"
        response = self.get(endpoint).get("dags", [])

        if not response:
            print("No DAGs found.")
            return pd.DataFrame(columns=columns)

        df = pd.DataFrame(response)[columns]
        df["tags"] = df["tags"].apply(lambda x: [elt["name"] for elt in x])  # Convert tags to list format

        if include_all:
            return df.sort_values(by="dag_id")

        # Filter DAGs owned by the current user
        return (
            df[df["owners"].apply(lambda owners: self.username in owners)]
            .reset_index(drop=True)
            .sort_values(by="dag_id")
        )

    def get_dag_details(self, dag_id, include_tasks=False):
        """
        Fetches detailed information for a specific DAG.

        :param dag_id: ID of the DAG to retrieve.
        :param include_tasks: If True, includes task details in the response.
        :return: Dictionary containing DAG details.
        """
        endpoint = f"dags/{dag_id}"
        dag = self.get(endpoint)

        endpoint = f"dags/{dag_id}/details"
        details = self.get(endpoint)

        endpoint = f"dags/{dag_id}/tasks"
        tasks = self.get(endpoint)

        num_tasks = len(tasks.get("tasks", []))  # Handle potential missing "tasks" key

        response = dag | details  # Merge dictionaries (Python 3.9+)
        response["num_tasks"] = num_tasks

        if include_tasks:
            response["tasks"] = tasks.get("tasks", [])

        return response

    def get_dag_tasks(self, dag_id):
        """
        Retrieves the list of tasks for a specific DAG.

        :param dag_id: ID of the DAG.
        :return: Pandas DataFrame containing task details.
        """
        columns = [
            "task_id", "operator_name", "owner", "params", "depends_on_past",
            "downstream_task_ids", "wait_for_downstream", "trigger_rule"
        ]

        endpoint = f"dags/{dag_id}/tasks"
        tasks = self.get(endpoint)

        return pd.DataFrame(tasks.get("tasks", []), columns=columns)

    def trigger_dag(self, dag_id, start_date, end_date):
        """
        Triggers a DAG run with the specified start and end dates.

        :param dag_id: ID of the DAG to trigger.
        :param start_date: Start date in YYYY-MM-DD format.
        :param end_date: End date in YYYY-MM-DD format.
        :return: Dictionary containing the API response.
        """
        endpoint = f"dags/{dag_id}/dagRuns"

        start_dt = datetime.datetime.strptime(start_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
        end_dt = datetime.datetime.strptime(end_date, "%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)

        data = {
            "conf": {},
            "dag_run_id": f"manual_run_{start_dt.strftime('%Y%m%dT%H%M%S')}",
            "data_interval_start": start_dt.isoformat(),
            "data_interval_end": end_dt.isoformat(),
            "logical_date": end_dt.isoformat(),
            "note": f"{self.username} triggered {dag_id} from {start_date} to {end_date}",
        }

        return self.post(endpoint, data=data)
