import io
from operator import attrgetter
import os
import re
import base64
import time
import hashlib
import struct
import datetime
from uuid import UUID
from pathlib import Path
from typing import Iterator, Iterable, List, Optional, Callable, Any, Union, Dict
from concurrent.futures import ThreadPoolExecutor, Future, as_completed
from threading import Event

import crc32c
import requests
import psutil
from tqdm import tqdm
from PIL import Image as ImagePIL

from lqs.transcode import Transcode
from lqs.common.facade import CoreFacade
from lqs.common.utils import (
    get_relative_object_path,
    decompress_chunk_bytes,
    get_record_image,
)
from lqs.common.exceptions import ConflictException, NotFoundException
from lqs.interface.base.models import UploadState
from lqs.interface.core.models import (
    Digestion,
    DigestionPart,
    DigestionPartIndexEntry,
    Ingestion,
    IngestionPart,
    JSONLLog,
    Object,
    ObjectPart,
    ObjectStore,
    Record,
    Topic,
    ProcessState,
)

DEFAULT_LOG_FILE_REGEXES = [
    r"/(?P<log_name>[^/]*?)\.bag$",
    r"/(?P<log_name>[^/]*?)\.log$",
    r"/(?P<log_name>[^/]*?)\.mcap$",
    r"/(?P<log_name>[^/]*?)\.jsonl$",
    r"/(?P<log_name>[^/]*)\.log/log0$",
    r"/(?P<log_name>[^/]*)/log0$",
    r"/(?P<log_name>[^/]*)/manifests\/[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-4[0-9a-fA-F]{3}-[89aAbB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$",
]

DEFAULT_PATH_FILTER_REGEXES = [
    r"^(?!.*\/\.).*$",
]


