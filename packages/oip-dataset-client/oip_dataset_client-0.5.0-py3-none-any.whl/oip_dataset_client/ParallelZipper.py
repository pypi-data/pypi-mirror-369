import os
from concurrent.futures import ThreadPoolExecutor
from typing import Any, Optional, List, Dict, Set, Deque
from zipfile import ZipFile, ZIP_DEFLATED
from six.moves.queue import PriorityQueue, Queue, Empty
from pathlib import Path
from tempfile import mkstemp
from collections import deque
from tqdm import tqdm


class ParallelZipper(object):
    """
    Used to zip multiple files in zip chunks of a particular size, all in parallel
    """

    class ZipperObject(object):
        def __init__(
            self,
            chunk_size: int,  # int
            zipper_queue: PriorityQueue,
            zipper_results: Queue,
            allow_zip_64: bool,
            compression: Any,
            zip_prefix: str,
            zip_suffix: str,
        ):
            # (...) -> ParallelZipper.ZipperObject
            """
            Initialize a ParallelZipper.ZipperObject instance that holds its corresponding zip
            file, as well as other relevant data

            :param chunk_size: Chunk size, in MB. The ParallelZipper will try its best not to exceed this size
                when bulding up this zipper object, but that is not guaranteed
            :param zipper_queue: PriorityQueue that holds ParallelZipper.ZipperObject instances.
                When this ParallelZipper.ZipperObject can hold more data (i.e. chunk_size was not exceeded),
                this object will reinsert itself in this queue to be reused by the ParallelZipper.
                Else, a fresh ParallelZipper.ZipperObject will be inserted
            :param zipper_results: Queue that holds ParallelZipper.ZipperObject instances. These instances
                are added to this queue when chunk_size is exceeded
            :param allow_zip_64: if True, ZipFile will create files with ZIP64 extensions when
                needed, otherwise it will raise an exception when this would be necessary
            :param compression: ZipFile.ZIP_STORED (no compression), ZipFile.ZIP_DEFLATED (requires zlib),
                ZipFile.ZIP_BZIP2 (requires bz2) or ZipFile.ZIP_LZMA (requires lzma).
            :param zip_prefix: The zip file created by this object will have its name prefixed by this
            :param zip_suffix: The zip file created by this object will have its name suffixed by this
            :return: ParallelZipper.ZipperObject instance
            """
            self._chunk_size: int = chunk_size
            self._zipper_queue = zipper_queue
            self._zipper_results = zipper_results
            self._allow_zip_64: bool = allow_zip_64
            self._compression: Any = compression
            self._zip_prefix: str = zip_prefix
            self._zip_suffix: str = zip_suffix
            self.fd, zip_path = mkstemp(prefix=zip_prefix, suffix=zip_suffix)
            self.zip_path = Path(zip_path)
            self.zip_file = ZipFile(
                self.zip_path.as_posix(),
                "w",
                allowZip64=allow_zip_64,
                compression=compression,
            )
            self.archive_preview: List[Dict[str, str]] = []
            self.count: int = 0
            self.files_zipped: Set = set()

        def zip(self, file_path: str, zip_name: str) -> None:
            """
            Zips a file into the ZipFile created by this instance. This instance will either add
            itself back to the PriorityQueue used to select the best zipping candidate or add itself
            to the result Queue after exceeding self.chunk_size.

            :param file_path: str: Path to the file to be zipped
            :param zip_name: str: Name of the file in the archive
            """
            self.zip_file.write(file_path, zip_name)
            self.count += 1
            self.files_zipped.add(Path(file_path).as_posix())
            if self._chunk_size <= 0 or self.size < self._chunk_size:
                self._zipper_queue.put(self)
            else:
                self._zipper_queue.put(
                    ParallelZipper.ZipperObject(
                        self._chunk_size,
                        self._zipper_queue,
                        self._zipper_results,
                        self._allow_zip_64,
                        self._compression,
                        self._zip_prefix,
                        self._zip_suffix,
                    )
                )
                self._zipper_results.put(self)

        def merge(self, other) -> None:
            """
            Merges one ParallelZipper.ZipperObject instance into the current one.
            All the files zipped by the other instance will be added to this instance,
            as well as any other useful additional data

            :param other: ParallelZipper.ZipperObject: ParallelZipper.ZipperObject instance to merge into this one
            """
            with ZipFile(self.zip_path.as_posix(), "a") as parent_zip:
                with ZipFile(other.zip_path.as_posix(), "r") as child_zip:
                    for child_name in child_zip.namelist():
                        parent_zip.writestr(
                            child_name, child_zip.open(child_name).read()
                        )
            self.files_zipped |= other.files_zipped
            self.count += other.count

        def close(self) -> None:
            """
            Attempts to close file descriptors associated to the ZipFile
            """
            try:
                self.zip_file.close()
                os.close(self.fd)
            except (Exception,):
                pass

        def delete(self) -> None:
            """
            Attempts to delete the ZipFile from the disk
            """
            try:
                self.close()
                self.zip_path.unlink()
            except (Exception,):
                pass

        @property
        def size(self) -> int:
            """
            :return: Size of the ZipFile, in bytes
            """
            return self.zip_path.stat().st_size

        def __lt__(self, other):
            # we want to completely "fill" as many zip files as possible, hence the ">" comparison
            return self.size > other.size

    def __init__(
        self,
        chunk_size: int,
        max_workers: int,
        allow_zip_64: Optional[bool] = True,
        compression: Optional[Any] = ZIP_DEFLATED,
        zip_prefix: Optional[str] = "",
        zip_suffix: Optional[str] = "",
        pool: Optional[ThreadPoolExecutor] = None,
    ) -> None:
        """
        Initialize the ParallelZipper. Each zip created by this object will have the following naming
        format: [zip_prefix]<random_string>[zip_suffix]

        :param chunk_size: Chunk size, in MB. The ParallelZipper will try its best not to exceed this size,
            but that is not guaranteed
        :param max_workers: The maximum number of workers spawned when zipping the files
        :param allow_zip_64: if True, ZipFile will create files with ZIP64 extensions when
            needed, otherwise it will raise an exception when this would be necessary
        :param compression: ZipFile.ZIP_STORED (no compression), ZipFile.ZIP_DEFLATED (requires zlib),
            ZipFile.ZIP_BZIP2 (requires bz2) or ZipFile.ZIP_LZMA (requires lzma).
        :param zip_prefix: Zip file names will be prefixed by this
        :param zip_suffix: Zip file names will pe suffixed by this
        :param pool: Use this ThreadPoolExecutor instead of creating one. Note that this pool will not be
            closed after zipping is finished.

        :return: ParallelZipper instance
        """
        # chunk_size in Megabyte
        self._chunk_size: int = chunk_size * (1024**2)
        self._max_workers: int = max_workers
        self._allow_zip_64: bool = allow_zip_64
        self._compression: Any = compression
        self._zip_prefix: str = zip_prefix
        self._zip_suffix: str = zip_suffix
        self._pool: ThreadPoolExecutor = pool
        self._zipper_queue: PriorityQueue = PriorityQueue()
        self._zipper_results: Queue = Queue()

    def zip_iter(
        self,
        file_paths: List[str],
        zip_names: Dict[str, str],
        total_chunks: int,
        verbose: Optional[bool] = True,
    ):
        """
        Generator function that returns zip files as soon as they are available.
        The zipping is done in parallel

        :param file_paths: List[str]: List of paths to the files to zip
        :param zip_names: dict: example {abs_local_path_to_file_1:relative_path_to_file_1,abs_local_path_to_file_2:..}
        :param total_chunks: int: Expected number of chunks to zip
            (total_chunks value is an approximate estimation it may be lower)
        :return: Generator of ParallelZipper.ZipperObjects
        """
        while not self._zipper_queue.empty():
            self._zipper_queue.get_nowait()
        for _ in range(self._max_workers):
            self._zipper_queue.put(
                ParallelZipper.ZipperObject(
                    self._chunk_size,
                    self._zipper_queue,
                    self._zipper_results,
                    self._allow_zip_64,
                    self._compression,
                    self._zip_prefix,
                    self._zip_suffix,
                )
            )
        for file_path in file_paths[:]:
            if not Path(file_path).is_file():
                file_paths.remove(file_path)

        file_paths = sorted(
            file_paths, key=lambda k: Path(k).stat().st_size, reverse=True
        )
        # zip in parallel
        pooled: List = []
        if verbose:
            zip_pbar: tqdm = tqdm(total=total_chunks,
                                  desc="zipping", unit=" chunk")
        if not self._pool:
            pool: ThreadPoolExecutor = ThreadPoolExecutor(
                max_workers=self._max_workers)
        else:
            pool = self._pool
        for f in file_paths:
            zipper = self._zipper_queue.get()
            pooled.append(pool.submit(zipper.zip, Path(
                f).as_posix(), zip_names.get(f)))
            # yield zipped files
            for result in self._yield_zipper_results():
                yield result
                if verbose:
                    zip_pbar.update(1)
        # await task completion
        for task in pooled:
            task.result()
        #  if no active tasks in the pool
        if not self._pool:
            pool.shutdown()

        for result in self._yield_zipper_results():
            yield result
        # files that have been compressed but are still in the queue
        zipper_results_leftover: Deque = deque()

        # extract remaining results
        while not self._zipper_queue.empty():
            result = self._zipper_queue.get()
            if result.count != 0:
                zipper_results_leftover.append(result)
            else:
                result.delete()
        # double-ended queue.
        # It is a data structure that allows you to efficiently add and remove elements from both ends
        zipper_results_leftover = deque(
            sorted(zipper_results_leftover, reverse=True))

        # merge zip files greedily if possible and get the paths as results
        while len(zipper_results_leftover) > 0:
            zip_ = zipper_results_leftover.pop()
            zip_.close()
            if zip_.size >= self._chunk_size > 0:
                yield zip_
                if verbose:
                    zip_pbar.update(1)
                continue
            while len(zipper_results_leftover) > 0 and (
                self._chunk_size <= 0
                or zipper_results_leftover[0].size + zip_.size < self._chunk_size
            ):
                child_zip = zipper_results_leftover.popleft()
                child_zip.close()
                zip_.merge(child_zip)
                child_zip.delete()
            yield zip_
            if verbose:
                zip_pbar.update(1)
        if verbose:
            zip_pbar.total = zip_pbar.n

    def _yield_zipper_results(self):
        while True:
            try:
                result = self._zipper_results.get_nowait()
                result.close()
                yield result
            except Empty:
                break
