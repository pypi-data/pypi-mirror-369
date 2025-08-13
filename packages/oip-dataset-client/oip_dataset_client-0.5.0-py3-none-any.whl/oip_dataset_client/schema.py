from typing import Dict, List, Optional, TypedDict, Any
from enum import Enum

# entity instance
EntityInstance = Dict[str, Any]

# list of entities instances
EntityListInstances = List[EntityInstance]


# class ApiRequestArgs(TypedDict, total=False):
#     filter_cols: Optional[str]
#     filter_ops: Optional[str]
#     filter_vals: Optional[str]
#     page_num: Optional[str]
#     page_size: Optional[str]
#     sort_col: Optional[str]
#     sort_order: Optional[str]
#     logical_op: Optional[str]

ApiRequestArgs = Dict[str, str]


class FileEntryDict(TypedDict, total=False):
    relative_path: str
    parent_dataset_id: str
    artifact_name: Optional[str]
    local_path: Optional[str]
    size: Optional[int]
    hash: Optional[str]
    remote_url_basename: Optional[str]


FileEntries = Dict[str, FileEntryDict]


class DatasetDict(TypedDict, total=False):
    name: str
    id: str
    workspace_id: str
    version: str
    is_main: bool
    parent_datasets: List[str]
    _tags: List[str]
    status: str
    file_entries: List[FileEntryDict]
    file_count: int
    added_files: int
    modified_files: int
    removed_files: int
    total_size: int
    total_size_compressed: int
    local_download_folder: str
    description: Optional[str]
    dependency_graph: Dict[str, List[str]]
    dependency_chunk_lookup: Dict[str, int]


class DatasetState(TypedDict, total=False):
    id: str
    file_entries: List[FileEntryDict]
    file_count: int
    added_files: int
    modified_files: int
    removed_files: int
    total_size: int
    total_size_compressed: int
    dependency_graph: Dict[str, List[str]]
    dependency_chunk_lookup: Optional[Dict[str, int]]


class DatasetStatus(Enum):
    CREATED: str = "created"
    IN_PROGRESS: str = "in_progress"
    UPLOADED: str = "uploaded"
    FAILED: str = "failed"
    COMPLETED: str = "completed"
    ABORTED: str = "aborted"
    UNKNOWN: str = "unknown"
