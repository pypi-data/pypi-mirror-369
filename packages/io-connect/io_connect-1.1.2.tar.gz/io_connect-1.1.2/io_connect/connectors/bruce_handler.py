# External Imports
import requests
from typeguard import typechecked
import io_connect.constants as c
from typing import Optional, Literal, Union
import json
import logging
from io_connect.utilities.store import ERROR_MESSAGE, Logger


@typechecked
class BruceHandler:
    __version__ = c.VERSION

    def __init__(
        self,
        user_id: str,
        data_url: str,
        organisation_id=str,
        on_prem: Optional[bool] = False,
        logger: Optional[logging.Logger] = None,
    ):
        self.user_id = user_id
        self.data_url = data_url
        self.organisation_id = organisation_id
        self.header = {"userID": user_id}
        self.on_prem = on_prem
        self.logger = Logger(logger)

    def get_insight_details(
        self,
        populate: list,
        sort: Optional[dict] = None,
        projection: Optional[dict] = None,
        filter: Optional[dict] = {},
        on_prem: Optional[bool] = None,
    ) -> list:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.GET_INSIGHT_DETAILS.format(
                protocol=protocol,
                data_url=self.data_url,
            )

            # Prepare the request payload
            payload = {
                "pagination": {"page": 1, "count": 1000},
                "populate": populate,
                "sort": sort,
                "projection": projection,
                "user": {"id": self.user_id},
                "filters": filter,
            }

            # Send the request via HTTP POST with headers
            response = requests.put(url, json=payload, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            response_data = json.loads(response.text)

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]["data"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return []

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return []

    def add_insight_result(
        self,
        insight_id: str,
        workbench_id: str,
        result: list,
        devID: str,
        whitelisted_users: list,
        metadata: dict,
        tags: list,
        on_prem: Optional[bool] = None,
    ) -> bool:
        """
        Adds an insight result.

        This function adds an insight result using the specified parameters.

        Args:
            insight_id (str): The ID of the insight.
            workbench_id (str): The ID of the workbench.
            result (list): List of results.
            devID (str): Parameters related to the result.
            class_type (str): Metadata related to the result.
            tags (list): List of tags associated with the result.

        Returns:
            bool: True if the result was added successfully, False otherwise.
        Example:
            # Instantiate BruceHandler
            >>> bruce_handler = BruceHandler(data_url="example.com", user_id="userID")

            # Example: Adding an insight result
            >>> insight_added = bruce_handler.add_insight_result(
            ...     insight_id="insightID",
            ...     workbench_id="workbenchID",
            ...     result=["result1", "result2"],
            ...     devID="devID",
            ...     class_type="class type",
            ...     tags=['tags']
            ... )

        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.ADD_INSIGHT_RESULT.format(
                protocol=protocol,
                data_url=self.data_url,
            )

            # Prepare the request payload
            payload = {
                "insightID": insight_id,
                "workbenchID": workbench_id,
                "result": result,
                "parameters": {"devID": devID},
                "metadata": metadata,
                "whitelistedUIsers": whitelisted_users,
                "tags": tags,
            }

            # Send the request via HTTP POST with headers
            response = requests.post(url, json=payload, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            return True

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return False

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return False

    def get_insight_results(
        self,
        insight_id: str,
        filter: Optional[dict] = {},
        page: int = 1,
        count: int = 10,
        single_page: bool = False,
        on_prem: Optional[bool] = None,
    ) -> Union[list, dict]:
        """
        Fetches insights results.

        This function fetches insights results using the specified parameters.

        Args:
            insight_id (str): The ID of the insight.
            filter (Optional[dict]): Dictionary for filtering the results.

        Returns:
            list: A list containing the fetched insight results.

        Example:
            # Instantiate BruceHandler
            >>> bruce_handler = BruceHandler(data_url="example.com", user_id="userID",organisation_id ="organisation_id")
            # Example
            >>> insight_id = "insightID"
            >>> fetched_results = bruce_handler.get_insight_results(insight_id=insight_id)
            # Example
            >>> insight_id = "insightID"
            >>> filter = {}
            >>> fetched_results = bruce_handler.get_insight_results(insight_id=insight_id,filter=filter)

        """
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.GET_INSIGHT_RESULT.format(
                protocol=protocol, data_url=self.data_url, insight_id=insight_id
            )

            all_results = []
            total_pages = 1  # Initialize with 1 to enter the loop
            while page <= total_pages:
                # Prepare the request payload
                payload = {
                    "filter": filter,
                    "pagination": {"page": page, "count": count},
                    "user": {"id": self.user_id, "organisation": self.organisation_id},
                }

                # Send the request via HTTP PUT with headers
                response = requests.put(
                    url, json=payload, headers={"userID": self.user_id}
                )

                # Check the response status code
                response.raise_for_status()

                response_data = response.json()

                if not response_data.get("success", False):
                    raise ValueError(response_data)

                if single_page:
                    return response_data["data"]
                page_data = response_data["data"]["data"]
                total_pages = response_data["data"]["pagination"]["totalPages"]
                all_results.extend(page_data)
                page += 1
            return all_results

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return [] if not single_page else {}


        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return [] if not single_page else {}


    def vector_upsert(
        self,
        insight_id: str,
        vector: list,
        payload: dict,
        on_prem: Optional[bool] = None,
    ) -> dict:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.VECTOR_UPSERT.format(protocol=protocol, data_url=self.data_url)

            # Prepare the request payload
            data = {
                "insightID": insight_id,
                "vector": vector,
                "payload": payload,
            }

            # Send the request via HTTP POST with headers
            response = requests.post(url, json=data, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            response_data = response.json()

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return {}

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return {}

    def vector_search(
        self,
        query_vector: list,
        insight_list: list,
        document_list: list,
        limit: int = 100,
        on_prem: Optional[bool] = None,
    ) -> list:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.VECTOR_SEARCH.format(protocol=protocol, data_url=self.data_url)

            # Prepare the request payload
            payload = {
                "query_vector": query_vector,
                "insightIDList": insight_list,
                "documentIDList": document_list,
                "limit": limit,
            }

            # Send the request via HTTP POST with headers
            response = requests.post(url, json=payload, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            response_data = response.json()

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return []

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return []

    def process_file(
        self,
        insight_id: str,
        insight_mongo_id: str,
        file_type: str,
        file_name: str,
        operation: Literal["upload", "download"] = None,
        on_prem: Optional[bool] = None,
    ) -> str:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.PROCESS_FILE.format(protocol=protocol, data_url=self.data_url)

            # Prepare the request payload
            payload = {
                "insightID": insight_id,
                "insightMongoID": insight_mongo_id,
                "fileType": file_type,
                "fileName": file_name,
            }

            # Send the request via HTTP POST with headers
            response = requests.post(url + operation, json=payload, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            response_data = response.json()

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return ""

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return ""

    def get_insight_tags(
        self,
        insight_id: str,
        on_prem: Optional[bool] = None,
    ) -> list:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.GET_INSIGHT_TAGS.format(protocol=protocol, data_url=self.data_url)

            # Send the request via HTTP GET with headers
            response = requests.get(url + insight_id, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            response_data = response.json()

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]["tags"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return []

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return []

    def get_related_insight(
        self,
        insight_id: str,
        on_prem: Optional[bool] = None,
    ) -> list:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.GET_RELATED_INSIGHTS.format(
                protocol=protocol,
                data_url=self.data_url,
                insight_id=insight_id,
            )

            # Send the request via HTTP GET with headers
            response = requests.get(url, headers=self.header)

            # Check the response status code
            response.raise_for_status()

            response_data = json.loads(response.text)

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return []

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return []

    def save_file_metadata(
        self,
        insight_id: str,
        file_name: str,
        file_type: str,
        file_size: int,
        tags: list,
        application_type: Literal["Workbench", "Insight"] = "Workbench",
        on_prem: Optional[bool] = None,
    ) -> str:
        try:
            # If on_prem is not provided, use the default value from the class attribute
            if on_prem is None:
                on_prem = self.on_prem

            # Construct the URL based on the on_prem flag
            protocol = "http" if on_prem else "https"

            # Endpoint URL
            url = c.SAVE_FILE_METADATA.format(
                protocol=protocol,
                data_url=self.data_url,
                insight_id=insight_id,
            )

            data = {
                "file": {
                    "fileName": file_name,
                    "fileType": file_type,
                    "fileSize": file_size,
                },
                "tags": tags,  # convert from string to list
                "insightID": insight_id,
                "user": {"id": self.user_id},
                "applicationType": application_type,
            }

            # Step 1: Get signed URL
            response = requests.post(
                url,
                headers=self.header,
                json=data,
            )

            # Check the response status code
            response.raise_for_status()

            response_data = json.loads(response.text)

            if not response_data["success"]:
                raise ValueError(response_data)

            return response_data["data"]

        except requests.exceptions.RequestException as e:
            error_message = (
                ERROR_MESSAGE(response, url)
                if "response" in locals()
                else f"\n[URL] {url}\n[EXCEPTION] {e}"
            )
            self.logger.error(f"[EXCEPTION] {type(e).__name__}: {error_message}")
            return ""

        except Exception as e:
            self.logger.error(f"[EXCEPTION] {e}")
            return ""