class CoreUtils:
    def __init__(self, app: CoreFacade):
        self.app = app

    def get_info(self, print_config=False, log_config=False):
        self.app.logger.info("Logging info message.")
        self.app.logger.debug("Logging debug message.")
        self.app.logger.warning("Logging warn message.")
        self.app.logger.error("Logging error message.")

        if print_config:
            print(self.app.config)

        if log_config:
            self.app.logger.info(self.app.config)

    def fetch_by_name_or_create(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        resource_name: Optional[str] = None,
        list_params: dict = {},
        create_if_missing: bool = True,
        create_params: dict = {},
        create_func: Optional[Callable] = None,
        list_func: Optional[Callable] = None,
        fetch_func: Optional[Callable] = None,
    ) -> Any:
        """
        Fetch or create a resource by name.

        This function fetches a resource by id if provided, or by name if provided,
        or creates the resource if it doesn't exist and ``create_if_missing`` is True.

        If no resource id or name is provided, the function returns None.

        :param resource_type: The type of the resource.
        :type resource_type: str
        :param resource_id: The id of the resource. Defaults to None.
        :type resource_id: str, optional
        :param resource_name: The name of the resource. Defaults to None.
        :type resource_name: str, optional
        :param list_params: Additional parameters to use when listing the resource. Defaults to ``{}``.
        :type list_params: dict, optional
        :param create_if_missing: Whether to create the resource if it doesn't exist. Defaults to True.
        :type create_if_missing: bool, optional
        :param create_params: Additional parameters to use when creating the resource. Defaults to ``{}``.
        :type create_params: dict, optional
        :param create_func: The function to use when creating the resource. Defaults to None.
        :type create_func: Callable, optional
        :param list_func: The function to use when listing the resource. Defaults to None.
        :type list_func: Callable, optional
        :param fetch_func: The function to use when fetching the resource. Defaults to None.
        :type fetch_func: Callable, optional

        :raises NotFoundException: If no resource is found and ``create_if_missing`` is False.

        :returns: The fetched or created resource, or None if no resource is found or created.
        :rtype: Any
        """
        resource = None
        if resource_id is None and resource_name is not None:
            # if no resource id is provided, we try to find the resource by name
            resources = list_func(name=resource_name, **list_params).data
            if len(resources) == 0:
                # we didn't find the resource by name
                if create_if_missing:
                    # if we're allowed to create the resource, we create it using the provided parameters
                    try:
                        resource = create_func(name=resource_name, **create_params).data
                    except ConflictException:
                        # resource with the name may have been created while we were trying to create the resource
                        resources = list_func(name=resource_name, **list_params).data
                        if len(resources) == 0:
                            raise NotFoundException(
                                f"No {resource_type} found with name {resource_name}"
                            )
                        resource = resources[0]
                else:
                    raise NotFoundException(
                        f"No {resource_type} found with name {resource_name}"
                    )
            else:
                # we use the found resource
                resource = resources[0]
        elif resource_id is not None and resource_name is None:
            # if no resource name is provided, we try to find the resource by id
            resource = fetch_func(resource_id).data

        return resource

    def list_all(
        self,
        list_method,
        limit=100,
        start_offset=0,
        max_workers=10,
        **kwargs,
    ) -> List[Any]:
        """
        List all resources.

        This function lists all resources using the provided list method.

        :param list_method: The method to use to list the resources.
        :type list_method: Callable
        :param limit: The maximum number of resources to list at a time. Defaults to 100.
        :type limit: int, optional
        :param start_offset: The offset to start listing resources from. Defaults to 0.
        :type start_offset: int, optional
        :param max_workers: The maximum number of workers to use when listing resources. Defaults to 10.
        :type max_workers: int, optional
        :param kwargs: Additional parameters to pass to the list method.
        :type kwargs: dict

        :returns: The list of resources.
        :rtype: List[Any]
        """

        current_offset = start_offset

        kwargs["limit"] = limit
        kwargs["offset"] = current_offset
        resources = []
        res = list_method(**kwargs)
        resources += res.data
        total_count = res.count
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            while current_offset + limit < total_count:
                current_offset += limit
                kwargs["offset"] = current_offset
                future = executor.submit(list_method, **kwargs)
                futures.append(future)

            for future in futures:
                res = future.result()
                resources += res.data
        return resources

    def fetch_all(
        self,
        list_method,
        fetch_function,
        limit=100,
        start_offset=0,
        max_workers=10,
        **kwargs,
    ) -> List[Any]:
        """
        Fetch all resources.

        This function first lists all resources using the provided list method, then fetches each resource.
        This is useful for process part resources, which do not return the full resource when listed.

        :param list_method: The method to use to list the resources.
        :type list_method: Callable
        :param fetch_function: The function to use to fetch the resources given an instance of the resource.
        :type fetch_function: Callable
        :param limit: The maximum number of resources to list at a time. Defaults to 100.
        :type limit: int, optional
        :param start_offset: The offset to start listing resources from. Defaults to 0.
        :type start_offset: int, optional
        :param max_workers: The maximum number of workers to use when listing resources. Defaults to 10.
        :type max_workers: int, optional
        :param kwargs: Additional parameters to pass to the list method.
        :type kwargs: dict

        :returns: The list of resources.
        :rtype: List[Any]
        """
        shallow_resources = self.list_all(
            list_method=list_method,
            limit=limit,
            start_offset=start_offset,
            max_workers=max_workers,
            **kwargs,
        )
        resources = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = []
            for resource in shallow_resources:
                future = executor.submit(fetch_function, resource)
                futures.append(future)

            for future in futures:
                resources.append(future.result())
        return resources

    # Object Utils

    def calculate_etag(self, file_path: str, part_size: int = 100 * 1024 * 1024) -> str:
        """
        Calculate the ETag of a file.

        This function calculates the ETag of a file assuming it is uploaded as a multipart upload.

        :param file_path: The path to the file to calculate the ETag for.
        :type file_path: str
        :param part_size: The size of each chunk to read from the file. Defaults to 100 * 1024 * 1024.
        :type part_size: int, optional

        :returns: The calculated ETag.
        :rtype: str
        """
        part_md5s = []
        with open(file_path, "rb") as f:
            for part in iter(lambda: f.read(part_size), b""):
                part_md5s.append(hashlib.md5(part).digest())
        return hashlib.md5(b"".join(part_md5s)).hexdigest() + f"-{len(part_md5s)}"

    def verify_integrity(
        self, file_path: str, etag: str, part_size: int = 100 * 1024 * 1024
    ) -> bool:
        """
        Verify the integrity of a file given an ETag.

        This function verifies the integrity of a file assuming it is uploaded as a multipart upload.

        :param file_path: The path to the file to verify the integrity of.
        :type file_path: str
        :param etag: The ETag of the file.
        :type etag: str
        :param part_size: The size of each chunk to read from the file. Defaults to 100 * 1024 * 1024.
        :type part_size: int, optional
        :returns: Whether the file is intact.
        :rtype: bool
        """
        calculated_etag = self.calculate_etag(file_path, part_size)
        self.app.logger.debug(
            f"Calculated ETag for file {file_path}: {calculated_etag}"
        )
        return calculated_etag == etag

    def verify_object_integrity(
        self, file_path: str, object: Object, part_size: int = 100 * 1024 * 1024
    ) -> bool:
        """
        Verify the integrity of a file given an object.

        This function verifies the integrity of a file assuming it is uploaded as a multipart upload.

        :param file_path: The path to the file to verify the integrity of.
        :type file_path: str
        :param object: The object to verify the integrity of.
        :type object: Object
        :param part_size: The size of each chunk to read from the file. Defaults to 100 * 1024 * 1024.
        :type part_size: int, optional
        :returns: Whether the file is intact.
        :rtype: bool
        """
        return self.verify_integrity(file_path, object.etag, part_size)

    def get_object_store(
        self,
        object_store_id: Optional[UUID] = None,
        bucket_name: Optional[str] = None,
    ) -> ObjectStore:
        """
        Get an object store.

        This function gets an object store by ID or bucket name. If both object_store_id and bucket_name are provided, an exception is raised.

        :param object_store_id: The id of the object store. Defaults to None.
        :type object_store_id: UUID, optional
        :param bucket_name: The name of the object store bucket. Defaults to None.
        :type bucket_name: str, optional
        :raises Exception: If neither object_store_id nor bucket_name is provided.
        :returns: The object store.
        :rtype: ObjectStore
        """
        if object_store_id is not None and bucket_name is not None:
            raise Exception(
                "Only one of object_store_id or bucket_name can be provided."
            )
        elif object_store_id is not None:
            object_store = self.app.fetch.object_store(object_store_id).data
        elif bucket_name is not None:
            object_stores = self.app.list.object_store(bucket_name=bucket_name).data
            if len(object_stores) == 0:
                raise Exception(f"Object store {bucket_name} not found.")
            object_store = object_stores[0]
        else:
            raise Exception("Either object_store_id or bucket_name must be provided.")
        return object_store

    def find_object_store_logs(
        self,
        object_store_id: Optional[UUID] = None,
        bucket_name: Optional[str] = None,
        root_prefix: str = "",
        skip_prefixes: List[str] = [],
        skip_duplicates: bool = True,
        log_file_regexes: List[str] = DEFAULT_LOG_FILE_REGEXES,
        max_objects_to_list: Optional[int] = 100_000,
        fail_if_more_than_max_objects_to_list: bool = False,
    ) -> List[dict]:
        """
        Find logs in an object store.

        This function finds log objects in a given object store bucket. It uses a list of regular expressions to match log file names.
        One of object_store_id or bucket_name must be provided, but not both. Searching starts from the root_prefix and continues recursively.
        If skip_duplicates is set to True, only unique logs based on the found log name, group name, the object's Etag, and the object's size,
        and the first unique object encountered is what is used. Specific prefixes can be skipped using skip_prefixes.
        We only list up to max_objects_to_list objects, and if fail_if_more_than_max_objects_to_list is set to True,
        we raise an exception if we find more objects than max_objects_to_list.

        :param object_store_id: The id of the object store to find logs in (mutually exclusive with bucket_name).
        :type object_store_id: UUID, optional
        :param bucket_name: The name of the object store bucket to find logs in (mutually exclusive with object_store_id).
        :type bucket_name: str, optional
        :param root_prefix: The prefix to start searching from. Defaults to "".
        :type root_prefix: str, optional
        :param skip_prefixes: A list of prefixes to skip. Defaults to [].
        :type skip_prefixes: List[str], optional
        :param skip_duplicates: Whether to skip duplicate logs. Defaults to True.
        :type skip_duplicates: bool, optional
        :param log_file_regexes: A list of regular expressions to match log file names. Defaults to DEFAULT_LOG_FILE_REGEXES.
        :type log_file_regexes: List[str], optional
        :param max_objects_to_list: The maximum number of objects to list. Defaults to 100_000.
        :type max_objects_to_list: int, optional
        :param fail_if_more_than_max_objects_to_list: Whether to raise an exception if more objects are found than max_objects_to_list. Defaults to False.
        :type fail_if_more_than_max_objects_to_list: bool, optional
        :returns: A list of dictionaries containing log parameters.
        :rtype: List[dict]
        """
        if isinstance(log_file_regexes, str):
            log_file_regexes = [log_file_regexes]

        object_store = self.get_object_store(
            object_store_id=object_store_id, bucket_name=bucket_name
        )

        objects = []
        object_list_res = None
        while object_list_res is None or object_list_res.is_truncated:
            object_list_res = self.app.list.object(
                object_store_id=object_store.id,
                prefix=root_prefix,
                continuation_token=object_list_res.next_continuation_token
                if object_list_res is not None
                else None,
            )
            for object in object_list_res.data:
                skip = False
                for skip_prefix in skip_prefixes:
                    if object.key.startswith(skip_prefix):
                        skip = True
                        break
                if not skip:
                    objects.append(object)
            if max_objects_to_list is not None and len(objects) > max_objects_to_list:
                if fail_if_more_than_max_objects_to_list:
                    raise Exception(
                        f"Found more than {max_objects_to_list} objects in object store {bucket_name}."
                    )
                break

        log_param_sets = []
        for object in objects:
            object_key = object.key
            for log_file_regex in log_file_regexes:
                re_match = re.search(log_file_regex, object_key)
                if re_match:
                    re_params = re_match.groupdict()
                    log_name = re_params.get("log_name")
                    group_name = re_params.get("group_name")
                    log_params = {
                        "log_key": object_key,
                        "log_name": log_name,
                        "group_name": group_name,
                        "etag": object.etag,
                        "size": object.size,
                    }
                    log_param_sets.append(log_params)
                    break

        if skip_duplicates:
            unique_keys = set()
            log_param_sets_filtered = []
            for log_params in log_param_sets:
                unique_key = f"{log_params['log_name']}_{log_params['group_name']}_{log_params['etag']}_{log_params['size']}"
                if unique_key not in unique_keys:
                    unique_keys.add(unique_key)
                    log_param_sets_filtered.append(log_params)
            log_param_sets = log_param_sets_filtered

        return log_param_sets

    def sync_object_store_logs(
        self,
        object_store_id: Optional[UUID] = None,
        bucket_name: Optional[str] = None,
        root_prefix: str = "",
        skip_prefixes: List[str] = [],
        skip_duplicates: bool = True,
        log_file_regexes: List[str] = DEFAULT_LOG_FILE_REGEXES,
        max_objects_to_list: Optional[int] = 100_000,
        fail_if_more_than_max_objects_to_list: bool = False,
        log_param_sets: Optional[List[Dict[str, str | int | None]]] = None,
        group_id: Optional[str] = None,
        group_name: Optional[str] = None,
        create_group_if_missing: bool = True,
        group_note: Optional[str] = None,
        group_context: Optional[dict] = None,
        ignore_group_for_matching: bool = True,
        log_id: Optional[str] = None,
        log_name: Optional[str] = None,
        create_log_if_missing: bool = True,
        log_note: Optional[str] = None,
        log_context: Optional[dict] = None,
        create_ingestions: bool = True,
        skip_existing_ingestions: bool = True,
        ingestion_state: ProcessState = ProcessState.queued,
        ingestion_note: Optional[str] = None,
        ingestion_context: Optional[dict] = None,
        ingestion_workflow_id: Optional[str] = None,
        ingestion_workflow_context: Optional[dict] = None,
        retry_count: Optional[int] = None,
        verbosity: Optional[str] = "info",
        dry_run: bool = False,
    ) -> int:
        """
        Ingest logs from an object store.

        This function creates logs and ingestions for log objects found in a given object store. It uses a list of regular expressions to match log file names.
        One of object_store_id or bucket_name must be provided, but not both. Searching starts from the root_prefix and continues recursively.
        If skip_duplicates is set to True, only unique logs based on the found log name, group name, the object's Etag, and the object's size,
        and the first unique object encountered is what is used. Specific prefixes can be skipped using skip_prefixes.
        We only list up to max_objects_to_list objects, and if fail_if_more_than_max_objects_to_list is set to True,
        we raise an exception if we find more objects than max_objects_to_list.
        If group_id or group_name is provided, we use the provided group, otherwise we create a group based on the found log parameters.
        If log_id or log_name is provided, we use the provided log, otherwise we create a log based on the found log parameters.

        :param object_store_id: The id of the object store to find logs in (mutually exclusive with bucket_name).
        :type object_store_id: UUID, optional
        :param bucket_name: The name of the object store bucket to find logs in (mutually exclusive with object_store_id).
        :type bucket_name: str, optional
        :param root_prefix: The prefix to start searching from. Defaults to "".
        :type root_prefix: str, optional
        :param skip_prefixes: A list of prefixes to skip. Defaults to [].
        :type skip_prefixes: List[str], optional
        :param skip_duplicates: Whether to skip duplicate logs. Defaults to True.
        :type skip_duplicates: bool, optional
        :param log_file_regexes: A list of regular expressions to match log file names. Defaults to DEFAULT_LOG_FILE_REGEXES.
        :type log_file_regexes: List[str], optional
        :param max_objects_to_list: The maximum number of objects to list. Defaults to 100_000.
        :type max_objects_to_list: int, optional
        :param fail_if_more_than_max_objects_to_list: Whether to raise an exception if more objects are found than max_objects_to_list. Defaults to False.
        :type fail_if_more_than_max_objects_to_list: bool, optional
        :param log_param_sets: A list of log parameters describing logs in the object store.  If provided, only these logs will be synced (i.e., the root_prefix will not be searched for logs fitting the specified criteria). Defaults to None.
        :type log_param_sets: List[dict[str, str | int | None]], optional
        :param group_id: The id of the group to create logs in. Defaults to None.
        :type group_id: str, optional
        :param group_name: The name of the group to create logs in. Defaults to None.
        :type group_name: str, optional
        :param create_group_if_missing: Whether to create the group if it doesn't exist. Defaults to True.
        :type create_group_if_missing: bool, optional
        :param group_note: The note to use when creating the group. Defaults to None.
        :type group_note: str, optional
        :param group_context: The context to use when creating the group. Defaults to None.
        :type group_context: dict, optional
        :param ignore_group_for_matching: Whether to ignore the group when matching logs. Suitable if logs have been moved to different groups since last sync. Defaults to False.
        :type ignore_group_for_matching: bool, optional
        :param log_id: The id of the log to create ingestions for. Defaults to None.
        :type log_id: str, optional
        :param log_name: The name of the log to create ingestions for. Defaults to None.
        :type log_name: str, optional
        :param create_log_if_missing: Whether to create the log if it doesn't exist. Defaults to True.
        :type create_log_if_missing: bool, optional
        :param log_note: The note to use when creating the log. Defaults to None.
        :type log_note: str, optional
        :param log_context: The context to use when creating the log. Defaults to None.
        :type log_context: dict, optional
        :param create_ingestions: Whether to create ingestions for the found logs. Defaults to True.
        :type create_ingestions: bool, optional
        :param skip_existing_ingestions: Whether to skip existing ingestions. Defaults to True.
        :type skip_existing_ingestions: bool, optional
        :param ingestion_state: The state to use when creating ingestions. Defaults to ProcessState.queued.
        :type ingestion_state: ProcessState, optional
        :param ingestion_note: The note to use when creating ingestions. Defaults to None.
        :type ingestion_note: str, optional
        :param ingestion_context: The context to use when creating ingestions. Defaults to None.
        :type ingestion_context: dict, optional
        :param ingestion_workflow_id: The workflow id to use when creating ingestions. Defaults to None.
        :type ingestion_workflow_id: str, optional
        :param ingestion_workflow_context: The workflow context to use when creating ingestions. Defaults to None.
        :type ingestion_workflow_context: dict, optional
        :param retry_count: The number of times to retry the operation. Defaults to None.
        :type retry_count: int, optional
        :param verbosity: The verbosity level to use for logging. Defaults to "info".
        :type verbosity: str, optional
        :param dry_run: Whether to perform a dry run. Defaults to False.
        :type dry_run: bool, optional
        :returns: The number of ingestions created.
        :rtype: int
        """

        def logger(msg):
            if verbosity is not None:
                getattr(self.app.logger, verbosity.lower())(msg)

        if retry_count is not None:
            if not isinstance(retry_count, int):
                raise TypeError("retry_count must be an integer.")
            if retry_count < 0:
                raise ValueError("retry_count must be greater than or equal to zero.")
            self.app.config.retry_count = retry_count

        # First, figure out which group/log we're working with
        group = None
        if group_id is not None or group_name is not None:
            group = self.fetch_by_name_or_create(
                resource_type="group",
                resource_id=group_id,
                resource_name=group_name,
                list_params={},
                create_if_missing=create_group_if_missing and not dry_run,
                create_params={"note": group_note, "context": group_context},
                create_func=self.app.create.group,
                list_func=self.app.list.group,
                fetch_func=self.app.fetch.group,
            )
        if group is None:
            logger(
                "No group ID or name provided; will find/create groups based on found log parameters."
            )

        log = None
        if group is not None:
            if log_id is not None or log_name is not None:
                list_params = {}
                if not ignore_group_for_matching:
                    list_params["group_id"] = group.id
                log = self.fetch_by_name_or_create(
                    resource_type="log",
                    resource_id=log_id,
                    resource_name=log_name,
                    list_params=list_params,
                    create_if_missing=create_log_if_missing and not dry_run,
                    create_params={
                        "group_id": group.id,
                        "note": log_note,
                        "context": log_context,
                    },
                    create_func=self.app.create.log,
                    list_func=self.app.list.log,
                    fetch_func=self.app.fetch.log,
                )
            if log is None:
                logger(
                    "No log ID or name provided; will find/create logs based on found log parameters."
                )

        object_store = self.get_object_store(
            object_store_id=object_store_id, bucket_name=bucket_name
        )

        if not log_param_sets:
            log_param_sets = self.find_object_store_logs(
                object_store_id=object_store_id,
                bucket_name=bucket_name,
                root_prefix=root_prefix,
                skip_prefixes=skip_prefixes,
                skip_duplicates=skip_duplicates,
                log_file_regexes=log_file_regexes,
                max_objects_to_list=max_objects_to_list,
                fail_if_more_than_max_objects_to_list=fail_if_more_than_max_objects_to_list,
            )
            logger(
                f"Found {len(log_param_sets)} logs in {root_prefix} of object store {object_store.bucket_name} ({object_store.id})."
            )

        created_ingestion_count = 0
        for params in log_param_sets:
            sync_group = None
            sync_log = None

            log_key_param = params.get("log_key")
            log_name_param = params.get("log_name")
            group_name_param = params.get("group_name")

            if sync_group is None and group is None:
                groups = self.app.list.group(name=group_name_param).data
                if len(groups) == 0:
                    logger(f"Creating group {group_name_param}")
                    sync_group = self.app.create.group(
                        name=group_name_param,
                        note=group_note,
                        context=group_context,
                    ).data
                else:
                    sync_group = groups[0]
            elif sync_group is None and group is not None:
                sync_group = group

            if sync_log is None and log is None:
                list_params = {}
                if not ignore_group_for_matching:
                    list_params["group_id"] = sync_group.id
                sync_log = self.fetch_by_name_or_create(
                    resource_type="log",
                    resource_name=log_name_param,
                    list_params=list_params,
                    create_if_missing=create_log_if_missing and not dry_run,
                    create_params={
                        "group_id": sync_group.id,
                        "note": log_note,
                        "context": log_context,
                    },
                    create_func=self.app.create.log,
                    list_func=self.app.list.log,
                    fetch_func=self.app.fetch.log,
                )
            elif sync_log is None and log is not None:
                sync_log = log

            # for each log, we create an ingestion
            if create_ingestions:
                ingestions = self.app.list.ingestion(
                    log_id=sync_log.id,
                    object_store_id=object_store.id,
                    object_key=log_key_param,
                ).data
                if len(ingestions) == 0 or not skip_existing_ingestions:
                    logger(
                        f"No ingestions found for log {sync_log.name} ({sync_log.id}) for {log_key_param} in {object_store.id}"
                    )
                    if not dry_run:
                        logger(
                            f"Creating ingestion for log {sync_log.name} ({sync_log.id}) for {log_key_param} in {object_store.id}"
                        )
                        ingestion = self.app.create.ingestion(
                            log_id=sync_log.id,
                            object_store_id=object_store.id,
                            object_key=log_key_param,
                            name=sync_log.name,
                            note=ingestion_note,
                            state=ingestion_state,
                            context=ingestion_context,
                            workflow_id=ingestion_workflow_id,
                            workflow_context=ingestion_workflow_context,
                        ).data
                        logger(
                            f"Ingestion {ingestion.id} created for log {sync_log.name} ({sync_log.id}) for {log_key_param} in {object_store.id}"
                        )
                        created_ingestion_count += 1
                else:
                    logger(
                        f"Ingestions already exist for log {sync_log.name} ({sync_log.id}) for {log_key_param} in {object_store.id}"
                    )

        logger(f"Created {created_ingestion_count} ingestions.")
        return created_ingestion_count

    # Uploading

    def upload_log_object_part(
        self,
        log_id: str,
        object_key: str,
        part_number: int,
        file_path: str,
        offset: int,
        size: int,
        verify_integrity: bool = True,
        max_attempts: int = 5,
        backoff_factor: float = 5.0,
        connect_timeout: int = 60,
        read_timeout: int = 600,
    ):
        """
        Upload a part of a file to a log object.

        :param log_id: The log id to upload the object part to.
        :type log_id: str
        :param object_key: The key of the object to upload the part to.
        :type object_key: str
        :param part_number: The part number of the object part.
        :type part_number: int
        :param file_path: The path to the file to upload.
        :type file_path: str
        :param offset: The offset in the file to start reading from.
        :type offset: int
        :param size: The size of the part to upload.
        :type size: int
        :param verify_integrity: Whether to verify the integrity of the uploaded part. Defaults to True.
        :type verify_integrity: bool, optional
        :param max_attempts: The maximum number of attempts to upload the part. Defaults to 5.
        :type max_attempts: int, optional
        :param backoff_factor: The backoff factor for retrying the upload. Defaults to 5.0.
        :type backoff_factor: float, optional
        :param connect_timeout: The connection timeout for the upload. Defaults to 60.
        :type connect_timeout: int, optional
        :param read_timeout: The read timeout for the upload. Defaults to 600.
        :type read_timeout: int, optional
        :raises Exception: If the upload fails.
        :returns: The uploaded object part.
        :rtype: ObjectPart
        """
        with open(file_path, "rb") as f:
            f.seek(offset)
            data = f.read(size)
            attempt_count = 0
            response = None
            headers = None

            log_id = str(log_id)
            object_part = self.app.create.log_object_part(
                log_id=log_id,
                object_key=object_key,
                size=size,
                part_number=part_number,
            ).data
            upload_object_data_url = object_part.presigned_url

            if verify_integrity:
                part_hash = base64.b64encode(struct.pack(">I", crc32c.crc32c(data)))
                headers = {"x-amz-checksum-crc32c": part_hash}
            last_exception = None
            for attempt_count in range(1, max_attempts + 1):
                if attempt_count > 1:
                    self.app.logger.debug(
                        f"Retrying upload of part {part_number} of object {object_key} in log {log_id} (attempt {attempt_count}/{max_attempts})."
                    )
                try:
                    headers = None
                    response = requests.put(
                        upload_object_data_url,
                        data=data,
                        headers=headers,
                        timeout=(connect_timeout, read_timeout),
                    )
                    response.raise_for_status()
                    break
                except Exception as e:
                    last_exception = e
                    self.app.logger.debug(
                        f"Error while uploading part {part_number} of object {object_key} in log {log_id} (attempt {attempt_count}/{max_attempts}): {e}"
                    )
                    time.sleep(backoff_factor * (2 ** (attempt_count - 1)))
                    continue

        if response is None:
            raise Exception(
                f"Failed to upload part {part_number} of object {object_key} in log {log_id} after {max_attempts} attempts. Last exception: {last_exception}"
            )

        if response.status_code != 200:
            raise Exception(f"Error while uploading object part: {response.text}")

        return self.app.fetch.log_object_part(
            log_id=log_id,
            object_key=object_key,
            part_number=part_number,
        ).data

    def list_all_log_object_parts(
        self,
        log_id: str,
        object_key: str,
    ) -> list["ObjectPart"]:
        """
        List all parts of a log object.

        :param log_id: The log id to list the object parts of.
        :type log_id: str
        :param object_key: The key of the object to list the parts of.
        :type object_key: str
        :returns: The list of object parts.
        :rtype: list[ObjectPart]
        """

        log_object_parts: List[ObjectPart] = []
        parts_res = self.app.list.log_object_part(log_id=log_id, object_key=object_key)
        log_object_parts += parts_res.data
        while parts_res.is_truncated:
            parts_res = self.app.list.log_object_part(
                log_id=log_id,
                object_key=object_key,
                part_number_marker=parts_res.next_part_number_marker,
            )
            log_object_parts += parts_res.data
        log_object_parts.sort(key=attrgetter("part_number"))

        return log_object_parts

    def upload_log_object(
        self,
        log_id: str,
        file_path: str,
        object_key: Optional[str] = None,
        key_replacement: tuple[str, str] = None,
        key_prefix: str = None,
        part_size: Optional[int] = None,
        max_workers: int = 32,
        skip_if_exists: bool = False,
        continue_upload: bool = False,
        skip_if_complete: bool = True,
        overwrite: bool = False,
        show_progress: bool = True,
        verify_integrity: bool = True,
        manage_memory: bool = True,
        connect_timeout: int = 60,
        read_timeout: int = 600,
    ) -> tuple["Object", list["ObjectPart"]]:
        """
        Upload a file to a log.

        The file is uploaded as a log object, meaning it is associated with a single log given by log_id.
        The file is split into parts of size part_size, which are uploaded in parallel using a maximum of max_workers workers.
        If no part_size is provided, the part size will be determined based on the file size to try to optimize the upload.
        If manage_memory is set to True, the upload will try to avoid using too much memory by limiting the number of parts that are uploaded in parallel.
        Note that larger values for part_size and max_workers will generally result in faster uploads, but may also result in higher memory usage.

        If skip_if_exists is set to True, the upload will be skipped if the object already exists.
        If continue_upload is set to True, any existing parts of the object will be skipped and the upload will continue from where it left off.
        If continue_upload is set to True and skip_if_complete is set to True, the upload will be skipped if the object is already complete.
        If overwrite is set to True, any existing object with the same key will be deleted before the upload.

        :param log_id: The log id to upload the object to.
        :type log_id: str
        :param file_path: The path to the file to upload.
        :type file_path: str
        :param object_key: The key to use for the object. Defaults to None.
        :type object_key: str, optional
        :param key_replacement: A tuple of strings to replace in the object key. Defaults to None.
        :type key_replacement: tuple[str, str], optional
        :param key_prefix: A prefix to add to the object key. Defaults to None.
        :type key_prefix: str, optional
        :param part_size: The size of each part to upload in bytes. Defaults to None, which means the part size will be calculated based on the file size.
        :type part_size: int, optional
        :param max_workers: The maximum number of workers to use for parallel uploads. Defaults to 32.
        :type max_workers: int, optional
        :param skip_if_exists: Whether to skip the upload if the object already exists. Defaults to False.
        :type skip_if_exists: bool, optional
        :param continue_upload: Whether to continue an existing upload. Defaults to True.
        :type continue_upload: bool, optional
        :param skip_if_complete: Whether to skip the continued upload if the object is already complete. Defaults to True.
        :type skip_if_complete: bool, optional
        :param overwrite: Whether to overwrite the object if it already exists. Defaults to False.
        :type overwrite: bool, optional
        :param show_progress: Whether to show a progress bar for the upload. Defaults to True.
        :type show_progress: bool, optional
        :param verify_integrity: Whether to verify the integrity of the uploaded object. Defaults to True.
        :type verify_integrity: bool, optional
        :param manage_memory: Whether to try to manage memory usage during the upload. Defaults to True.
        :type manage_memory: bool, optional
        :param connect_timeout: The connection timeout for the upload. Defaults to 60.
        :type connect_timeout: int, optional
        :raises ConflictException: If existing resources conflict with the upload.
        :returns: The uploaded object and its parts.
        :rtype: tuple[Object, list[ObjectPart]]
        """

        # Validate parameters
        if max_workers <= 0 or not isinstance(max_workers, int):
            raise ValueError("max_workers must be an integer greater than 0.")

        if continue_upload and overwrite:
            raise Exception(
                "Only one one of continue_upload, overwrite can be set to true"
            )

        ABS_MIN_PART_SIZE = 5 * 1024 * 1024
        ABS_MAX_PART_SIZE = 5 * 1024 * 1024 * 1024
        ABS_MAX_NUMBER_OF_PARTS = 10_000
        OPTIMAL_PART_SIZE = 10 * 1024 * 1024
        MAX_MEMORY_HIT_COUNT = 60
        object_size = os.path.getsize(file_path)

        if part_size is None:
            # determining the optimal part size is tricky
            # we want to minimize the number of parts to avoid overhead,
            # but we want to reduce the chance of failures due to connection issues
            # we've found that a part size of 10MB is a good compromise
            expected_number_of_parts = object_size // (OPTIMAL_PART_SIZE + 1)
            if expected_number_of_parts <= ABS_MAX_NUMBER_OF_PARTS:
                part_size = OPTIMAL_PART_SIZE
            else:
                # if the object is too large, we need to increase the part size
                # to avoid hitting the maximum number of parts
                part_size = object_size // (ABS_MAX_NUMBER_OF_PARTS + 1)
            if part_size < ABS_MIN_PART_SIZE:
                part_size = ABS_MIN_PART_SIZE
            if part_size > ABS_MAX_PART_SIZE:
                part_size = ABS_MAX_PART_SIZE
        number_of_parts = object_size // part_size + 1

        if part_size < ABS_MIN_PART_SIZE:
            raise ValueError(f"part_size must be at least {ABS_MIN_PART_SIZE} bytes.")
        if part_size > ABS_MAX_PART_SIZE:
            raise ValueError(f"part_size must be at most {ABS_MAX_PART_SIZE} bytes.")
        number_of_parts = object_size // part_size + 1
        if number_of_parts > ABS_MAX_NUMBER_OF_PARTS:
            raise ValueError(
                f"part_size is too small for object size {object_size}. "
                f"part_size must be at least {object_size // ABS_MAX_NUMBER_OF_PARTS} bytes."
            )

        if object_key is None:
            object_key = file_path.split("/")[-1]
        if key_replacement is not None:
            object_key = object_key.replace(*key_replacement)
        if key_prefix is not None:
            object_key = os.path.join(key_prefix, object_key)
        if object_key.startswith("/"):
            object_key = object_key[1:]

        self.app.logger.debug(
            f"Using part_size {part_size} with {number_of_parts} parts for object {object_key} of size {object_size} in log {log_id}."
        )

        # First, create/re-create/fetch/etc. the log object

        log_id = str(log_id)
        try:
            log_object = self.app.create.log_object(
                log_id=log_id,
                key=object_key,
            ).data
        except ConflictException as e:
            if skip_if_exists:
                self.app.logger.debug(
                    f"Skipping upload of object {object_key} in log {log_id}."
                )
                log_object = self.app.fetch.log_object(
                    log_id=log_id, object_key=object_key
                ).data
                return log_object, []

            if continue_upload:
                self.app.logger.debug(
                    f"Continuing upload of object {object_key} in log {log_id}."
                )
                log_object = self.app.fetch.log_object(
                    log_id=log_id, object_key=object_key
                ).data
                if log_object.upload_state == UploadState.complete:
                    if skip_if_complete:
                        self.app.logger.debug(
                            f"Skipping complete upload of object {object_key} in log {log_id}."
                        )
                        return log_object, []
                    else:
                        raise ConflictException(
                            f"Can't continue upload: Upload of Object {object_key} in log {log_id} is already complete."
                        )
            elif overwrite:
                self.app.logger.debug(
                    f"Overwriting object {object_key} in log {log_id}."
                )
                self.app.delete.log_object(log_id=log_id, object_key=object_key)
                log_object = self.app.create.log_object(
                    log_id=log_id,
                    key=object_key,
                ).data
            else:
                raise e

        # Then, handle the part logic
        log_object_parts = self.list_all_log_object_parts(
            log_id=log_id, object_key=object_key
        )
        self.app.logger.debug(
            f"Found {len(log_object_parts)} existing parts for object {object_key} in log {log_id}."
        )
        if not continue_upload and not overwrite:
            if len(log_object_parts) > 0:
                raise ConflictException(
                    f"Object {object_key} in log {log_id} already has {len(log_object_parts)} parts."
                    "Set continue_upload to True to continue the upload or overwrite to start over."
                )

        # Validate existing parts sizes
        for idx, part in enumerate(log_object_parts):
            if part.part_number == number_of_parts:
                # the last part is allowed to be smaller than part_size
                continue
            if part.size == 0:
                # the part exists, but it has no data, so we'll overwrite it anyways
                continue
            if part.size != part_size:
                # in order to keep things simple, we require all parts to be the same size
                # TODO: we could relax this requirement in the future
                raise ConflictException(
                    f"Part {part.part_number} of object {object_key} in log {log_id} has an unexpected size {part.size}."
                    f"All parts except for the last part need to be the same size as the given part_size {part_size}."
                    f"Either overwrite the object to start over or change the part_size to match existing parts or set to None."
                )

        # Upload the parts

        futures: list[Future] = []
        log_object_parts: list[ObjectPart] = []
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            with tqdm(
                total=object_size,
                unit="B",
                unit_scale=True,
                unit_divisor=1024,
                disable=not show_progress,
            ) as pbar:
                for idx in range(0, number_of_parts):
                    offset = idx * part_size
                    size = min(part_size, object_size - offset)
                    part_number = idx + 1

                    # check if we should skip the part
                    existing_part = next(
                        (
                            part
                            for part in log_object_parts
                            if part.part_number == part_number
                        ),
                        None,
                    )
                    if existing_part is not None:
                        if existing_part.size == 0:
                            self.app.logger.debug(
                                f"Overwriting empty part {part_number} of object {object_key} in log {log_id}."
                            )
                        else:
                            self.app.logger.debug(
                                f"Skipping existing part {part_number} of object {object_key} in log {log_id}."
                            )
                            pbar.update(size)
                            continue

                    memory_limit_hit_count = 0
                    while True:
                        if not manage_memory:
                            future = executor.submit(
                                self.upload_log_object_part,
                                log_id=log_id,
                                object_key=object_key,
                                part_number=part_number,
                                file_path=file_path,
                                offset=offset,
                                size=size,
                                verify_integrity=verify_integrity,
                                connect_timeout=connect_timeout,
                                read_timeout=read_timeout,
                            )
                            futures.append(future)
                            break
                        else:
                            # calculate how much memory we have available
                            available_memory = psutil.virtual_memory().available
                            # calculate how much memory the thread will need
                            needed_memory = 2 * part_size
                            # if we have enough memory, start the thread
                            if available_memory > needed_memory:
                                future = executor.submit(
                                    self.upload_log_object_part,
                                    log_id=log_id,
                                    object_key=object_key,
                                    part_number=part_number,
                                    file_path=file_path,
                                    offset=offset,
                                    size=size,
                                    verify_integrity=verify_integrity,
                                    connect_timeout=connect_timeout,
                                    read_timeout=read_timeout,
                                )
                                futures.append(future)
                                break
                            else:
                                self.app.logger.debug(
                                    f"Memory limit reached ({available_memory} available, {needed_memory} needed), waiting for memory to become available."
                                )
                                memory_limit_hit_count += 1
                                if memory_limit_hit_count >= MAX_MEMORY_HIT_COUNT:
                                    raise Exception(
                                        (
                                            f"Memory limit reached ({available_memory} available, {needed_memory} needed)."
                                            " Consider reducing the part size, reducing the number of workers, or freeing up memory."
                                            " Alternatively, set manage_memory to False to disable memory management."
                                        )
                                    )
                            # otherwise, wait a bit and try again
                            time.sleep(1)

                for future in as_completed(futures):
                    part: ObjectPart = future.result()
                    pbar.update(part.size)
                    log_object_parts.append(part)

        # Finally, mark the object as complete to finish the upload
        log_object = self.app.update.log_object(
            log_id=log_id,
            object_key=object_key,
            data={"upload_state": UploadState.complete},
        ).data

        return log_object, log_object_parts

    def upload_log_object_part_from_memory(
        self,
        log_id: str,
        object_key: str,
        part_number: int,
        part_data: Union[bytes, str],
        size: int,
        max_attempts: int = 3,
        backoff_factor: float = 5.0,
        connect_timeout: int = 60,
        read_timeout: int = 600,
    ):
        """
        Upload a part of a file to a log object.

        :param log_id: The log id to upload the object part to.
        :type log_id: str
        :param object_key: The key of the object to upload the part to.
        :type object_key: str
        :param part_number: The part number of the object part.
        :type part_number: int
        :param part_data: The data to upload.
        :type part_data: bytes | str
        :param size: The size of the part to upload.
        :type size: int
        :param max_attempts: The maximum number of attempts to upload the part. Defaults to 3.
        :type max_attempts: int, optional
        :param backoff_factor: The backoff factor for retrying the upload. Defaults to 5.0.
        :type backoff_factor: float, optional
        :param connect_timeout: The connection timeout for the upload. Defaults to 60.
        :type connect_timeout: int, optional
        :param read_timeout: The read timeout for the upload. Defaults to 600.
        :type read_timeout: int, optional
        :raises Exception: If the upload fails.
        :returns: The uploaded object part.
        :rtype: ObjectPart
        """
        log_id = str(log_id)
        object_part = self.app.create.log_object_part(
            log_id=log_id,
            object_key=object_key,
            size=size,
            part_number=part_number,
        ).data
        upload_object_data_url = object_part.presigned_url

        attempt_count = 0
        response = None
        last_error = None
        for attempt_count in range(1, max_attempts + 1):
            if attempt_count > 1:
                self.app.logger.debug(
                    f"Retrying upload of part {part_number} of object {object_key} in log {log_id} (attempt {attempt_count}/{max_attempts})."
                )
            try:
                response = requests.put(
                    upload_object_data_url,
                    data=part_data,
                    timeout=(connect_timeout, read_timeout),
                )
                break
            except Exception as e:
                last_error = e
                self.app.logger.debug(
                    f"Error while uploading part {part_number} of object {object_key} in log {log_id} (attempt {attempt_count}/{max_attempts}): {e}"
                )
                time.sleep(backoff_factor * (2 ** (attempt_count - 1)))
                continue

        if response is None:
            raise Exception(
                f"Failed to upload part {part_number} of object {object_key} in log {log_id} after {max_attempts} attempts. Last error: {last_error}"
            )

        if response.status_code != 200:
            raise Exception(f"Error while uploading object part: {response.text}")

        return self.app.fetch.log_object_part(
            log_id=log_id,
            object_key=object_key,
            part_number=part_number,
        ).data

    def upload_log_object_from_memory(
        self,
        log_id: str,
        file_like: Union[io.BytesIO, io.StringIO],
        object_key: str,
        key_replacement: tuple[str, str] = None,
        key_prefix: str = None,
        part_size: int = 100 * 1024 * 1024,
        max_workers: Optional[int] = 8,
        skip_if_exists: bool = False,
        continue_upload: bool = True,
        skip_if_complete: bool = True,
        overwrite: bool = False,
    ) -> tuple["Object", list["ObjectPart"]]:
        """
        Upload a file-like object to a log.

        The file is uploaded as a log object, meaning it is associated with a single log given by log_id.
        The file is split into parts of size part_size, which are uploaded in parallel using a maximum of max_workers workers.
        Note that larger values for part_size and max_workers will generally result in faster uploads, but may also result in higher memory usage.

        If skip_if_exists is set to True, the upload will be skipped if the object already exists.
        If continue_upload is set to True, any existing parts of the object will be skipped and the upload will continue from where it left off.
        If continue_upload is set to True and skip_if_complete is set to True, the upload will be skipped if the object is already complete.
        If overwrite is set to True, any existing object with the same key will be deleted before the upload.

        :param log_id: The log id to upload the object to.
        :type log_id: str
        :param file_like: The file-like object to upload.
        :type file_like: io.BytesIO | io.StringIO
        :param object_key: The key to use for the object.
        :type object_key: str
        :param key_replacement: A tuple of strings to replace in the object key. Defaults to None.
        :type key_replacement: tuple[str, str], optional
        :param key_prefix: A prefix to add to the object key. Defaults to None.
        :type key_prefix: str, optional
        :param part_size: The size of each part to upload. Defaults to 100 * 1024 * 1024.
        :type part_size: int, optional
        :param max_workers: The maximum number of workers to use for parallel uploads. Defaults to 8.
        :type max_workers: int, optional
        :param skip_if_exists: Whether to skip the upload if the object already exists. Defaults to False.
        :type skip_if_exists: bool, optional
        :param continue_upload: Whether to continue an existing upload. Defaults to True.
        :type continue_upload: bool, optional
        :param skip_if_complete: Whether to skip the continued upload if the object is already complete. Defaults to True.
        :type skip_if_complete: bool, optional
        :param overwrite: Whether to overwrite the object if it already exists. Defaults to False.
        :type overwrite: bool, optional
        :raises ConflictException: If existing resources conflict with the upload.
        :returns: The uploaded object and its parts.
        :rtype: tuple[Object, list[ObjectPart]]
        """

        # First, create/re-create/fetch/etc. the log object
        log_id = str(log_id)
        if key_replacement is not None:
            object_key = object_key.replace(*key_replacement)
        if key_prefix is not None:
            object_key = os.path.join(key_prefix, object_key)
        if object_key.startswith("/"):
            object_key = object_key[1:]

        try:
            log_object = self.app.create.log_object(
                log_id=log_id,
                key=object_key,
            ).data
        except ConflictException as e:
            if skip_if_exists:
                self.app.logger.debug(
                    f"Skipping upload of object {object_key} in log {log_id}."
                )
                log_object = self.app.fetch.log_object(
                    log_id=log_id, object_key=object_key
                ).data
                return log_object, []

            if continue_upload:
                self.app.logger.debug(
                    f"Continuing upload of object {object_key} in log {log_id}."
                )
                log_object = self.app.fetch.log_object(
                    log_id=log_id, object_key=object_key
                ).data
                if log_object.upload_state == UploadState.complete:
                    if skip_if_complete:
                        self.app.logger.debug(
                            f"Skipping complete upload of object {object_key} in log {log_id}."
                        )
                        return log_object, []
                    else:
                        raise ConflictException(
                            f"Can't continue upload: Upload of Object {object_key} in log {log_id} is already complete."
                        )
            elif overwrite:
                self.app.logger.debug(
                    f"Overwriting object {object_key} in log {log_id}."
                )
                self.app.delete.log_object(log_id=log_id, object_key=object_key)
                log_object = self.app.create.log_object(
                    log_id=log_id,
                    key=object_key,
                ).data
            else:
                raise e

        # Then, figure out which parts we need to upload
        if isinstance(file_like, io.StringIO):
            object_size = len(file_like.getvalue())
        elif isinstance(file_like, io.BytesIO):
            object_size = file_like.getbuffer().nbytes
        else:
            raise TypeError(
                "file_like must be an instance of io.BytesIO or io.StringIO"
            )
        number_of_parts = object_size // part_size + 1
        log_object_parts: List[ObjectPart] = []

        parts_res = self.app.list.log_object_part(log_id=log_id, object_key=object_key)
        log_object_parts += parts_res.data
        while parts_res.is_truncated:
            parts_res = self.app.list.log_object_part(
                log_id=log_id,
                object_key=object_key,
                part_number_marker=parts_res.next_part_number_marker,
            )
            log_object_parts += parts_res.data
        if continue_upload is False:
            if len(log_object_parts) > 0:
                raise ConflictException(
                    f"Object {object_key} in log {log_id} already has {len(log_object_parts)} parts."
                    "Set continue_upload to True to continue the upload or overwrite to start over."
                )
        else:
            self.app.logger.debug(
                f"Found {len(log_object_parts)} existing parts for object {object_key} in log {log_id}."
            )
        log_object_parts.sort(key=attrgetter("part_number"))

        # Validate existing parts sizes
        for idx, part in enumerate(log_object_parts):
            if part.part_number == number_of_parts:
                # the last part is allowed to be smaller than part_size
                continue
            if part.size == 0:
                # the part exists, but it has no data, so we'll overwrite it anyways
                continue
            if part.size != part_size:
                raise ConflictException(
                    f"Part {part.part_number} of object {object_key} in log {log_id} has an unexpected size {part.size}."
                    f"All parts except for the last part need to be the same size as the given part_size {part_size}."
                    f"Either overwrite the object to start over or change the part_size to match existing parts."
                )

        def should_skip_part(part_number):
            existing_part = next(
                (part for part in log_object_parts if part.part_number == part_number),
                None,
            )
            if existing_part is not None:
                if existing_part.size == 0:
                    self.app.logger.debug(
                        f"Overwriting empty part {part_number} of object {object_key} in log {log_id}."
                    )
                else:
                    self.app.logger.debug(
                        f"Skipping existing part {part_number} of object {object_key} in log {log_id}."
                    )
                    return True
            return False

        # Upload the parts (in parallel if max_workers is set)
        if max_workers is not None:
            futures = []
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                for idx in range(0, number_of_parts):
                    offset = idx * part_size
                    file_like.seek(offset)
                    size = min(part_size, object_size - offset)
                    part_number = idx + 1
                    if should_skip_part(part_number):
                        continue
                    futures.append(
                        executor.submit(
                            self.upload_log_object_part_from_memory,
                            log_id=log_id,
                            object_key=object_key,
                            part_number=part_number,
                            part_data=file_like.read(size),
                            size=size,
                        )
                    )

                for future in futures:
                    log_object_parts.append(future.result())
        else:
            for idx in range(0, number_of_parts):
                offset = idx * part_size
                file_like.seek(offset)
                size = min(part_size, object_size - offset)
                part_number = idx + 1
                if should_skip_part(part_number):
                    continue
                log_object_parts.append(
                    self.upload_log_object_part_from_memory(
                        log_id=log_id,
                        object_key=object_key,
                        part_number=part_number,
                        part_data=file_like.read(size),
                        size=size,
                    )
                )

        # Finally, mark the object as complete to finish the upload
        log_object = self.app.update.log_object(
            log_id=log_id,
            object_key=object_key,
            data={"upload_state": UploadState.complete},
        ).data

        return log_object, log_object_parts

    def upload_log_objects(
        self,
        log_id: str,
        file_dir: str,
        path_filter_regexes: Optional[List[str]] = DEFAULT_PATH_FILTER_REGEXES,
        key_replacement: tuple[str, str] = None,
        key_prefix: str = None,
        part_size: Optional[int] = None,
        max_workers: int = 32,
        skip_if_exists: bool = False,
        continue_upload: bool = True,
        skip_if_complete: bool = True,
        overwrite: bool = False,
        verify_integrity: bool = True,
        fail_if_empty_dir: bool = True,
        fail_if_empty_file: bool = True,
        skip_if_empty_file: bool = False,
        warn_if_empty_file: bool = True,
        manage_memory: bool = True,
        connect_timeout: int = 60,
        read_timeout: int = 600,
    ) -> List[tuple["Object", list["ObjectPart"]]]:
        """
        Upload a directory of files to a log.

        The files are uploaded as log objects, meaning they are associated with a single log given by log_id.
        The files are split into parts of size part_size, which are uploaded in parallel using a maximum of max_workers workers.
        If no part_size is provided, the part size will be determined based on the file size to try to optimize the upload.
        Note that larger values for part_size and max_workers will generally result in faster uploads, but may also result in higher memory usage and connection issues.

        If skip_if_exists is set to True, the upload will be skipped if the object already exists.
        If continue_upload is set to True, any existing parts of the object will be skipped and the upload will continue from where it left off.
        If continue_upload is set to True and skip_if_complete is set to True, the upload will be skipped if the object is already complete.
        If overwrite is set to True, any existing object with the same key will be deleted before the upload.

        :param log_id: The log id to upload the objects to.
        :type log_id: str
        :param file_dir: The path to the directory to upload.
        :type file_dir: str
        :param path_filter_regexes: A list of regular expressions to match file paths. Defaults to ``DEFAULT_PATH_FILTER_REGEXES``.
        :type path_filter_regexes: List[str], optional
        :param key_replacement: A tuple of strings to replace in the object keys. Defaults to None.
        :type key_replacement: tuple[str, str], optional
        :param key_prefix: A prefix to add to the object keys. Defaults to None.
        :type key_prefix: str, optional
        :param part_size: The size of each part to upload. Defaults to None, which means the part size will be calculated based on the file size.
        :type part_size: int, optional
        :param max_workers: The maximum number of workers to use for parallel uploads. Defaults to 32.
        :type max_workers: int, optional
        :param skip_if_exists: Whether to skip the upload if the object already exists. Defaults to False.
        :type skip_if_exists: bool, optional
        :param continue_upload: Whether to continue an existing upload. Defaults to True.
        :type continue_upload: bool, optional
        :param skip_if_complete: Whether to skip the continued upload if the object is already complete. Defaults to True.
        :type skip_if_complete: bool, optional
        :param overwrite: Whether to overwrite the object if it already exists. Defaults to False.
        :type overwrite: bool, optional
        :param verify_integrity: Whether to verify the integrity of the uploaded objects. Defaults to True.
        :type verify_integrity: bool, optional
        :param fail_if_empty_dir: Whether to raise an exception if no files are found in the directory. Defaults to True.
        :type fail_if_empty_dir: bool, optional
        :param fail_if_empty_file: Whether to raise an exception if a file is empty. Defaults to True.
        :type fail_if_empty_file: bool, optional
        :param skip_if_empty_file: Whether to skip the upload if a file is empty. Defaults to False.
        :type skip_if_empty_file: bool, optional
        :param warn_if_empty_file: Whether to log a warning if a file is empty. Defaults to True.
        :type warn_if_empty_file: bool, optional
        :param manage_memory: Whether to try to manage memory usage during the upload. Defaults to True.
        :type manage_memory: bool, optional
        :param connect_timeout: The connection timeout for the upload. Defaults to 60.
        :type connect_timeout: int, optional
        :raises Exception: If no files are found in the directory and fail_if_empty_dir is True.
        :returns: A list of tuples of uploaded objects and their parts.
        :rtype: list[tuple[Object, list[ObjectPart]]]
        """
        if isinstance(path_filter_regexes, str):
            path_filter_regexes = [path_filter_regexes]
        log_id = str(log_id)
        upload_result_sets = []
        for file_path in Path(file_dir).rglob("*"):
            if path_filter_regexes is not None:
                filter_match = False
                for path_filter_regex in path_filter_regexes:
                    if re.search(path_filter_regex, str(file_path)):
                        filter_match = True
                        break
                if not filter_match:
                    self.app.logger.debug(
                        f"Skipping file {file_path} based on path_filter_regexes."
                    )
                    continue
            if os.path.isfile(file_path):
                if os.path.getsize(file_path) == 0:
                    if fail_if_empty_file:
                        raise Exception(f"File {file_path} is empty.")
                    elif skip_if_empty_file:
                        self.app.logger.debug(f"Skipping empty file {file_path}.")
                        continue
                    elif warn_if_empty_file:
                        self.app.logger.warning(f"Uploading empty file {file_path}.")
                    else:
                        self.app.logger.debug(f"Uploading empty file {file_path}.")
                object_key = str(file_path)
                if key_replacement is not None:
                    object_key = object_key.replace(*key_replacement)
                if key_prefix is not None:
                    object_key = os.path.join(key_prefix, object_key)
                if object_key.startswith("/"):
                    object_key = object_key[1:]
                upload_result = self.upload_log_object(
                    log_id=log_id,
                    file_path=file_path,
                    object_key=object_key,
                    part_size=part_size,
                    max_workers=max_workers,
                    skip_if_exists=skip_if_exists,
                    continue_upload=continue_upload,
                    skip_if_complete=skip_if_complete,
                    overwrite=overwrite,
                    verify_integrity=verify_integrity,
                    manage_memory=manage_memory,
                    connect_timeout=connect_timeout,
                    read_timeout=read_timeout,
                )
                upload_result_sets.append(upload_result)
        if fail_if_empty_dir and len(upload_result_sets) == 0:
            raise Exception(f"No files found in {file_dir}")
        return upload_result_sets

    def find_local_logs(
        self,
        root_dir: str,
        log_file_regexes: List[str] = DEFAULT_LOG_FILE_REGEXES,
        max_depth: Optional[int] = None,
    ) -> List[dict]:
        """
        Generate a list of log parameters from a directory of log files.

        This function searches the root directory for log files using the given regular expressions. The log parameters include the log_path, log_directory, log_name, and group_name.
        The log_name and group_name are extracted from the corresponding named capture groups of the regular expression.
        If the log_name captured group is followed by a slash, the log directory is also extracted, otherwise it is set to None.

        :param root_dir: The directory to search for log files.
        :type root_dir: str
        :param log_file_regexes: A list of regular expressions to match log files. Defaults to DEFAULT_LOG_FILE_REGEXES.
        :type log_file_regexes: List[str], optional
        :param max_depth: The maximum depth to search for log files. Defaults to None.
        :type max_depth: int, optional
        :returns: A list of log parameters.
        :rtype: List[dict]
        """
        if isinstance(log_file_regexes, str):
            log_file_regexes = [log_file_regexes]

        log_param_sets = []
        for dir_path, dir_names, file_names in os.walk(root_dir):
            if (
                max_depth is not None
                and dir_path.count("/") - root_dir.count("/") > max_depth
            ):
                continue
            for file_name in file_names:
                file_path = os.path.join(dir_path, file_name)
                for log_file_regex in log_file_regexes:
                    re_match = re.search(log_file_regex, file_path)
                    if re_match:
                        re_params = re_match.groupdict()
                        log_name = re_params.get("log_name")
                        group_name = re_params.get("group_name")
                        log_dir = None
                        try:
                            r_index = re_match.end(1)
                        except IndexError as e:
                            raise Exception(
                                f"Log file regex {log_file_regex} must contain a named capture group 'log_name'."
                            ) from e
                        slash_index = file_path.find("/", r_index)
                        if slash_index != -1:
                            log_dir = file_path[: slash_index + 1]

                        log_params = {
                            "log_path": file_path,
                            "log_dir": log_dir,
                            "log_name": log_name,
                            "group_name": group_name,
                        }
                        log_param_sets.append(log_params)
                        break
        return log_param_sets

    def sync_log_objects(
        self,
        root_dir: str,
        log_file_regexes: List[str] = DEFAULT_LOG_FILE_REGEXES,
        path_filter_regexes: Optional[List[str]] = DEFAULT_PATH_FILTER_REGEXES,
        max_depth: Optional[int] = None,
        group_id: Optional[str] = None,
        group_name: Optional[str] = None,
        create_group_if_missing: bool = True,
        group_note: Optional[str] = None,
        group_context: Optional[dict] = None,
        log_id: Optional[str] = None,
        log_name: Optional[str] = None,
        create_log_if_missing: bool = True,
        log_note: Optional[str] = None,
        log_context: Optional[dict] = None,
        key_prefix: str = None,
        part_size: Optional[int] = None,
        max_workers: int = 32,
        skip_if_exists: bool = False,
        continue_upload: bool = True,
        skip_if_complete: bool = True,
        overwrite: bool = False,
        verify_integrity: bool = True,
        manage_memory: bool = True,
        connect_timeout: int = 60,
        read_timeout: int = 600,
        fail_if_empty_file: bool = True,
        skip_if_empty_file: bool = False,
        warn_if_empty_file: bool = True,
        create_ingestions: bool = True,
        skip_existing_ingestions: bool = True,
        ingestion_state: ProcessState = ProcessState.queued,
        ingestion_note: Optional[str] = None,
        ingestion_context: Optional[dict] = None,
        ingestion_workflow_id: Optional[str] = None,
        ingestion_workflow_context: Optional[dict] = None,
        retry_count: Optional[int] = None,
        verbosity: Optional[str] = "info",
    ) -> int:
        """
        Sync log files from a local directory to LogQS.

        This function searches the root directory for log files using the given regular expressions. It then uploads
        the log files to LogQS and, optionally, creates ingestions for them.

        The name used for the LogQS log resource of a found log file is extracted from the first capture group of the
        regular expression. If the captured group is followed by a slash, the log directory is also extracted.

        If the log with the extracted name does not exist in the group, it is created. If the group does not exist,
        it is created if ``create_group_if_missing`` is True.

        If ``log_id`` or ``log_name`` is provided, the logs are uploaded to the specified log instead of the log
        given by the name captured when finding the log files. Similarly, if the ``group_id`` is not provided,
        ``group_name`` is used to find or create the group.

        If ``create_ingestions`` is True, ingestions are created for the logs. If ``skip_existing_ingestions`` is
        True, ingestions are only created for logs that don't already have corresponding ingestions.

        :param root_dir: The directory to search for log files.
        :type root_dir: str
        :param log_file_regexes: A list of regular expressions to match log files. Defaults to ``DEFAULT_LOG_FILE_REGEXES```.
        :type log_file_regexes: List[str], optional
        :param path_filter_regexes: A list of regular expressions to match file paths. Defaults to ``DEFAULT_PATH_FILTER_REGEXES``.
        :type path_filter_regexes: List[str], optional
        :param max_depth: The maximum depth to search for log files. Defaults to None.
        :type max_depth: int, optional
        :param group_id: The group id to upload the logs to. Defaults to None.
        :type group_id: str, optional
        :param group_name: The group name to upload the logs to. Defaults to None.
        :type group_name: str, optional
        :param create_group_if_missing: Whether to create the group if it doesn't exist. Defaults to True.
        :type create_group_if_missing: bool, optional
        :param group_note: A note to use when creating the group. Defaults to None.
        :type group_note: str, optional
        :param group_context: A context to use when creating the group. Defaults to None.
        :type group_context: dict, optional
        :param log_id: The log id to upload the logs to. Defaults to None.
        :type log_id: str, optional
        :param log_name: The log name to upload the logs to. Defaults to None.
        :type log_name: str, optional
        :param create_log_if_missing: Whether to create the log if it doesn't exist. Defaults to True.
        :type create_log_if_missing: bool, optional
        :param log_note: A note to use when creating the log. Defaults to None.
        :type log_note: str, optional
        :param log_context: A context to use when creating the log. Defaults to None.
        :type log_context: dict, optional
        :param key_prefix: A prefix to add to the object keys. Defaults to None.
        :type key_prefix: str, optional
        :param part_size: The size of each part to upload. Defaults to None, which means the part size will be calculated based on the file size.
        :type part_size: int, optional
        :param max_workers: The maximum number of workers to use for parallel uploads. Defaults to 32.
        :type max_workers: int, optional
        :param skip_if_exists: Whether to skip the upload if the object already exists. Defaults to False.
        :type skip_if_exists: bool, optional
        :param continue_upload: Whether to continue an existing upload. Defaults to True.
        :type continue_upload: bool, optional
        :param skip_if_complete: Whether to skip the continued upload if the object is already complete. Defaults to True.
        :type skip_if_complete: bool, optional
        :param overwrite: Whether to overwrite the object if it already exists. Defaults to False.
        :type overwrite: bool, optional
        :param verify_integrity: Whether to verify the integrity of the uploaded objects. Defaults to True.
        :type verify_integrity: bool, optional
        :param manage_memory: Whether to try to manage memory usage during the upload. Defaults to True.
        :type manage_memory: bool, optional
        :param connect_timeout: The connection timeout for the upload. Defaults to 60.
        :type connect_timeout: int, optional
        :param read_timeout: The read timeout for the upload. Defaults to 600.
        :type read_timeout: int, optional
        :param fail_if_empty_file: Whether to raise an exception if a file is empty. Defaults to True.
        :type fail_if_empty_file: bool, optional
        :param skip_if_empty_file: Whether to skip the upload if a file is empty. Defaults to False.
        :type skip_if_empty_file: bool, optional
        :param warn_if_empty_file: Whether to log a warning if a file is empty. Defaults to True.
        :type warn_if_empty_file: bool, optional
        :param create_ingestions: Whether to create ingestions for the logs. Defaults to True.
        :type create_ingestions: bool, optional
        :param skip_existing_ingestions: Whether to skip creating ingestions for logs that already have ingestions. Defaults to True.
        :type skip_existing_ingestions: bool, optional
        :param ingestion_state: The state to set for the ingestions. Defaults to ProcessState.queued.
        :type ingestion_state: ProcessState, optional
        :param ingestion_note: A note to add to the ingestions. Defaults to None.
        :type ingestion_note: str, optional
        :param ingestion_context: A context to add to the ingestions. Defaults to None.
        :type ingestion_context: dict, optional
        :param ingestion_workflow_id: The workflow id to use when creating the ingestions. Defaults to None.
        :type ingestion_workflow_id: str, optional
        :param ingestion_workflow_context: The workflow context to use when creating the ingestions. Defaults to None.
        :type ingestion_workflow_context: dict, optional
        :param retry_count: The number of times to retry creating the ingestions. Defaults to None, which falls back to the client's configured retry count.
        :type retry_count: int, optional
        :param verbosity: The verbosity level to use. One of "debug", "info", or "error". Defaults to "info".
        :type verbosity: str, optional

        :returns: The number of uploaded log files.
        :rtype: int
        """

        def logger(msg):
            if verbosity is not None:
                getattr(self.app.logger, verbosity.lower())(msg)

        if retry_count is not None:
            if not isinstance(retry_count, int):
                raise TypeError("retry_count must be an integer.")
            if retry_count < 0:
                raise ValueError("retry_count must be greater than or equal to zero.")
            self.app.config.retry_count = retry_count

        # First, figure out which group/log we're working with
        group = None
        if group_id is not None or group_name is not None:
            group = self.fetch_by_name_or_create(
                resource_type="group",
                resource_id=group_id,
                resource_name=group_name,
                list_params={},
                create_if_missing=create_group_if_missing,
                create_params={"note": group_note, "context": group_context},
                create_func=self.app.create.group,
                list_func=self.app.list.group,
                fetch_func=self.app.fetch.group,
            )
        if group is None:
            logger(
                "No group ID or name provided; will find/create groups based on found log parameters."
            )

        log = None
        if group is not None:
            if log_id is not None or log_name is not None:
                log = self.fetch_by_name_or_create(
                    resource_type="log",
                    resource_id=log_id,
                    resource_name=log_name,
                    list_params={"group_id": group.id},
                    create_if_missing=create_log_if_missing,
                    create_params={
                        "group_id": group.id,
                        "note": log_note,
                        "context": log_context,
                    },
                    create_func=self.app.create.log,
                    list_func=self.app.list.log,
                    fetch_func=self.app.fetch.log,
                )
            if log is None:
                logger(
                    "No log ID or name provided; will find/create logs based on found log parameters."
                )

        # Next, we find all the log files in the root directory
        log_param_sets = self.find_local_logs(
            root_dir=root_dir,
            log_file_regexes=log_file_regexes,
            max_depth=max_depth,
        )
        logger(f"Found {len(log_param_sets)} logs in {root_dir}")

        # for each log, we check if the log already exists in the group
        uploaded_file_count = 0
        for params in log_param_sets:
            sync_group = None
            sync_log = None

            log_name_param = params.get("log_name")
            group_name_param = params.get("group_name")
            log_dir_param = params.get("log_dir")
            log_path_param = params.get("log_path")

            if log_path_param.endswith(".jsonl"):
                # if the log_path_param points to a JSONL file, we attempt to parse it as a JSONLLog
                jsonl_log = JSONLLog()
                jsonl_log.load_jsonl_file(log_path_param)
                if jsonl_log.header:
                    header_log_name = jsonl_log.header.log_name
                    header_group_name = jsonl_log.header.group_name
                    jsonl_group = self.fetch_by_name_or_create(
                        resource_type="group",
                        resource_name=header_group_name,
                        create_if_missing=create_group_if_missing,
                        create_params={
                            "note": jsonl_log.header.group_note,
                            "context": jsonl_log.header.group_context,
                        },
                        create_func=self.app.create.group,
                        list_func=self.app.list.group,
                        fetch_func=self.app.fetch.group,
                    )
                    sync_log = self.fetch_by_name_or_create(
                        resource_type="log",
                        resource_name=header_log_name,
                        list_params={"group_id": jsonl_group.id},
                        create_if_missing=create_log_if_missing,
                        create_params={
                            "group_id": jsonl_group.id,
                            "note": jsonl_log.header.log_note,
                            "context": jsonl_log.header.log_context,
                        },
                        create_func=self.app.create.log,
                        list_func=self.app.list.log,
                        fetch_func=self.app.fetch.log,
                    )
                    logger(
                        f"Using JSONL header defined log {sync_log.name} ({sync_log.id}) in group {jsonl_group.name} ({jsonl_group.id})"
                    )

            if sync_group is None and group is None:
                groups = self.app.list.group(name=group_name_param).data
                if len(groups) == 0:
                    logger(f"Creating group {group_name_param}")
                    sync_group = self.app.create.group(
                        name=group_name_param,
                        note=group_note,
                        context=group_context,
                    ).data
                else:
                    sync_group = groups[0]
            elif sync_group is None and group is not None:
                sync_group = group

            if sync_log is None and log is None:
                sync_log = self.fetch_by_name_or_create(
                    resource_type="log",
                    resource_name=log_name_param,
                    list_params={"group_id": sync_group.id},
                    create_if_missing=create_log_if_missing,
                    create_params={
                        "group_id": sync_group.id,
                        "note": log_note,
                        "context": log_context,
                    },
                    create_func=self.app.create.log,
                    list_func=self.app.list.log,
                    fetch_func=self.app.fetch.log,
                )
            elif sync_log is None and log is not None:
                sync_log = log

            # for each log, we upload the log files
            logger(f"Uploading log files for log {sync_log.name} ({sync_log.id})")
            log_object_key = None
            if log_dir_param is not None:
                key_replacement = (log_dir_param, "")
                log_object_sets = self.upload_log_objects(
                    log_id=sync_log.id,
                    file_dir=log_dir_param,
                    path_filter_regexes=path_filter_regexes,
                    key_replacement=key_replacement,
                    key_prefix=key_prefix,
                    part_size=part_size,
                    max_workers=max_workers,
                    skip_if_exists=skip_if_exists,
                    continue_upload=continue_upload,
                    skip_if_complete=skip_if_complete,
                    overwrite=overwrite,
                    verify_integrity=verify_integrity,
                    fail_if_empty_file=fail_if_empty_file,
                    skip_if_empty_file=skip_if_empty_file,
                    warn_if_empty_file=warn_if_empty_file,
                    manage_memory=manage_memory,
                    connect_timeout=connect_timeout,
                    read_timeout=read_timeout,
                )
                uploaded_file_count += len(log_object_sets)
                log_file_name = log_path_param.split("/")[-1]
                for log_object, _ in log_object_sets:
                    if log_file_name in log_object.key:
                        log_object_key = log_object.key
                        break
                if log_object_key is None:
                    raise Exception(
                        f"Log file {log_file_name} not found in uploaded objects."
                    )
            else:
                log_object, _ = self.upload_log_object(
                    log_id=sync_log.id,
                    file_path=log_path_param,
                    part_size=part_size,
                    max_workers=max_workers,
                    skip_if_exists=skip_if_exists,
                    continue_upload=continue_upload,
                    skip_if_complete=skip_if_complete,
                    overwrite=overwrite,
                    verify_integrity=verify_integrity,
                    manage_memory=manage_memory,
                    connect_timeout=connect_timeout,
                    read_timeout=read_timeout,
                )
                uploaded_file_count += 1
                log_object_key = log_object.key
            logger(
                f"Log object key {log_object_key} uploaded for log {sync_log.name} ({sync_log.id})"
            )

            # for each log, we create an ingestion
            if create_ingestions:
                ingestions = self.app.list.ingestion(
                    log_id=sync_log.id, object_key_like=log_object_key
                ).data
                if len(ingestions) == 0 or not skip_existing_ingestions:
                    ingestion = self.app.create.ingestion(
                        log_id=sync_log.id,
                        object_key=log_object_key,
                        name=sync_log.name,
                        note=ingestion_note,
                        state=ingestion_state,
                        context=ingestion_context,
                        workflow_id=ingestion_workflow_id,
                        workflow_context=ingestion_workflow_context,
                    ).data
                    logger(
                        f"Ingestion {ingestion.id} created for log {sync_log.name} ({sync_log.id}) for {log_object_key}"
                    )

        logger(f"Uploaded {uploaded_file_count} log files")
        return uploaded_file_count

    # Downloading

    def get_object_meta(
        self,
        object_key: str,
        object_store_id: Optional[str] = None,
        log_id: Optional[str] = None,
        offset: int = 0,
        length: Optional[int] = None,
    ) -> Object:
        """
        Get the metadata for either a Log Object or an Object Store Object.

        :param object_key: The key of the object.
        :type object_key: str
        :param object_store_id: The object store id to use. Defaults to None.
        :type object_store_id: str, optional
        :param log_id: The log id to use. Defaults to None.
        :type log_id: str, optional
        :param offset: The offset to use. Defaults to 0.
        :type offset: int, optional
        :param length: The length to use. Defaults to None.
        :type length: int, optional
        :raises ValueError: If both object_store_id and log_id are provided.
        :raises ValueError: If neither object_store_id nor log_id are provided.
        :returns: The object metadata.
        :rtype: Object
        """
        if object_store_id is None:
            if log_id is None:
                raise ValueError("Either object_store_id or log_id must be provided.")
        elif log_id is not None:
            raise ValueError("Only one of object_store_id or log_id can be provided.")

        if object_store_id is not None:
            object_meta = self.app.fetch.object(
                object_key=object_key,
                object_store_id=object_store_id,
                redirect=False,
                offset=offset,
                length=length,
            ).data
        else:
            object_meta = self.app.fetch.log_object(
                object_key=object_key,
                log_id=log_id,
                redirect=False,
                offset=offset,
                length=length,
            ).data

        return object_meta

    def fetch_object_data_part(
        self,
        offset: int,
        length: int,
        object_key: str,
        object_store_id: Optional[str] = None,
        log_id: Optional[str] = None,
        max_attempts: int = 3,
        backoff_factor: float = 5.0,
        connect_timeout: int = 60,
        read_timeout: int = 600,
        data_container: Optional[bytearray] = None,
    ) -> tuple[bytearray, int]:
        """
        Fetch a part of an object's data.

        :param offset: The offset to start downloading from.
        :type offset: int
        :param length: The length of the data to download.
        :type length: int
        :param object_key: The key of the object.
        :type object_key: str
        :param object_store_id: The object store id to use. Defaults to None.
        :type object_store_id: str, optional
        :param log_id: The log id to use. Defaults to None.
        :type log_id: str, optional
        :param max_attempts: The maximum number of attempts to make. Defaults to 3.
        :type max_attempts: int, optional
        :param backoff_factor: The backoff factor to use. Defaults to 5.0.
        :type backoff_factor: float, optional
        :param connect_timeout: The connect timeout to use. Defaults to 60.
        :type connect_timeout: int, optional
        :param read_timeout: The read timeout to use. Defaults to 600.
        :type read_timeout: int, optional
        :param data_container: A bytearray to use as a container for the fetched data. Defaults to None.
        :type data_container: bytearray, optional
        :returns: The downloaded data and the offset of the data.
        :rtype: tuple[bytearray, int]
        """
        if data_container is None:
            data_container = bytearray(length)
        for attempt_count in range(1, max_attempts + 1):
            try:
                if attempt_count > 1:
                    self.app.logger.debug(
                        f"Retrying object data fetch for {object_key} part {offset}-{offset + length - 1} (attempt {attempt_count}/{max_attempts})"
                    )
                object_meta = self.get_object_meta(
                    object_key=object_key,
                    object_store_id=object_store_id,
                    log_id=log_id,
                    offset=offset,
                    length=length,
                )
                start_offset = offset
                end_offset = offset + length
                headers = {
                    "Range": f"bytes={start_offset}-{end_offset - 1}",
                }
                r = requests.get(
                    object_meta.presigned_url,
                    headers=headers,
                    stream=True,
                    timeout=(connect_timeout, read_timeout),
                )
                r.raise_for_status()
                container_offset = 0
                for chunk in r.iter_content(chunk_size=1024 * 32):  # 32 KB chunks
                    if chunk:
                        data_container[
                            container_offset : container_offset + len(chunk)
                        ] = chunk
                        container_offset += len(chunk)
                break
            except Exception as e:
                if attempt_count == max_attempts:
                    raise e
                self.app.logger.debug(
                    f"Error while fetching object data for {object_key} part {offset}-{offset + length - 1} (attempt {attempt_count}/{max_attempts}): {e}"
                )
                backoff = backoff_factor * (2 ** (attempt_count - 1))
                time.sleep(backoff)
        return data_container, offset

    def iter_object_data_parts(
        self,
        object_key: str,
        object_store_id: Optional[str] = None,
        log_id: Optional[str] = None,
        part_size: int = 100 * 1024 * 1024,
        max_workers: Optional[int] = 10,
        start_offset: int = 0,
        end_offset: Optional[int] = None,
        max_attempts: int = 3,
        backoff_factor: float = 5.0,
        connect_timeout: int = 60,
        read_timeout: int = 600,
        return_as_completed: bool = False,
    ) -> Iterable[tuple[bytearray, int]]:
        """
        Yield parts of an object's data.

        :param object_key: The key of the object.
        :type object_key: str
        :param object_store_id: The object store id to use. Defaults to None.
        :type object_store_id: str, optional
        :param log_id: The log id to use. Defaults to None.
        :type log_id: str, optional
        :param part_size: The size of each part to download. Defaults to 100 * 1024 * 1024.
        :type part_size: int, optional
        :param max_workers: The maximum number of workers to use for parallel downloads. Defaults to 10.
        :type max_workers: int, optional
        :param start_offset: The offset to start downloading from. Defaults to 0.
        :type start_offset: int, optional
        :param end_offset: The offset to stop downloading at. Defaults to None.
        :type end_offset: int, optional
        :param max_attempts: The maximum number of attempts to make. Defaults to 3.
        :type max_attempts: int, optional
        :param backoff_factor: The backoff factor to use. Defaults to 5.0.
        :type backoff_factor: float, optional
        :param connect_timeout: The connect timeout to use. Defaults to 60.
        :type connect_timeout: int, optional
        :param read_timeout: The read timeout to use. Defaults to 600.
        :type read_timeout: int, optional
        :param return_as_completed: Whether to return the results as they are completed. Defaults to False.
        :type return_as_completed: bool, optional
        :yields: The downloaded data and the offset of the data.
        :rtype: Iterable[tuple[bytearray, int]]
        """

        if end_offset is None:
            # If no end_offset is provided, fetch the object metadata to determine the size
            object_meta = self.get_object_meta(
                object_key=object_key,
                object_store_id=object_store_id,
                log_id=log_id,
            )
            end_offset = object_meta.size

        if max_workers is None or max_workers <= 0:
            # Sequential fallback (no threading)
            current = start_offset
            while current < end_offset:
                size = min(part_size, end_offset - current)
                data = self.fetch_object_data_part(
                    offset=current,
                    length=size,
                    object_key=object_key,
                    object_store_id=object_store_id,
                    log_id=log_id,
                    max_attempts=max_attempts,
                    backoff_factor=backoff_factor,
                    connect_timeout=connect_timeout,
                    read_timeout=read_timeout,
                )
                yield data
                current += size
            return

        if return_as_completed:
            # Existing behavior (submit all; memory footprint limited to in‑flight parts since
            # results released right after yield).
            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures: list[Future] = []
                for offset in range(start_offset, end_offset, part_size):
                    size = min(part_size, end_offset - offset)
                    futures.append(
                        executor.submit(
                            self.fetch_object_data_part,
                            offset=offset,
                            length=size,
                            object_key=object_key,
                            object_store_id=object_store_id,
                            log_id=log_id,
                            max_attempts=max_attempts,
                            backoff_factor=backoff_factor,
                            connect_timeout=connect_timeout,
                            read_timeout=read_timeout,
                        )
                    )
                for future in as_completed(futures):
                    yield future.result()
            return

        # Ordered mode with streaming window (memory friendly)
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            in_flight: list[tuple[int, Future]] = []
            next_offset = start_offset

            # Prime initial window
            while next_offset < end_offset and len(in_flight) < max_workers:
                size = min(part_size, end_offset - next_offset)
                fut = executor.submit(
                    self.fetch_object_data_part,
                    offset=next_offset,
                    length=size,
                    object_key=object_key,
                    object_store_id=object_store_id,
                    log_id=log_id,
                    max_attempts=max_attempts,
                    backoff_factor=backoff_factor,
                    connect_timeout=connect_timeout,
                    read_timeout=read_timeout,
                )
                in_flight.append((next_offset, fut))
                next_offset += size

            # Consume in order while continuously scheduling new work
            while in_flight:
                part_offset, fut = in_flight.pop(0)
                data_tuple = fut.result()  # (bytearray, offset)
                yield data_tuple  # consumer should release reference after use
                # Refill window
                if next_offset < end_offset:
                    size = min(part_size, end_offset - next_offset)
                    new_fut = executor.submit(
                        self.fetch_object_data_part,
                        offset=next_offset,
                        length=size,
                        object_key=object_key,
                        object_store_id=object_store_id,
                        log_id=log_id,
                        max_attempts=max_attempts,
                        backoff_factor=backoff_factor,
                        connect_timeout=connect_timeout,
                        read_timeout=read_timeout,
                    )
                    in_flight.append((next_offset, new_fut))
                    next_offset += size

    def download(
        self,
        object_key: str,
        file_path: Optional[str] = None,
        object_store_id: Optional[str] = None,
        log_id: Optional[str] = None,
        continue_download: bool = False,
        skip_if_exists: bool = False,
        overwrite: bool = False,
        part_size: int = 100 * 1024 * 1024,
        max_workers: Optional[int] = 10,
        start_offset: int = 0,
        end_offset: Optional[int] = None,
        max_attempts: int = 3,
        backoff_factor: float = 5.0,
        connect_timeout: int = 60,
        read_timeout: int = 600,
    ) -> int:
        """
        Download an object's data directly to a file.

        :param object_key: The key of the object.
        :type object_key: str
        :param file_path: The path to the file to download to. Defaults to None.
        :type file_path: str, optional
        :param object_store_id: The object store id to use. Defaults to None.
        :type object_store_id: str, optional
        :param log_id: The log id to use. Defaults to None.
        :type log_id: str, optional
        :param continue_download: Whether to continue an existing download. Defaults to False.
        :type continue_download: bool, optional
        :param skip_if_exists: Whether to skip the download if the file already exists. Defaults to False.
        :type skip_if_exists: bool, optional
        :param overwrite: Whether to overwrite the file if it already exists. Defaults to False.
        :type overwrite: bool, optional
        :param part_size: The size of each part to download. Defaults to 100 * 1024 * 1024.
        :type part_size: int, optional
        :param max_workers: The maximum number of workers to use for parallel downloads. Defaults to 10.
        :type max_workers: int, optional
        :param start_offset: The offset to start downloading from. Defaults to 0.
        :type start_offset: int, optional
        :param end_offset: The offset to stop downloading at. Defaults to None.
        :type end_offset: int, optional
        :param max_attempts: The maximum number of attempts to make. Defaults to 3.
        :type max_attempts: int, optional
        :param backoff_factor: The backoff factor to use. Defaults to 5.0.
        :type backoff_factor: float, optional
        :param connect_timeout: The connect timeout to use. Defaults to 60.
        :type connect_timeout: int, optional
        :param read_timeout: The read timeout to use. Defaults to 600.
        :type read_timeout: int, optional
        :raises FileExistsError: If the file already exists and skip_if_exists is False.
        :raises Exception: If the file already exists and continue_download is False.
        :returns: The number of bytes downloaded.
        :rtype: int
        """
        if file_path is None:
            file_path = object_key.split("/")[-1]

        if os.path.exists(file_path):
            if skip_if_exists:
                self.app.logger.debug(
                    f"Skipping download of {object_key} to {file_path} because it already exists"
                )
                return
            elif overwrite:
                self.app.logger.debug(f"Overwriting file {file_path}")
                os.remove(file_path)
            elif not continue_download:
                raise FileExistsError(f"File {file_path} already exists")
            else:
                start_offset = os.path.getsize(file_path)
                self.app.logger.debug(
                    f"Continuing download of {object_key} to {file_path} from offset {start_offset}"
                )

        if end_offset is None:
            object_meta = self.get_object_meta(
                object_key=object_key,
                object_store_id=object_store_id,
                log_id=log_id,
            )
            end_offset = object_meta.size

        file_mode = "ab" if continue_download else "wb"
        with open(file_path, file_mode) as file:
            for data, part_offset in self.iter_object_data_parts(
                object_key=object_key,
                object_store_id=object_store_id,
                log_id=log_id,
                part_size=part_size,
                max_workers=max_workers,
                start_offset=start_offset,
                end_offset=end_offset,
                max_attempts=max_attempts,
                backoff_factor=backoff_factor,
                connect_timeout=connect_timeout,
                read_timeout=read_timeout,
                return_as_completed=file_mode == "wb",
            ):
                file.seek(part_offset)
                file.write(data)
                # Explicitly drop reference to allow GC of large bytearrays sooner.
                del data
        return os.path.getsize(file_path)

    # Record Data

    def get_record_image(
        self,
        record_data: dict | bytes,
        max_size: Optional[int] = None,
        format: str = "WEBP",
        format_params: dict = {},
        renormalize: bool = True,
        reset_position: bool = True,
        return_bytes: bool = False,
        **kwargs,
    ) -> Union[ImagePIL.Image, io.BytesIO, None]:
        """
        A convenience method which takes deserialized record data from a standard image topic and returns the image as a PIL Image or BytesIO object.

        :param record_data: The record data.
        :type record_data: dict | bytes
        :param max_size: The maximum width or height to downscale to. Defaults to None, which means no downscaling.
        :type max_size: int, optional
        :param format: The output format to use. Defaults to "WEBP".
        :type format: str, optional
        :param format_params: The format parameters to use. Defaults to {}.
        :type format_params: dict, optional
        :param renormalize: Whether to renormalize the image, which is necessary for visualization in some cases. Defaults to True.
        :type renormalize: bool, optional
        :param reset_position: Whether to reset the position offset position of the BytesIO object. Defaults to True.
        :type reset_position: bool, optional
        :param return_bytes: Whether to return the image as a BytesIO object. Defaults to False.
        :type return_bytes: bool, optional
        :returns: The image, either as a PIL Image or BytesIO object, or None if the record data does not contain an image.
        :rtype: Union[ImagePIL.Image, io.BytesIO, None]
        """
        return get_record_image(
            record_data=record_data,
            max_size=max_size,
            format=format,
            format_params=format_params,
            renormalize=renormalize,
            reset_position=reset_position,
            return_bytes=return_bytes,
            **kwargs,
        )

    def iter_topic_records(
        self,
        topic: Union[Topic, UUID, str],
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        per_request_limit: int = 1000,
        frequency: Optional[float] = None,
        include_auxiliary_data: bool = False,
    ):
        """
        Iterate over records for a topic.

        :param topic: The topic to use.
        :type topic: Topic | UUID | str
        :param start_time: The start time to use. Defaults to None.
        :type start_time: int, optional
        :param end_time: The end time to use. Defaults to None.
        :type end_time: int, optional
        :param per_request_limit: The limit to use for each request. Defaults to 1000.
        :type per_request_limit: int, optional
        :param frequency: The frequency to use for each request. Defaults to None.
        :type frequency: float, optional
        :param include_auxiliary_data: Whether to include auxiliary data. Defaults to False.
        :type include_auxiliary_data: bool, optional
        :yields: The record.
        :rtype: Record
        """
        if isinstance(topic, Topic):
            topic_id = topic.id
        else:
            topic_id = topic
        with ThreadPoolExecutor() as executor:
            records = self.app.list.record(
                topic_id=topic_id,
                timestamp_gte=start_time,
                timestamp_lte=end_time,
                limit=per_request_limit,
                frequency=frequency,
                include_auxiliary_data=include_auxiliary_data,
            ).data
            if len(records) == 0:
                return
            last_record = records[-1]
            last_record_timestamp = last_record.timestamp
            records_future = executor.submit(
                self.app.list.record,
                topic_id=topic_id,
                timestamp_gt=last_record_timestamp,
                timestamp_lte=end_time,
                limit=per_request_limit,
                frequency=frequency,
                include_auxiliary_data=include_auxiliary_data,
            )
            while len(records) > 0:
                yield from records
                records_res = records_future.result()
                records = records_res.data
                if len(records) == 0:
                    break
                last_record = records[-1]
                last_record_timestamp = last_record.timestamp
                records_future = executor.submit(
                    self.app.list.record,
                    topic_id=topic_id,
                    timestamp_gt=last_record_timestamp,
                    timestamp_lte=end_time,
                    limit=per_request_limit,
                    frequency=frequency,
                    include_auxiliary_data=include_auxiliary_data,
                )

    def iter_topics_records(
        self,
        topics: List[Union[Topic, UUID, str]],
        start_time: Optional[int] = None,
        end_time: Optional[int] = None,
        per_request_limit: int = 1000,
        frequency: Optional[float] = None,
        include_auxiliary_data: bool = False,
    ):
        """
        Iterate over records for multiple topics.

        :param topics: The topics to use.
        :type topics: List[Topic | UUID | str]
        :param start_time: The start time to use. Defaults to None.
        :type start_time: int, optional
        :param end_time: The end time to use. Defaults to None.
        :type end_time: int, optional
        :param per_request_limit: The limit to use for each request. Defaults to 1000.
        :type per_request_limit: int, optional
        :param frequency: The frequency to use for each request. Defaults to None.
        :type frequency: float, optional
        :param include_auxiliary_data: Whether to include auxiliary data. Defaults to False.
        :type include_auxiliary_data: bool, optional
        :yields: The record.
        :rtype: Record
        """
        topic_ids = []
        for topic in topics:
            if isinstance(topic, Topic):
                topic_ids.append(topic.id)
            else:
                topic_ids.append(topic)
        record_iters = {
            topic_id: self.iter_topic_records(
                topic=topic_id,
                start_time=start_time,
                end_time=end_time,
                per_request_limit=per_request_limit,
                frequency=frequency,
                include_auxiliary_data=include_auxiliary_data,
            )
            for topic_id in topic_ids
        }
        next_records = {topic_id: None for topic_id in topic_ids}
        while True:
            for topic_id, record_iter in record_iters.items():
                if next_records[topic_id] is None:
                    next_records[topic_id] = next(record_iter, None)
            next_topic_id = None
            next_record = None
            for topic_id, record in next_records.items():
                if record is not None:
                    if next_record is None or record.timestamp < next_record.timestamp:
                        next_topic_id = topic_id
                        next_record = record
            if next_record is None:
                break
            yield next_record
            next_records[next_topic_id] = next(record_iters[next_topic_id], None)

    def load_auxiliary_data_image(self, source: Union[Record, dict]):
        if isinstance(source, Record):
            auxiliary_data = source.get_auxiliary_data()
        else:
            auxiliary_data = source

        if auxiliary_data is None:
            return None
        if "image" not in auxiliary_data:
            return None
        encoded_webp_data = auxiliary_data["image"]
        decoded_webp_data = base64.b64decode(encoded_webp_data)
        image = ImagePIL.open(io.BytesIO(decoded_webp_data))
        return image

    def get_deserialized_record_data(
        self,
        record: Record,
        topic: Optional[Topic] = None,
        ingestion: Optional[Ingestion] = None,
        transcoder: Optional[Transcode] = None,
    ) -> dict:
        if transcoder is None:
            transcoder = Transcode()

        if topic is None:
            topic = self.app.fetch.topic(record.topic_id).data

        message_bytes = self.fetch_record_bytes(record=record, ingestion=ingestion)

        return transcoder.deserialize(
            type_encoding=topic.type_encoding,
            type_name=topic.type_name,
            type_data=topic.type_data,
            message_bytes=message_bytes,
        )

    def fetch_record_bytes(
        self,
        record: Record,
        ingestion: Optional[Ingestion] = None,
        decompress_chunk: bool = True,
        return_full_chunk: bool = False,
    ) -> bytes:

        if ingestion is None:
            ingestion = self.app.fetch.ingestion(record.ingestion_id).data

        object_store_id = (
            str(ingestion.object_store_id)
            if ingestion.object_store_id is not None
            else None
        )
        object_key = str(ingestion.object_key)

        if record.source is not None:
            # if the record has a source, we need to get the relative path from the object_key
            object_key = get_relative_object_path(
                object_key=object_key, source=record.source
            )

        if object_store_id is None:
            # the data is coming from a log object
            message_bytes: bytes = self.app.fetch.log_object(
                object_key=object_key,
                log_id=record.log_id,
                redirect=True,
                offset=record.data_offset,
                length=record.data_length,
            )
        else:
            # the data is coming from an object store
            message_bytes: bytes = self.app.fetch.object(
                object_key=object_key,
                object_store_id=object_store_id,
                redirect=True,
                offset=record.data_offset,
                length=record.data_length,
            )

        if record.chunk_compression is not None and record.chunk_compression not in [
            "",
            "none",
        ]:
            if decompress_chunk:
                # if the record is compressed, we need to decompress it
                message_bytes = decompress_chunk_bytes(
                    chunk_bytes=message_bytes,
                    chunk_compression=record.chunk_compression,
                    chunk_length=record.chunk_length,
                )
                if not return_full_chunk:
                    # we only return the relevant part of the chunk
                    message_bytes = message_bytes[
                        record.chunk_offset : record.chunk_offset + record.chunk_length
                    ]
            else:
                if not return_full_chunk:
                    raise Exception(
                        "Cannot return partial chunk without decompressing it."
                    )

        return message_bytes

    def get_record_set(
        self,
        records: Iterable[Record],
        carryover_record: Optional[Record] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,  # 100 MB
        max_contiguous_records: int = 1000,
    ) -> tuple[list[list[Record]], Optional[Record]]:
        record_set: list[Record] = []
        relevant_length = 0
        full_length = 0
        start_offset = None
        last_ingestion_id = None
        last_source = None
        last_offset = None

        if carryover_record is not None:
            record_set.append(carryover_record)
            start_offset = carryover_record.data_offset
            last_ingestion_id = carryover_record.ingestion_id
            last_source = carryover_record.source
            last_offset = carryover_record.data_offset + carryover_record.data_length
            carryover_record = None
        leftover_record: Optional[Record] = None

        for record in records:
            if start_offset is None:
                start_offset = record.data_offset
            if last_ingestion_id is None:
                last_ingestion_id = record.ingestion_id
            if last_source is None:
                last_source = record.source
            if last_offset is None:
                last_offset = record.data_offset + record.data_length

            if (record.data_offset + record.data_length) < last_offset:
                # ensure records are ordered properly by offset
                leftover_record = record
                break

            relevant_length += record.data_length
            full_length = record.data_offset + record.data_length - start_offset
            if (
                relevant_length / full_length > density_threshold
                and last_ingestion_id == record.ingestion_id
                and last_source == record.source
                and len(record_set) < max_contiguous_records
                and full_length < max_contiguous_size
                and record.data_offset + record.data_length >= last_offset
            ):
                record_set.append(record)
                last_offset = record.data_offset + record.data_length
            else:
                if len(record_set) == 0:
                    raise Exception("Record set cannot be empty.")
                leftover_record = record
                break
        return record_set, leftover_record

    def get_presigned_url(
        self,
        object_key: str,
        object_store_id: Union[UUID, str, None] = None,
        log_id: Union[UUID, str, None] = None,
        start_offset: Optional[int] = None,
        end_offset: Optional[int] = None,
    ) -> str:
        params = dict(object_key=object_key, redirect=False)
        if object_store_id is None:
            # the data is coming from a log object
            params["log_id"] = log_id
            if start_offset is not None:
                params["offset"] = start_offset
                if end_offset is not None:
                    params["length"] = end_offset - start_offset
            object_meta: Object = self.app.fetch.log_object(**params).data
        else:
            # the data is coming from an object store
            params["object_store_id"] = object_store_id
            if start_offset is not None:
                params["offset"] = start_offset
                if end_offset is not None:
                    params["length"] = end_offset - start_offset
            object_meta: Object = self.app.fetch.object(**params).data
        presigned_url = object_meta.presigned_url
        return presigned_url

    def iter_dense_record_data(
        self,
        records: Iterable[Record],
        deserialize_results: bool = True,
        transcoder: Optional[Transcode] = None,
        stream_data: bool = True,
        ingestions: dict[str, Ingestion] = {},
        topics: dict[str, Topic] = {},
        presigned_urls: dict[str, str] = {},
    ) -> Iterator[tuple[Record, Union[bytes, dict]]]:
        if transcoder is None:
            transcoder = Transcode()

        object_key: Optional[str] = None
        source: Optional[str] = None

        start_offset = None
        end_offset = None
        for record in records:
            ingestion_id = str(record.ingestion_id)
            if ingestion_id not in ingestions:
                ingestions[ingestion_id] = self.app.fetch.ingestion(ingestion_id).data
            ingestion = ingestions[ingestion_id]

            if object_key is None:
                object_key = str(ingestion.object_key)
                if record.source is not None:
                    source = record.source
                    object_key = get_relative_object_path(
                        object_key=object_key, source=record.source
                    )

            if record.ingestion_id != ingestion.id:
                raise Exception(
                    f"All records must have the same ingestion. Found {record.ingestion_id} and {ingestion.id}."
                )

            if record.source != source:
                raise Exception(
                    f"All records must have the same source. Found {record.source} and {source}."
                )

            if start_offset is None:
                start_offset = record.data_offset

            if end_offset is None:
                end_offset = record.data_offset + record.data_length

            current_end_offset = record.data_offset + record.data_length
            if current_end_offset < end_offset:
                raise Exception(
                    f"Records must be ordered by data offset. Found current end offset {current_end_offset} less than last end offset {end_offset}."
                )
            else:
                end_offset = current_end_offset

        presigned_url = presigned_urls.get(object_key, None)
        if presigned_url is None:
            # TODO: we assume object_key is unique, but it may exist across object stores
            presigned_url = self.get_presigned_url(
                object_key=object_key,
                object_store_id=ingestion.object_store_id,
                log_id=ingestion.log_id,
                # TODO: we can't request the presigned URL with a range, so we need to fetch the whole object
                # we should update this to fetch specific ranges and request new presigned URLs as needed
                # start_offset=start_offset,
                # end_offset=end_offset,
            )
            presigned_urls[object_key] = presigned_url

        def get_data_stream(presigned_url):
            headers = {
                "Range": f"bytes={start_offset}-{end_offset - 1}",
            }
            if stream_data:
                buffer_length = 1_000_000 * 32  # 32 MB
                r = requests.get(presigned_url, headers=headers, stream=True)
                r.raise_for_status()
                data_stream = io.BufferedReader(r.raw, buffer_length)
            else:
                r = requests.get(presigned_url, headers=headers, stream=False)
                r.raise_for_status()
                data_stream = io.BytesIO(r.content)
            return data_stream

        try:
            data_stream = get_data_stream(presigned_url)
        except Exception as e:
            self.app.logger.debug(f"Error getting data stream: {e}")
            self.app.logger.debug("Generating new presigned URL and trying again.")
            presigned_url = self.get_presigned_url(
                object_key=object_key,
                object_store_id=ingestion.object_store_id,
                log_id=ingestion.log_id,
                # TODO: we can't request the presigned URL with a range, so we need to fetch the whole object
                # we should update this to fetch specific ranges and request new presigned URLs as needed
                # start_offset=start_offset,
                # end_offset=end_offset,
            )
            presigned_urls[object_key] = presigned_url
            data_stream = get_data_stream(presigned_url)

        # Now we can iterate over the records and read the data from the stream
        decompressed_bytes: Optional[bytes] = None
        compressed_chunk_offset: Optional[int] = None
        current_offset = start_offset
        for record in records:
            data_offset = record.data_offset
            data_length = record.data_length

            if (
                compressed_chunk_offset is not None
                and record.chunk_compression is not None
                and record.data_offset == compressed_chunk_offset
            ):
                message_bytes = decompressed_bytes[
                    record.chunk_offset : record.chunk_offset + record.chunk_length
                ]
            else:
                data_stream.read(data_offset - current_offset)
                message_bytes = data_stream.read(data_length)
                current_offset = data_offset + data_length

                if (
                    record.chunk_compression is not None
                    and record.chunk_compression not in ["", "none"]
                ):
                    decompressed_bytes = decompress_chunk_bytes(
                        chunk_bytes=message_bytes,
                        chunk_compression=record.chunk_compression,
                        chunk_length=record.chunk_length,
                    )
                    message_bytes = decompressed_bytes[
                        record.chunk_offset : record.chunk_offset + record.chunk_length
                    ]
                    compressed_chunk_offset = record.data_offset

            if deserialize_results:
                # if we want to deserialize the results, we need the topic
                topic_id = str(record.topic_id)
                if topic_id not in topics:
                    # if we haven't seen this record's topic yet, we fetch it here
                    topics[topic_id] = self.app.fetch.topic(record.topic_id).data
                topic = topics[topic_id]
                record_data = transcoder.deserialize(
                    type_encoding=topic.type_encoding,
                    type_name=topic.type_name,
                    type_data=topic.type_data,
                    message_bytes=message_bytes,
                )
                yield (record, record_data)
            else:
                yield (record, message_bytes)

    def iter_record_data(
        self,
        records: Iterable[Record],
        deserialize_results: bool = False,
        transcoder: Optional[Transcode] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,
        max_contiguous_records: int = 1000,
        max_workers: Optional[int] = 2,
        order_by_timestamp: bool = True,
        stop_event: Optional[Event] = None,
    ) -> Iterator[tuple[Record, Union[bytes, dict]]]:
        """
        Given a set of records, yield the record and its data.

        :param records: The records to use.
        :type records: Iterable[Record]
        :param deserialize_results: Whether to deserialize the results. Defaults to False.
        :type deserialize_results: bool, optional
        :param transcoder: The transcoder to use. Defaults to None.
        :type transcoder: Transcode, optional
        :param density_threshold: The density threshold to use. Defaults to 0.9.
        :type density_threshold: float, optional
        :param max_contiguous_size: The maximum contiguous size to use. Defaults to 100 * 1000 * 1000.
        :type max_contiguous_size: int, optional
        :param max_contiguous_records: The maximum contiguous records to use. Defaults to 1000.
        :type max_contiguous_records: int, optional
        :param max_workers: The maximum number of workers to use. Defaults to 2.
        :type max_workers: int | None, optional
        :param order_by_timestamp: Whether to order the records by timestamp. Defaults to True.
        :type order_by_timestamp: bool, optional
        :param stop_event: An event to signal stopping the iteration. Defaults to None.
        :type stop_event: Event, optional
        :yields: The record and the record data.
        :rtype: tuple[Record, dict | bytes]
        """
        if stop_event is None:
            stop_event = Event()

        generating_record_sets = True
        kill_threads = False
        record_sets: list[list[Record]] = []

        accumulated_records = {}
        original_record_ordering = []

        if transcoder is None:
            transcoder = Transcode()
        ingestions: dict[str, Ingestion] = {}
        topics: dict[str, Topic] = {}
        presigned_urls: dict[str, str] = {}

        if isinstance(records, list):
            records = iter(records)

        # We generate record sets in a thread so that we can start processing records as soon as possible.
        # A record set is a set of records which conform to our density requirements and can be processed together.
        # i.e., they're batches of records that should be fetched from object storage in one chunk.
        def generate_record_sets():
            nonlocal generating_record_sets
            nonlocal kill_threads
            try:
                record_set_count = 0
                record_set_sizes = {}
                leftover_record = None
                self.app.logger.debug("Generating record sets...")
                while not stop_event.is_set():
                    if kill_threads:
                        break
                    record_set, leftover_record = self.get_record_set(
                        records=records,
                        carryover_record=leftover_record,
                        density_threshold=density_threshold,
                        max_contiguous_size=max_contiguous_size,
                        max_contiguous_records=max_contiguous_records,
                    )
                    for record in record_set:
                        if record.timestamp not in accumulated_records:
                            accumulated_records[record.timestamp] = {}
                        accumulated_records[record.timestamp][record.topic_id] = None
                        original_record_ordering.append(record)
                    record_sets.append(record_set)
                    record_set_count += 1
                    record_set_sizes[record_set_count] = len(record_set)
                    if leftover_record is None:
                        break
                generating_record_sets = False
                self.app.logger.debug(
                    f"Done generating {record_set_count} record sets."
                )
            except Exception as e:
                self.app.logger.error(
                    {
                        "log_type": "generate_record_sets_error",
                        "exception": str(e),
                    }
                )
                kill_threads = True
                raise e

            # the following is for debugging only
            try:
                _record_set_sizes = list(record_set_sizes.values())
                record_set_sizes_1 = len(
                    [size for size in _record_set_sizes if size == 1]
                )
                record_set_sizes_lt_10 = len(
                    [size for size in _record_set_sizes if size < 10 and size > 1]
                )
                record_set_sizes_gt_10 = len(
                    [size for size in _record_set_sizes if size > 10]
                )
                self.app.logger.debug(
                    f"Record set sizes: 1={record_set_sizes_1}, >1,<10={record_set_sizes_lt_10}, >10={record_set_sizes_gt_10}"
                )
            except Exception as e:
                self.app.logger.debug(f"Error calculating record set sizes: {e}")

        # We process record sets in a thread so that we can parallelize the fetching of record data.
        def process_record_set(record_set):
            nonlocal kill_threads
            if kill_threads or stop_event.is_set():
                return
            max_attempts = 3
            for attempt_idx in range(1, max_attempts + 1):
                try:
                    record_data_iter = self.iter_dense_record_data(
                        records=record_set,
                        deserialize_results=deserialize_results,
                        transcoder=transcoder,
                        ingestions=ingestions,
                        topics=topics,
                        presigned_urls=presigned_urls,
                    )
                    for record, record_data in record_data_iter:
                        if stop_event.is_set():
                            return
                        try:
                            accumulated_records[record.timestamp][record.topic_id] = (
                                record,
                                record_data,
                            )
                        except KeyError:
                            pass
                    break
                except Exception as e:
                    self.app.logger.debug(
                        f"Error on attempt {attempt_idx} in process_record_set: {e}"
                    )
                    if attempt_idx == max_attempts:
                        self.app.logger.error(
                            {
                                "log_type": "process_record_set_error",
                                "exception": str(e),
                            }
                        )
                        kill_threads = True
                        raise e

        # We process accumulated records in a thread so that we can yield record data as it becomes available.
        # This function just runs process_record_set as record sets become available (i.e., nested threads).
        def process_accumulated_records():
            nonlocal kill_threads
            try:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    futures = []
                    while generating_record_sets or len(record_sets):
                        if kill_threads or stop_event.is_set():
                            break
                        if len(record_sets) == 0:
                            time.sleep(0.1)
                            continue
                        record_set = record_sets.pop(0)
                        if len(record_set):
                            future = executor.submit(process_record_set, record_set)
                            futures.append(future)
                    for future in as_completed(futures):
                        if stop_event.is_set():
                            break
                        future.result()
            except Exception as e:
                self.app.logger.error(
                    {
                        "log_type": "process_accumulated_records_error",
                        "exception": str(e),
                    }
                )
                kill_threads = True
                raise e

        # This is the main runner which starts the two main threads and yields record data as it becomes available.
        with ThreadPoolExecutor() as executor:
            generate_record_sets_future = executor.submit(generate_record_sets)
            process_accumulated_records_future = executor.submit(
                process_accumulated_records
            )
            current_record = None
            printed = False
            while generating_record_sets or len(accumulated_records) > 0:
                try:
                    if kill_threads or stop_event.is_set():
                        break
                    if len(accumulated_records) == 0:
                        time.sleep(0.1)
                        continue

                    if order_by_timestamp:
                        timestamp = min(accumulated_records)
                        while len(accumulated_records[timestamp]) > 0:
                            if kill_threads or stop_event.is_set():
                                break
                            topic_id = min(accumulated_records[timestamp])
                            result = accumulated_records[timestamp][topic_id]
                            if result is None:
                                time.sleep(0.1)
                                continue
                            del accumulated_records[timestamp][topic_id]
                            record, record_data = result
                            yield record, record_data
                        del accumulated_records[timestamp]
                    else:
                        if current_record is None:
                            if len(original_record_ordering) == 0:
                                if generating_record_sets:
                                    time.sleep(0.1)
                                    continue
                                else:
                                    break
                            current_record = original_record_ordering.pop(0)
                        timestamp = current_record.timestamp
                        topic_id = current_record.topic_id
                        if timestamp not in accumulated_records:
                            time.sleep(0.1)
                            continue
                        if topic_id not in accumulated_records[timestamp]:
                            time.sleep(0.1)
                            if not printed:
                                print(f"Waiting for {topic_id} at {timestamp}")
                                print(
                                    f"Topic IDs: {list(accumulated_records[timestamp].keys())}"
                                )
                                printed = True
                            continue
                        result = accumulated_records[timestamp][topic_id]
                        if result is None:
                            time.sleep(0.1)
                            continue
                        del accumulated_records[timestamp][topic_id]
                        record, record_data = result
                        current_record = None
                        printed = False
                        yield record, record_data
                except KeyboardInterrupt as e:
                    kill_threads = True
                    raise e
            generate_record_sets_future.result()
            process_accumulated_records_future.result()

    def digestion_part_index_entry_to_record(
        self,
        entry: tuple,
        log_id: Union[UUID, str] = "00000000-0000-0000-0000-000000000000",
        created_at: datetime.datetime = datetime.datetime.now(),
    ) -> Record:
        (
            topic_id,
            ingestion_id,
            source,
            data_offset,
            data_length,
            chunk_compression,
            chunk_offset,
            chunk_length,
            timestamp,
        ) = entry
        record = Record(
            log_id=log_id,
            topic_id=topic_id,
            timestamp=timestamp,
            ingestion_id=ingestion_id,
            data_offset=data_offset,
            data_length=data_length,
            chunk_compression=chunk_compression,
            chunk_offset=chunk_offset,
            chunk_length=chunk_length,
            source=source,
            error=None,
            query_data=None,
            auxiliary_data=None,
            raw_data=None,
            context=None,
            note=None,
            locked=False,
            locked_by=None,
            locked_at=None,
            lock_token=None,
            created_at=created_at,
            updated_at=None,
            deleted_at=None,
            created_by=None,
            updated_by=None,
            deleted_by=None,
        )
        return record

    def iter_digestion_part_records(
        self,
        digestion_part: Union[DigestionPart, UUID, str],
        digestion: Union[Digestion, UUID, str, None] = None,
        digestion_part_wait_duration: int = 60 * 30,
        stream_buffer_length: int = 1_000_000 * 32,
        raise_if_ready: bool = True,
        raise_if_queued: bool = False,
    ) -> Iterator[tuple[DigestionPartIndexEntry, bytes]]:
        if isinstance(digestion_part, DigestionPart):
            if digestion_part.index is None:
                # we have to fetch the digestion part to get the index
                digestion_part = self.app.fetch.digestion_part(
                    digestion_id="00000000-0000-0000-0000-000000000000",
                    digestion_part_id=digestion_part.id,
                ).data
        else:
            digestion_part = self.app.fetch.digestion_part(
                digestion_id="00000000-0000-0000-0000-000000000000",
                digestion_part_id=digestion_part,
            ).data

        if digestion is None:
            digestion = self.app.fetch.digestion(digestion_part.digestion_id).data
        else:
            if digestion.id != digestion_part.digestion_id:
                raise Exception(
                    f"Digestion ID {digestion_part.digestion_id} from digestion part does not match provided digestion ID {digestion.id}"
                )

        current_digestion_wait_time = time.time()
        while digestion_part.state != ProcessState.completed:
            if digestion_part.state == ProcessState.failed:
                raise Exception(
                    f"Digestion part {digestion_part.id} is in a failed state."
                )
            if digestion_part.state == ProcessState.queued:
                if raise_if_queued:
                    raise Exception(
                        f"Digestion part {digestion_part.id} is in a queued state."
                    )
            if digestion_part.state == ProcessState.ready:
                if raise_if_ready:
                    raise Exception(
                        f"Digestion part {digestion_part.id} is in a ready state."
                    )
            if time.time() - current_digestion_wait_time > digestion_part_wait_duration:
                raise Exception(
                    f"Digestion part {digestion_part.id} is not in completed state after waiting {digestion_part_wait_duration} seconds."
                )
            time.sleep(10)
            digestion_part = self.app.fetch.digestion_part(
                digestion_id=digestion.id, digestion_part_id=digestion_part.id
            ).data

        record_blob_key = (
            f"digestions/{digestion.id}/digestion_parts/{digestion_part.id}.bin"
        )
        record_blob_object = self.app.fetch.log_object(
            log_id=digestion.log_id,
            object_key=record_blob_key,
            redirect=False,
        ).data
        r = requests.get(record_blob_object.presigned_url, stream=True)
        r.raise_for_status()
        record_blob_data_stream = io.BufferedReader(r.raw, stream_buffer_length)
        for entry_tuple in digestion_part.index:
            (
                topic_id,
                ingestion_id,
                source,
                data_offset,
                data_length,
                chunk_compression,
                chunk_offset,
                chunk_length,
                timestamp,
            ) = entry_tuple
            record_length = data_length if chunk_length is None else chunk_length
            record_bytes = record_blob_data_stream.read(record_length)
            entry = DigestionPartIndexEntry(
                topic_id=topic_id,
                ingestion_id=ingestion_id,
                source=source,
                data_offset=data_offset,
                data_length=data_length,
                chunk_compression=chunk_compression,
                chunk_offset=chunk_offset,
                chunk_length=chunk_length,
                timestamp=timestamp,
            )
            yield entry, record_bytes

    def iter_digestion_records(
        self,
        digestion: Union[Digestion, UUID, str],
        digestion_part_wait_duration: int = 60 * 30,
        stream_buffer_length: int = 1_000_000 * 32,
        max_workers: Optional[int] = 10,
    ) -> Iterator[tuple[UUID, DigestionPartIndexEntry, bytes]]:
        """
        Iterate over records for a digestion.

        A digestion is a collection of digestion parts, which each contain an index of records. This method returns an iterator which yields a tuple with the following:

        - The digestion part ID.
        - The entry from the digestion part index.
        - The record bytes.

        This is useful for iterating over all records in a digestion, which can be more efficient than iterating over records through the API.
        The `max_workers` parameter determines the number of workers to use for fetching the record data in parallel. Set to `None` to use no threading.

        :param digestion: The digestion or digestion ID to use.
        :type digestion: Digestion | UUID | str
        :param digestion_part_wait_duration: The digestion part wait duration to use. Defaults to 60 * 30.
        :type digestion_part_wait_duration: int, optional
        :param stream_buffer_length: The stream buffer length to use. Defaults to 1_000_000 * 32.
        :type stream_buffer_length: int, optional
        :param max_workers: The maximum number of workers to use. Defaults to 10.
        :type max_workers: int, optional

        :yields: The digestion part ID, the entry, and the record bytes.
        """
        if isinstance(digestion, Digestion):
            digestion_id = digestion.id
        else:
            digestion_id = digestion
            digestion = self.app.fetch.digestion(digestion_id).data

        max_digestion_parts = (
            10_000  # TODO: configurable, raise error if too many parts
        )
        limit = 1000
        offset = 0
        digestion_parts_res = self.app.list.digestion_parts(
            digestion_id=digestion_id, limit=limit, offset=offset
        )
        digestion_parts = digestion_parts_res.data
        total_digestion_parts = digestion_parts_res.count
        if total_digestion_parts > max_digestion_parts:
            raise Exception(
                f"Too many digestion parts ({total_digestion_parts}) for extraction (must be less than {max_digestion_parts})"
            )

        while len(digestion_parts) < total_digestion_parts:
            offset += limit
            digestion_parts_res = self.app.list.digestion_parts(
                digestion_id=digestion_id, limit=limit, offset=offset
            )
            digestion_parts.extend(digestion_parts_res.data)
        digestion_parts_count = len(digestion_parts)
        if digestion_parts_count != total_digestion_parts:
            raise Exception(
                f"Expected {digestion_parts_count} digestion parts, but got {total_digestion_parts}"
            )

        if max_workers is None:
            for part_idx, digestion_part in enumerate(digestion_parts):
                self.app.logger.debug(
                    f"Processing digestion part {part_idx + 1} of {digestion_parts_count}"
                )
                for entry, record_bytes in self.iter_digestion_part_records(
                    digestion_part=digestion_part,
                    digestion=digestion,
                    digestion_part_wait_duration=digestion_part_wait_duration,
                    stream_buffer_length=stream_buffer_length,
                ):
                    yield digestion_part.id, entry, record_bytes
        else:

            def get_digestion_part_record_iter(digestion_part):
                items = []
                for entry, record_bytes in self.iter_digestion_part_records(
                    digestion_part=digestion_part,
                    digestion=digestion,
                    digestion_part_wait_duration=digestion_part_wait_duration,
                    stream_buffer_length=stream_buffer_length,
                ):
                    items.append((digestion_part.id, entry, record_bytes))
                return items

            with ThreadPoolExecutor(max_workers=max_workers) as executor:
                futures = []
                for part_idx, digestion_part in enumerate(digestion_parts):
                    future = executor.submit(
                        get_digestion_part_record_iter, digestion_part
                    )
                    futures.append(future)
                for future_idx in range(len(futures)):
                    future = futures[future_idx]
                    for item in future.result():
                        yield item
                    futures[future_idx] = None

    def iter_digestion_data(
        self,
        digestion: Union[Digestion, UUID, str],
        deserialize_results: bool = False,
        transcoder: Optional[Transcode] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,
        max_contiguous_records: int = 1000,
        max_workers: Optional[int] = 2,
    ):
        if isinstance(digestion, Digestion):
            digestion_id = digestion.id
        else:
            digestion_id = digestion
            digestion = self.app.fetch.digestion(digestion_id).data

        log_id = digestion.log_id
        digestion_parts_res = self.app.list.digestion_parts(
            digestion_id=digestion_id, limit=1000
        )
        digestion_parts = digestion_parts_res.data
        digestion_parts_count = len(digestion_parts)
        if digestion_parts_count != digestion_parts_res.count:
            raise Exception(
                f"Expected {digestion_parts_count} digestion parts, but got {digestion_parts_res.count}"
            )

        def iter_digestion_records():
            with ThreadPoolExecutor(max_workers=2) as executor:
                futures = []
                for digestion_part in digestion_parts:
                    future = executor.submit(
                        self.app.fetch.digestion_part,
                        digestion_part_id=digestion_part.id,
                        digestion_id=digestion_id,
                    )
                    futures.append(future)
                for future in futures:
                    digestion_part = future.result().data
                    part_index = digestion_part.index
                    for entry in part_index:
                        record = self.digestion_part_index_entry_to_record(
                            entry=entry, log_id=log_id
                        )
                        yield record

        yield from self.iter_record_data(
            records=iter_digestion_records(),
            deserialize_results=deserialize_results,
            transcoder=transcoder,
            density_threshold=density_threshold,
            max_contiguous_size=max_contiguous_size,
            max_contiguous_records=max_contiguous_records,
            max_workers=max_workers,
        )

    def ingestion_part_index_entry_to_record(
        self,
        entry: tuple,
        ingestion_id: Union[UUID, str],
        source: Optional[str] = None,
        log_id: Union[UUID, str] = "00000000-0000-0000-0000-000000000000",
        created_at: datetime.datetime = datetime.datetime.now(),
    ) -> Record:
        context = None
        if len(entry) == 7:
            (
                topic_id,
                data_offset,
                data_length,
                chunk_compression,
                chunk_offset,
                chunk_length,
                timestamp,
            ) = entry
        elif len(entry) == 8:
            (
                topic_id,
                data_offset,
                data_length,
                chunk_compression,
                chunk_offset,
                chunk_length,
                timestamp,
                context,
            ) = entry
        else:
            raise ValueError(f"Invalid index entry length: {len(entry)}")
        record = Record(
            log_id=log_id,
            topic_id=topic_id,
            timestamp=timestamp,
            ingestion_id=ingestion_id,
            data_offset=data_offset,
            data_length=data_length,
            chunk_compression=chunk_compression,
            chunk_offset=chunk_offset,
            chunk_length=chunk_length,
            source=source,
            error=None,
            query_data=None,
            auxiliary_data=None,
            raw_data=None,
            context=context,
            note=None,
            locked=False,
            locked_by=None,
            locked_at=None,
            lock_token=None,
            created_at=created_at,
            updated_at=None,
            deleted_at=None,
            created_by=None,
            updated_by=None,
            deleted_by=None,
        )
        return record

    def iter_ingestion_part_data(
        self,
        ingestion_part: Union[IngestionPart, UUID, str],
        ingestion: Optional[Ingestion] = None,
        deserialize_results: bool = False,
        transcoder: Optional[Transcode] = None,
        density_threshold: float = 0.9,
        max_contiguous_size: int = 100 * 1000 * 1000,
        max_contiguous_records: int = 1000,
        max_workers: Optional[int] = 2,
    ):
        if isinstance(ingestion_part, IngestionPart):
            ingestion_part_id = ingestion_part.id
            if ingestion_part.index is None:
                ingestion_part = self.app.fetch.ingestion_part(
                    ingestion_part_id=ingestion_part_id,
                    ingestion_id="00000000-0000-0000-0000-000000000000",
                ).data
        else:
            ingestion_part_id = ingestion_part
            ingestion_part = self.app.fetch.ingestion_part(
                ingestion_part_id=ingestion_part_id,
                ingestion_id="00000000-0000-0000-0000-000000000000",
            ).data

        if ingestion is None:
            ingestion = self.app.fetch.ingestion(ingestion_part.ingestion_id).data

        def iter_ingestion_part_records():
            part_index = ingestion_part.index
            for entry in part_index:
                record = self.ingestion_part_index_entry_to_record(
                    entry=entry,
                    ingestion_id=ingestion_part.ingestion_id,
                    source=ingestion_part.source,
                    log_id=ingestion.log_id,
                )
                yield record

        yield from self.iter_record_data(
            records=iter_ingestion_part_records(),
            deserialize_results=deserialize_results,
            transcoder=transcoder,
            density_threshold=density_threshold,
            max_contiguous_size=max_contiguous_size,
            max_contiguous_records=max_contiguous_records,
            max_workers=max_workers,
        )
