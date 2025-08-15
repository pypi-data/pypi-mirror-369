from __future__ import annotations
from dataclasses import dataclass
import functools
from collections.abc import Iterable
from concurrent.futures import ThreadPoolExecutor
import glob
import json
import pathlib
from pathlib import PurePosixPath, PurePath
import re
import io
import os
import shutil
from typing import Callable, Any
import inspect
import itertools

from fsspec.spec import AbstractFileSystem
import datetime
import numpy as np
import pandas as pd
import pandas.io.formats.format as fmt
from pandas.api.types import is_dict_like
import pyarrow
import pyarrow.parquet as pq
import pyarrow.dataset as ds


try:
    import gcsfs
except ImportError:
    pass

try:
    from google.cloud import storage
except ImportError:
    pass

# regex with the prefix '_v' followed by an integer of any length
VERSION_PATTERN = r"_v(\d+)\."
VERSION_PREFIX = "_v"

# regex with the prefix '_p' followed by four length integer (year) and OPTIONALLY month and date, separated by '-'
# This will also match with more than 4 digits in a row, so we must catch that with an error message beforehand
PERIOD_PATTERN = r"_p(\d{4}(?:-Q[1-4]|-\d{2}(?:-\d{2})?)?)"
PERIOD_PREFIX = "_p"

INDEX_NAMES = ["timestamp", "mb", "type"]


@dataclass
class Config:
    __slots__ = ("file_system",)
    file_system: Callable


class LocalFileSystem(AbstractFileSystem):
    """Mimicks GCS's FileSystem but using standard library (os, glob, shutil)."""

    @staticmethod
    def glob(
        path: str,
        detail: bool = False,
        recursive: bool = True,
        include_hidden: bool = True,
        **kwargs,
    ) -> list[dict] | list[str]:
        relevant_paths = glob.iglob(
            path, recursive=recursive, include_hidden=include_hidden, **kwargs
        )

        if not detail:
            return list(relevant_paths)
        with ThreadPoolExecutor() as executor:
            return list(executor.map(get_file_info, relevant_paths))

    @classmethod
    def ls(cls, path: str, detail: bool = False, **kwargs):
        return cls().glob(
            str(pathlib.Path(path) / "**"), detail=detail, recursive=False, **kwargs
        )

    @staticmethod
    def info(path) -> dict[str, Any]:
        return get_file_info(path)

    @staticmethod
    def open(path: str, *args, **kwargs) -> io.TextIOWrapper:
        return open(path, *args, **kwargs)

    @staticmethod
    def exists(path: str) -> bool:
        return os.path.exists(path)

    @staticmethod
    def mv(source: str, destination, **kwargs) -> str:
        return shutil.move(source, destination, **kwargs)

    @classmethod
    def cp(cls, source: str, destination, **kwargs) -> str:
        return cls.cp_file(source, destination, **kwargs)

    @staticmethod
    def cp_file(source, destination, **kwargs):
        os.makedirs(pathlib.Path(destination).parent, exist_ok=True)
        return shutil.copy2(source, destination, **kwargs)

    @staticmethod
    def rm_file(path: str, *args, **kwargs) -> None:
        return os.remove(path, *args, **kwargs)

    @staticmethod
    def rmdir(path: str, *args, **kwargs) -> None:
        return shutil.rmtree(path, *args, **kwargs)

    @staticmethod
    def makedirs(path: str, exist_ok: bool = False) -> None:
        return os.makedirs(path, exist_ok=exist_ok)


class MyGCSFileSystem(gcsfs.GCSFileSystem):
    def isdir(self, path: str) -> bool:
        """Check if path is a directory."""
        info = super(gcsfs.GCSFileSystem, self).info(path)
        return info["type"] == "directory"

    def rmdir(self, path: str) -> None:
        """Remove contents of a directory in GCS. It might take some time before files are actually deleted."""
        path = pathlib.Path(path)
        remaining = self.glob(str(path / "**"))
        assert all(self.isdir(x) for x in remaining), [
            x for x in remaining if not self.isdir(x)
        ]
        storage_client = storage.Client()
        bucket = storage_client.get_bucket(path.parts[0])
        blobs = bucket.list_blobs(prefix="/".join(path.parts) + "/")
        for blob in blobs:
            blob.delete()


if any("dapla" in key.lower() for key in os.environ) and "gcsfs" in locals():
    _config = Config(MyGCSFileSystem)
else:
    _config = Config(LocalFileSystem)


class Tree:
    """Stores text to be printed/displayed in directory tree format.

    If displayed in Jupyter/interactive, paths will be hyperlinked and copyable.
    """

    def __init__(self):
        self.repr = ()
        self.repr_html = ()

    def _add(self, text: str):
        self.repr += (text,)

    def _add_html(self, text: str):
        self.repr_html += (text,)

    def __repr__(self):
        return "\n".join(self.repr)

    def __str__(self):
        return "\n".join(self.repr)

    def _repr_html_(self):
        return "\n".join(self.repr_html)


class _PathBase:
    _version_pattern: str = VERSION_PATTERN
    _version_prefix: str = VERSION_PREFIX
    _period_pattern: str = PERIOD_PATTERN
    _period_prefix: str = PERIOD_PREFIX

    @staticmethod
    def set_option(pat: str, value: Any) -> None:
        """Change config variable."""
        setattr(_config, pat, value)

    @property
    def _file_system_constructor(self) -> Callable | type:
        """Can be overridden in subclass.

        Must return a function or a class that, when called,
        implements the methods 'glob', 'info' and 'isdir',

        The 'info' method should return a dict like with at least the keys
        'updated', 'size', 'name' and 'type'.
        """
        return _config.file_system


class Path(str, _PathBase):
    """Path object that works like a string, with methods for working with the GCS file system."""

    _file_system_attrs: set[str] = {
        "info",
        "isdir",
        "open",
        "exists",
        "mv",
        "cp",
        "rm_file",
        "rmdir",
    }

    @property
    def _iterable_type(self) -> type | Callable:
        """Can be overridden in subclass."""
        return PathSeries

    @staticmethod
    def _standardize_path(path: str | PurePosixPath) -> str:
        """Make sure delimiter is '/' and path ends without '/'."""
        return str(path).replace("\\", "/").replace(r"\"", "/")

    def __new__(cls, gcs_path: str | PurePath | None = None, file_system=None):
        """Construct Path with '/' as delimiter."""
        gcs_path = cls._standardize_path(gcs_path or "")
        obj = super().__new__(cls, gcs_path)
        obj._path = PurePosixPath(obj)
        obj._file_system = file_system
        return obj

    def buckets_path(self) -> "Path":
        if self.startswith("/buckets"):
            return self

        root = self.parts[0]
        bucket = root.split("-data-")[-1].split("-prod")[0]

        try:
            return self._new(f"/buckets/{bucket}/{'/'.join(self.parts[1:])}")
        except IndexError:
            return self._new(f"/buckets/{bucket}")

    def tree(
        self,
        max_rows: int | None = 3,
        ascending: bool = True,
        indent: int = 4,
        include_hidden: bool = False,
    ) -> Tree:
        """Get directory tree.

        Args:
            max_rows: Maximum number of files to show per directory.
            ascending: Whether to sort in ascending or descending order.
            indent: Number of whitespaces to indent each level by.
                Defaults to 4.
        """
        return get_path_tree(
            self.glob("**", include_hidden=include_hidden, recursive=True),
            self,
            max_rows=max_rows,
            ascending=ascending,
            indent=indent,
        )

    def rglob(self, pattern: str, **kwargs) -> "PathSeries":
        return self.glob(pattern, recursive=True, **kwargs)

    def glob(
        self, pattern: str | None = None, recursive: bool = True, **kwargs
    ) -> "PathSeries":
        """Create PathSeries of files/directories that match the pattern."""

        recursive = kwargs.get("recurse_symlinks", recursive)

        if pattern:
            pattern = str(self / pattern)
        else:
            pattern = str(self)

        # pop kwargs going into PathSeries initialiser.
        iterable_init_args = get_arguments(self._iterable_type)
        iterable_init_kwargs = {
            key: kwargs.pop(key) for key in list(kwargs) if key in iterable_init_args
        }

        kwargs["detail"] = True

        if "recursive" in get_arguments(self.file_system.glob):
            kwargs["recursive"] = recursive
        else:
            # try to set to non-recursive if file_system.glob allows argument 'maxdepth'
            kwargs["maxdepth"] = None if recursive else 1

        try:
            info: list[dict] | dict = self.file_system.glob(pattern, **kwargs)
        except TypeError:
            kwargs.pop("maxdepth", None)
            info: list[dict] | dict = self.file_system.glob(pattern, **kwargs)

        if isinstance(info, dict):
            # file system can return single dict if only one file path
            info = [info]

        if any(isinstance(y, dict) for x in info for y in x.values()):
            # unpack nested dicts
            info: list[dict] = [
                {key.lower(): val for key, val in inner_filedict.items()}
                for filedict in info
                for inner_filedict in filedict.values()
            ]

        return self._iterable_constructor(info, **iterable_init_kwargs)

    def ls(self, recursive: bool = False, **kwargs) -> "PathSeries":
        """Lists the contents of a GCS bucket path.

        Returns a PathSeries with paths as values and timestamps
        and file size as index.
        """
        return self.glob("**", recursive=recursive, **kwargs)

    def rmdir(self) -> None:
        files = self.glob("**").files
        with ThreadPoolExecutor() as executor:
            list(executor.map(self.file_system.rm_file, files))

    def cp(self, destination: "Path | str") -> "Path":
        return self._cp_or_mv(destination, "cp")

    def mv(self, destination: "Path | str") -> "Path":
        was_dir = self.isdir()
        out_path = self._cp_or_mv(destination, "mv")
        if was_dir:
            try:
                self.file_system.rmdir(str(self))
            except (FileNotFoundError, NotADirectoryError):
                pass
        return out_path

    def read_text(self, *args, **kwargs):
        return self._path.read_text(*args, **kwargs)

    def versions(self, include_versionless: bool = False) -> "PathSeries":
        """Returns a PathSeries of all versions of the file."""
        files_in_folder: Iterable[Path] = self.parent.glob("**", recursive=False)

        if self.version_number:
            start, _, end = re.split(self._version_pattern, self)
        else:
            start, end = self.stem, self.suffix

        # create boolean mask. With numpy to make it work with both pandas and list
        arr = np.array(files_in_folder)
        is_version_of_this_file = (np_str_contains(arr, start)) & (
            np_str_endswith(arr, end)
        )
        if not include_versionless:
            is_version_of_this_file &= np_str_matches(arr, self._version_pattern)

        try:
            # this works for pandas and numpy, but not list etc.
            return files_in_folder[is_version_of_this_file]
        except TypeError:
            return self._iterable_type(
                [
                    x
                    for x, bool_ in zip(
                        files_in_folder, is_version_of_this_file, strict=True
                    )
                    if bool_
                ]
            )

    def latest_version(self) -> "Path":
        """Get the highest number version of the file path.

        Lists files in the parent directory with the same versionless stem
        and selects the one with the highest version number.

        Returns
        -------
        A Path.
        """
        try:
            versions: list[Path] = sorted(self.versions(include_versionless=False))
            return versions[-1]
        except IndexError as e:
            raise FileNotFoundError(self) from e

    def new_version(self, timeout: int | None = 30) -> "Path":
        """Return the Path with the highest existing version number + 1.

        The method will raise an Exception if the latest version is saved
        before the timeout period is out, to avoid saving new
        versions unpurposely.

        Parameters
        ----------
        timeout:
            Minutes needed between the timestamp of the current highest
            numbered version.

        Returns
        ------
        A Path with a new version number.

        Raises
        ------
        ValueError:
            If the method is run before the timeout period is up.
        """
        try:
            highest_numbered: Path = self.latest_version()
        except FileNotFoundError:
            return self.with_version(1)

        if timeout:
            timestamp: datetime.datetime = highest_numbered.timestamp

            time_should_be_at_least = pd.Timestamp.now(tz="Europe/Oslo").replace(
                tzinfo=None
            ).round("s") - pd.Timedelta(minutes=timeout)
            if timestamp > time_should_be_at_least:
                raise ValueError(
                    f"Latest version of the file was updated {timestamp[0]}, which "
                    f"is less than the timeout period of {timeout} minutes. "
                    "Change the timeout argument, but be sure to not save new "
                    "versions in a loop."
                )

        new_version_number: int = highest_numbered.version_number + 1
        return highest_numbered.with_version(new_version_number)

    def with_version(self, version: int | None) -> "Path":
        """Replace the Path's version number, if any, with a new version number.

        Examples
        --------
        >>> Path('file.parquet').with_version(1)
        'file_v1.parquet'

        >>> Path('file_v101.parquet').with_version(201)
        'file_v201.parquet'
        """
        version_text = f"{self._version_prefix}{version}" if version is not None else ""
        return self._new(
            f"{self.parent}/{self.versionless_stem}{version_text}{self.suffix}"
        )

    def get_versions_and_periods(
        self, include_versionless: bool = False
    ) -> "PathSeries":
        """Returns a PathSeries of all periods of the file."""
        files_in_folder: Iterable[Path] = self.parent.glob("**", recursive=False)

        # create boolean mask. With numpy to make it work with both pandas and list
        arr = np.array(files_in_folder)
        is_version_of_this_file = (
            np_str_contains(arr, self.periodless_stem)
        ) & np_str_endswith(arr, self.suffix)
        if not include_versionless:
            is_version_of_this_file &= np_str_matches(arr, self._version_pattern)

        try:
            # this works for pandas and numpy, but not list etc.
            return files_in_folder[is_version_of_this_file]
        except TypeError:
            return self._iterable_type(
                [
                    x
                    for x, bool_ in zip(
                        files_in_folder, is_version_of_this_file, strict=True
                    )
                    if bool_
                ]
            )

    def latest_period(self) -> "Path":
        """Get the path with greatest period and highest version number.

        Lists files in the parent directory with the same
        versionless and periodless stem and selects the path that sorts last.

        Raises
        ------
        ValueError: If there is mismatch in period patterns, e.g. if one
            path has the period "2020-01-01" and one path has "2021".

        Returns
        -------
        A Path.
        """
        try:
            period_paths: Iterable[Path] = self.get_versions_and_periods(
                include_versionless=False
            )
            sorted_paths = sort_by_period(period_paths)
            return next(iter(reversed(sorted_paths)))
        except (IndexError, StopIteration) as e:
            raise FileNotFoundError(self) from e

    def with_period(self, period: str) -> "Path":
        """Replace the Path's period, if any, with a new periods.

        Examples
        --------
        >>> Path('file_v1.parquet').with_period("2024-01-01")
        'file_p2024-01-01_v1.parquet'
        """
        if not isinstance(period, (str, int)):
            raise TypeError(f"'period' should be string or int. Got {type(period)}")
        if not self.period:
            raise ValueError(f"Cannot set period to path without period. {self}")
        if str(period) == self.period:
            return self
        return self.with_periods(period)

    def with_periods(self, from_period: str, to_period: str | None = None) -> "Path":
        """Replace the Path's period, if any, with one or two new periods.

        Examples
        --------
        >>> Path('file_v1.parquet').with_periods("2024-01-01")
        'file_p2024-01-01_v1.parquet'

        >>> Path('file_p2022_p2023_v1.parquet').with_periods("2024-01-01")
        'file_p2024-01-01_v1.parquet'
        """
        if not isinstance(from_period, (str, int)):
            raise TypeError(
                f"'from_period' should be string or int. Got {type(from_period)}"
            )
        if to_period and not isinstance(to_period, (str, int)):
            raise TypeError(
                f"'to_period' should be string or int. Got {type(to_period)}"
            )
        if not self.periods:
            raise ValueError(f"Cannot set period to path without period. {self}")

        periods: tuple[str] = (
            (str(from_period), str(to_period)) if to_period else (str(from_period),)
        )
        period_string: str = "".join([self._period_prefix + str(x) for x in periods])
        version_string = (
            f"{self._version_prefix}{self.version_number}"
            if self.version_number is not None
            else ""
        )
        stem: str = self.periodless_stem

        parent = f"{self.parent}/" if self.parent != "." else ""

        return self._new(
            f"{parent}{stem}{period_string}{version_string}{self.suffix}".replace(
                "".join(self.periods), period_string.strip(self._period_prefix)
            )
        )

    @property
    def version_number(self) -> int | None:
        return get_version_number(self, self._version_pattern)

    @property
    def periods(self) -> list[str]:
        if re.findall(r"_p(\d{5})", self):
            raise ValueError(f"Invalid period format in {self}")

        try:
            return re.findall(self._period_pattern, self)
        except IndexError:
            return []

    @property
    def period(self) -> str | None:
        periods = self.periods
        if len(periods) > 1:
            raise ValueError(
                "Cannot access the 'period' attribute for paths with multiple periods. "
                "Use the 'periods' attribute instead."
            )
        elif len(periods):
            return next(iter(periods))
        else:
            return None

    @property
    def periodless_stem(self) -> str:
        """Return the file stem before the period pattern."""
        return str(re.sub(f"{self._period_pattern}.*", "", self._path.stem))

    @property
    def versionless_stem(self) -> str:
        """Return the file stem before the version pattern."""
        return self._new(re.split(self._version_pattern, self._path.name)[0]).stem

    @property
    def parent(self) -> "Path":
        """Parent path."""
        return self._new(self._path.parent)

    @property
    def parents(self) -> "list[Path]":
        """Parent path."""
        return [self._new(parent) for parent in self._path.parents]

    @property
    def name(self) -> str:
        """Final part of the path."""
        return self._path.name

    @property
    def stem(self) -> str:
        """File name without the suffix"""
        return self._path.stem

    @property
    def parts(self) -> tuple[str]:
        return self._path.parts

    @property
    def suffix(self) -> str:
        """Final file path suffix."""
        return self._path.suffix

    @property
    def suffixes(self) -> list[str]:
        """File path suffixes, if multiple."""
        return self._path.suffixes

    @property
    def index_column_names(self) -> list[str]:
        return _get_index_cols(self.schema, self)

    @property
    def columns(self) -> pd.Index:
        """Columns of the file."""
        schema = self.schema
        try:
            names = [
                x["field_name"]
                for x in json.loads(schema.metadata[b"pandas"].decode())["columns"]
            ]
        except (KeyError, TypeError):
            names = schema.names
        index_cols = _get_index_cols(schema, self)
        return pd.Index(names).difference(index_cols)

    @property
    def schema(self) -> pyarrow.Schema:
        """Date types of the file's columns."""
        try:
            with self.open("rb") as file:
                return get_schema(file)
        except Exception:
            return get_schema(self)

    @property
    def dtypes(self) -> pd.Series:
        """Date types of the file's columns."""
        schema = self.schema
        index_cols = _get_index_cols(schema, self)
        return pd.Series(schema.types, index=schema.names).loc[
            lambda x: ~x.index.isin(index_cols)
        ]

    @property
    def shape(self) -> tuple[int, int]:
        """Number of rows and columns."""
        try:
            with self.open("rb") as file:
                return get_shape(file)
        except Exception:
            return get_shape(self)

    @property
    def nrow(self) -> int:
        return self.shape[0]

    @property
    def ncol(self) -> int:
        return self.shape[1]

    @property
    def timestamp(self) -> pd.Timestamp:
        """Pandas Timestamp of when the file was last updated."""
        try:
            info = self._info
        except AttributeError:
            info = self.file_system.info(self)
            self._info = info
        return _get_timestamps(info["updated"])

    @property
    def type(self) -> str:
        return "directory" if self.is_dir() else "file"

    @property
    def bytes(self) -> int:
        """File size in bytes."""
        try:
            info = self._info
        except AttributeError:
            info = self.file_system.info(self)
            self._info = info
        return info["size"]

    @property
    def kb(self) -> int:
        """File size in kilobytes."""
        return self.bytes / 1000

    @property
    def mb(self) -> float:
        """File size in megabytes."""
        return self.kb / 1000

    @property
    def gb(self) -> float:
        """File size in gigabytes."""
        return self.kb / 1_000_000

    @property
    def tb(self) -> float:
        """File size in terrabytes."""
        return self.kb / 1_000_000_000

    def partition_root(self) -> "Path":
        if not self.suffix or self.count(self.suffix) != 2:
            return self
        return self._new(self.split(self.suffix)[0] + self.suffix)

    def is_partitioned(self) -> bool:
        if not self.suffix or self.count(self.suffix) != 2:
            return False
        return bool(len(self.glob(f"**/*{self.suffix}")))

    def has_all_partitions(
        self, ids: Iterable[str], nrow_min: int, id_col: str, strict: bool = True
    ) -> bool:
        if not self.exists():
            return False
        paths = self.glob(f"**/*{self.suffix}")
        for id_ in ids:
            these_paths = [path for path in paths if f"{id_col}={id_}" in path]
            if len(these_paths) != 1:
                return False
            this_path = next(iter(these_paths))
            if Path(this_path).nrow < nrow_min:
                return False
        if not strict:
            return True
        for path in paths:
            if not any(f"{id_col}={id_}" for id_ in ids):
                # partition is not in list of ids
                return False
        return True

    def isfile(self) -> bool:
        return not self.isdir()

    def is_file(self) -> bool:
        return self.isfile()

    def is_dir(self) -> bool:
        return self.isdir()

    def with_suffix(self, suffix: str):
        return self._new(self._path.with_suffix(suffix))

    def with_name(self, new_name: str):
        return self._new(self._path.with_name(new_name))

    def with_stem(self, new_with_stem: str):
        return self._new(self._path.with_stem(new_with_stem))

    @property
    def file_system(self):
        if self._file_system is None:
            self._file_system = self._file_system_constructor()
        return self._file_system

    @file_system.setter
    def file_system(self, val):
        self._file_system = val
        return self._file_system

    def __truediv__(self, other: str | os.PathLike | PurePath) -> "Path":
        """Append a string or Path to the path with a forward slash.

        Example
        -------
        >>> folder = 'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2023'
        >>> file_path = folder / "ABAS_kommune_flate_p2023_v1.parquet"
        >>> file_path
        'ssb-areal-data-delt-kart-prod/analyse_data/klargjorte-data/2023/ABAS_kommune_flate_p2023_v1.parquet'
        """
        if not isinstance(other, (str, PurePath, os.PathLike)):
            raise TypeError(
                "unsupported operand type(s) for /: "
                f"{self.__class__.__name__} and {other.__class__.__name__}"
            )
        return self._new(f"{self}/{as_str(other)}")

    def __getattribute__(self, name):
        """stackoverflow hack to ensure we return Path when using string methods.

        It works for all but the string magigmethods, importantly __add__.
        """

        # skip magic methods
        if name not in dir(str) or name.startswith("__") and name.endswith("__"):
            return super().__getattribute__(name)

        def method(self, *args, **kwargs):
            value = getattr(super(), name)(*args, **kwargs)

            # not every string method returns a str:
            if isinstance(value, str):
                return type(self)(value)
            elif isinstance(value, list):
                return [type(self)(i) for i in value]
            elif isinstance(value, tuple):
                return tuple(type(self)(i) for i in value)
            else:  # dict, bool, or int
                return value

        return method.__get__(self)

    def __getattr__(self, attr: str) -> Any:
        """Get file_system attribute."""
        error_message = f"{self.__class__.__name__} has no attribute '{attr}'"
        if attr.startswith("_"):
            raise AttributeError(error_message)
        if attr not in self._file_system_attrs:
            raise AttributeError(error_message)
        return functools.partial(getattr(self.file_system, attr), self)

    def __fspath__(self) -> str:
        return str(self)

    def __dir__(self) -> list[str]:
        return list(sorted({x for x in dir(Path)} | self._file_system_attrs))

    def _iterable_constructor(self, info: list[dict], **kwargs) -> "PathSeries":
        series: pd.Series = _get_paths_and_index(info).apply(self.__class__)
        for path in series:
            path._file_system = self._file_system
        return self._iterable_type(series, **kwargs)

    def _new(self, new_path: str | Path) -> "Path":
        return self.__class__(new_path, self.file_system)

    def _cp_or_mv(self, destination: "Path | str", attr: str) -> "Path":
        func: Callable = getattr(self.file_system, attr)
        try:
            func(self, destination)
        except FileNotFoundError:
            destination = self.__class__(destination)
            sources = list(self.glob("**").files)
            destinations = [path.replace(self, destination) for path in sources]
            with ThreadPoolExecutor() as executor:
                list(executor.map(func, sources, destinations))
        self._new(destination)

    def keep_newest_partitions(self) -> "Path":
        def _keep_newest(path):
            while True:
                if path.isfile():
                    pass

        with ThreadPoolExecutor() as executor:
            list(executor.map(_keep_newest, self.ls()))


class PathSeries(pd.Series, _PathBase):
    """A pandas Series for working with GCS (Google Cloud Storage) paths.

    A PathSeries can be constructed from a root Path with the ls or glob methods,
    or from an iterable of strings.

    The Series will have a three leveled index. The 0th level holds the
    timestamp of when the path was updated. The 1st level is the file's size
    in megabytes. The 2nd level is the type, either "file" or "directory".

    The class share some of the properties and methods of the Path class.
    The Path method/attribute is applied to each row of the PathSeries.

    Parameters
    ----------
    data: An iterable of Path objects.

    Properties
    ----------
    version_number: Series
        The version number of the files.
    versionless_stem: PathSeries
        The versionless stems of the files.
    parent: PathSeries
        The parent directories of the files.
    files: PathSeries
        Select only the files in the Series.
    dirs: PathSeries
        Select only the directories in the Series.
    base: Path
        The common path amongst all paths in the Series.
    timestamp: pd.Index
        The timestamp of the files.
    mb: pd.Index
        The file size in megabytes.
    gb: pd.Index
        The file size in gigabytes.
    kb: pd.Index
        The file size in kilobytes.
    stem: Series
        The stem of the file paths.
    names: Series
        The names of the file paths.

    Methods
    -------
    tree():
        con
    keep_latest_versions():
        Keep only the highest-numbered versions of the files.
    within_minutes(minutes):
        Select files with a timestamp within the given number of minutes.
    not_within_minutes(minutes):
        Select files with a timestamp not within the given number of minutes.
    """

    _index_names = INDEX_NAMES
    _metadata = [
        "_version_pattern",
        "_max_rows",
        "_max_colwidth",
        "_defined_name",
        "_max_parts",
        "name",
    ]

    @property
    def _path_type(self) -> type:
        """Can be overridden in subclass."""
        return Path

    def __init__(
        self,
        data: Iterable[str] | None = None,
        index=None,
        max_rows: int | None = None,
        max_colwidth: int = None,
        max_parts: int | None = 2,
        **kwargs,
    ):
        should_construct_index: bool = (
            data is not None
            and len(data)
            and not (
                isinstance(data, pd.Series)
                and len(data.index.names) == len(self._index_names)
                or isinstance(index, pd.MultiIndex)
                and len(index.names) == len(self._index_names)
                # dict with e.g. tuple keys, turned into MultiIndex
                or is_dict_like(data)
                and all(len(key) == len(self._index_names) for key in data.keys())
            )
        )
        if should_construct_index:
            file_system = kwargs.get("file_system", self._file_system_constructor())
            data = _get_paths_and_index([file_system.info(path) for path in data])

        super().__init__(data, index=index, **kwargs)

        if len(self) and not all(isinstance(path, self._path_type) for path in self):
            self.loc[:] = [self._path_type(x) for x in self]

        max_rows = max_rows or pd.get_option("display.max_rows")
        max_colwidth = max_colwidth or pd.get_option("display.max_colwidth")

        self._max_rows = max_rows
        self._max_colwidth = max_colwidth
        self._max_parts = max_parts
        pd.set_option("display.max_colwidth", max_colwidth)

    @property
    def files(self) -> "PathSeries":
        """Select only the files in the Series."""
        return self[self.is_file()]

    def buckets_path(self) -> "PathSeries":
        return self.files.apply(lambda x: x.buckets_path())

    def partition_root(self, keep: str | None = "last") -> "PathSeries":
        return self.files.apply(lambda x: x.partition_root())[
            lambda x: ~x.duplicated(keep=keep)
        ]

    def partitioned_files(self) -> "PathSeries":
        return (
            self.files.loc[lambda x: x.str.count(r"\.parquet") == 2]
            .partition_root()
            .drop_duplicates()
        )

    @property
    def dirs(self) -> "PathSeries":
        """Select only the directories in the Series."""
        return self[self.is_dir()]

    def tree(
        self,
        max_rows: int | None = 3,
        ascending: bool = True,
        indent: int = 4,
    ) -> Tree:
        """Get directory tree."""
        return get_path_tree(
            self,
            self.base,
            max_rows=max_rows,
            ascending=ascending,
            indent=indent,
        )

    def groupby(self, by=None, *args, **kwargs) -> pd.Series:
        if by == "day":
            copied = self.copy()
            copied.index = copied.timestamp.round("d")
            return copied.groupby(level=0, *args, **kwargs)
        return super().groupby(by, *args, **kwargs)

    def within_minutes(self, minutes: int):
        """Select files with a timestamp within the given number of minutes."""
        time_then = pd.Timestamp.now(tz="Europe/Oslo").replace(tzinfo=None).round(
            "s"
        ) - pd.Timedelta(minutes=minutes)
        return self.files[lambda x: x.timestamp > time_then]

    def within_hours(self, hours: int):
        """Select files with a timestamp within the given number of hours."""
        time_then = pd.Timestamp.now(tz="Europe/Oslo").replace(tzinfo=None).round(
            "s"
        ) - pd.Timedelta(hours=hours)
        return self.files[lambda x: x.timestamp > time_then]

    def within_days(self, days: int):
        """Select files with a timestamp within the given number of days."""
        time_then = pd.Timestamp.now(tz="Europe/Oslo").replace(tzinfo=None).round(
            "s"
        ) - pd.Timedelta(days=days)
        return self.files[lambda x: x.timestamp > time_then]

    def not_within_minutes(self, minutes: int):
        """Select files with a timestamp within the given number of minutes."""
        time_then = pd.Timestamp.now(tz="Europe/Oslo").replace(tzinfo=None).round(
            "s"
        ) - pd.Timedelta(minutes=minutes)
        return self.files[lambda x: x.timestamp < time_then]

    def not_within_hours(self, hours: int):
        """Select files with a timestamp within the given number of hours."""
        time_then = pd.Timestamp.now(tz="Europe/Oslo").replace(tzinfo=None).round(
            "s"
        ) - pd.Timedelta(hours=hours)
        return self.files[lambda x: x.timestamp < time_then]

    def not_within_days(self, days: int):
        """Select files with a timestamp within the given number of days."""
        time_then = pd.Timestamp.now(tz="Europe/Oslo").replace(tzinfo=None).round(
            "s"
        ) - pd.Timedelta(days=days)
        return self.files[lambda x: x.timestamp < time_then]

    @property
    def parts(self) -> pd.Series:
        parts = self.apply(lambda x: x.parts)
        indexlist = [self.index.get_level_values(i) for i in range(self.index.nlevels)]
        parts.index = pd.MultiIndex.from_arrays(indexlist + [list(range(len(self)))])
        return parts

    @property
    def names(self) -> pd.Series:
        return self.apply(lambda x: x.name)

    def keep_latest_versions(self) -> "PathSeries":
        """Keeps only highest numbered version of each base path."""
        self = self.sort_values()
        is_latest = ~(self.versionless_stem.duplicated(keep="last")).values
        is_latest &= np_str_matches(self.values, self._version_pattern)
        return self[is_latest]

    def keep_latest_periods(self) -> "PathSeries":
        """Keeps only greatest period of each base path."""
        self = self[self.str.contains(self._period_pattern)]
        self = sort_by_period(self)
        is_latest = ~(self.periodless_stem.duplicated(keep="last"))
        return self[is_latest]

    def is_file(self) -> pd.Series:
        return self.index.get_level_values(2) != "directory"

    def is_dir(self) -> pd.Series:
        return self.index.get_level_values(2) == "directory"

    def dir_sizes(self, part_index: int, unit: str = "gb") -> pd.Series:
        """Get summarized file sizes in each directory."""

        def join_parts_if_enough_parts(path):
            parts = path.parts
            try:
                path = "/".join(parts[i] for i in range(part_index + 1))
            except IndexError:
                return
            if "." in path:
                return None
            return path

        sizes = getattr(self, unit)
        paths = [join_parts_if_enough_parts(path) for path in self]
        return pd.Series(list(sizes), index=paths).groupby(level=0).sum().sort_values()

    @property
    def timestamp(self) -> pd.Index:
        try:
            return self.index.get_level_values(0)
        except IndexError:
            assert not len(self)
            return self.index

    @property
    def type(self) -> pd.Index:
        try:
            return self.index.get_level_values(2)
        except IndexError:
            assert not len(self)
            return self.index

    @property
    def kb(self) -> pd.Index:
        try:
            return pd.Index(self.mb * 1000, name="kb")
        except IndexError:
            assert not len(self)
            return self.index

    @property
    def mb(self) -> pd.Index:
        try:
            return self.index.get_level_values(1)
        except IndexError:
            assert not len(self)
            return self.index

    @property
    def gb(self) -> pd.Index:
        try:
            return pd.Index(self.mb / 1000, name="gb")
        except IndexError:
            assert not len(self)
            return self.index

    @property
    def tb(self) -> pd.Index:
        """File size in terrabytes."""
        try:
            return pd.Index(self.mb / 1_000_000, name="tb")
        except IndexError:
            assert not len(self)
            return self.index

    @property
    def nrow(self) -> pd.Series:
        return pd.Series(
            self.apply(lambda x: x.shape[0]).values, index=self.values, name="nrow"
        )

    @property
    def ncol(self) -> pd.Series:
        return pd.Series(
            self.apply(lambda x: x.shape[1]).values, index=self.values, name="ncol"
        )

    @property
    def base(self) -> "Path":
        """The common path amongst all paths in the Series."""
        if len(self) <= 1:
            return self._path_type("")

        splitted_path: list[str] = self.iloc[0].split("/")

        common_parts = []
        for folder in splitted_path:
            if self.str.contains(folder).all():
                common_parts.append(folder)
            else:
                break

        return self._path_type("/".join(common_parts))

    def __getattr__(self, attr: str) -> Any:
        """Get Path attribute for each row."""

        def get_property(path: Path):
            x = getattr(path, attr)
            if callable(x):
                raise ValueError(
                    f"{self.__class__.__name__} cannot access Path methods, only properties."
                )
            return x

        if attr in dir(self._path_type) and attr != "name" and attr not in dir(str):
            try:
                series = self.apply(get_property)
                series.name = attr
                return series
            except IndexError as e:
                if len(self):
                    raise e
                series = self.copy()
                series.name = attr
                return series
        return super().__getattribute__(attr)

    def __str__(self) -> str:
        repr_params = fmt.get_series_repr_params()
        repr_params["max_rows"] = self._max_rows

        max_len = max(len(x) for x in self) if len(self) else 0

        if self.base and max_len > self._max_colwidth:
            s = pd.Series(self).str.replace(self.base, "...")
        else:
            s = pd.Series(self)

        if len(s):
            try:
                s.index = pd.MultiIndex.from_arrays(
                    [
                        s.index.get_level_values(0),
                        s.index.get_level_values(1).astype(int),
                        s.index.get_level_values(2),
                    ],
                    names=INDEX_NAMES,
                )
            except (IndexError, ValueError):
                pass

        return s.to_string(**repr_params)

    def __repr__(self) -> str:
        return self.__str__()

    def _repr_html_(self) -> str:
        df = pd.DataFrame({"path": self})

        if not len(df):
            return df._repr_html_()

        get_html_path_func = functools.partial(
            split_path_and_make_copyable_html, max_parts=self._max_parts
        )

        try:
            df.index = pd.MultiIndex.from_arrays(
                [
                    self.index.get_level_values(0),
                    self.index.get_level_values(1).astype(int),
                    self.index.get_level_values(2),
                ],
                names=INDEX_NAMES,
            )
        except (IndexError, ValueError):
            pass

        if len(df) <= self._max_rows:
            return df.style.format({"path": get_html_path_func}).to_html()

        # the Styler puts the elipsis row last. I want it in the middle. Doing it manually...
        first_rows = df.head(self._max_rows // 2).style.format(
            {"path": get_html_path_func}
        )
        last_rows = (
            df.tail(self._max_rows // 2)
            .style.format({"path": get_html_path_func})
            .set_table_styles([{"selector": "thead", "props": "display: none;"}])
        )

        elipsis_value = ["..."]
        elipsis_row = df.iloc[[0]]
        elipsis_row.index = pd.MultiIndex.from_arrays(
            [elipsis_value, elipsis_value, elipsis_value], names=elipsis_row.index.names
        )

        elipsis_row.iloc[[0]] = [
            f"[{len(df) - self._max_rows // 2 * 2} more rows]"
        ] * len(elipsis_row.columns)
        elipsis_row = elipsis_row.style

        return first_rows.concat(elipsis_row).concat(last_rows).to_html()

    @property
    def _constructor_expanddim(self) -> Callable | type:
        """Simply returns pandas.DataFrame with column 'path'.

        Can be overridden in subclass.
        """
        return _dataframe_constructor

    def reset_index(self) -> pd.DataFrame:
        return self._constructor_expanddim(self)

    @property
    def _constructor(self) -> functools.partial:
        """Needed to not return pandas.Series.

        Can be overridden in subclass.
        """
        try:
            return self._constructor_func
        except AttributeError:
            self._constructor_func = functools.partial(
                _pathseries_constructor_with_fallback,
                path_series_type=self.__class__,
            )
            return self._constructor_func


def _pathseries_constructor_with_fallback(
    data=None,
    index=None,
    max_rows: int | None = None,
    max_colwidth: int = None,
    max_parts: int | None = 2,
    path_series_type: type | None = None,
    **kwargs,
) -> "PathSeries | pd.Series":
    path_series_type = path_series_type or PathSeries

    kwargs["name"] = kwargs.pop("name", "path")
    series = pd.Series(data, index, **kwargs)

    if not len(series):
        return path_series_type(
            series,
            index=_get_default_multi_index(),
            max_rows=max_rows,
            max_colwidth=max_colwidth,
            max_parts=max_parts,
            **kwargs,
        )
    try:
        nparts = series.apply(Path._standardize_path).str.split("/").str.len()
        if nparts.max() <= 1:
            return series
    except Exception:
        return series

    try:
        return path_series_type(
            series,
            max_rows=max_rows,
            max_colwidth=max_colwidth,
            max_parts=max_parts,
            **kwargs,
        )
    except FileNotFoundError:
        return series


def _dataframe_constructor(data=None, index=None, **kwargs) -> "pd.DataFrame":
    data.name = "path"
    return pd.DataFrame(data, index=index, **kwargs)


def split_path_and_make_copyable_html(
    path: str,
    max_parts: int | None = 2,
    split: str | None = "/",
    display_prefix: str | None = ".../",
) -> str:
    """Get HTML text that displays the last part, but makes the full path copyable to clipboard.

    Splits the path on a delimiter and creates an HTML string that displays only the
    last part, but adds a hyperlink which copies the full path to clipboard when clicked.

    Parameters
    ----------
    path: File or directory path
    max_parts: Maximum number of path parts to display. Defaults to 2,
        meaning the two last parts. Set to None to show full paths.
    split: Text pattern to split the path on. Defaults to "/".
    display_prefix: The text to display instead of the parent directory. Defaults to ".../".

    Returns
    -------
    A string that holds the HTML and JavaScript code to be passed to IPython.display.display.
    """

    copy_to_clipboard_js = f"""<script>
function copyToClipboard(text, event) {{
    event.preventDefault();
    navigator.clipboard.writeText(text)
        .then(() => {{
            const alertBox = document.createElement('div');
            const selection = window.getSelection();

            alertBox.style.position = 'fixed';
            alertBox.style.top = (selection.getRangeAt(0).getBoundingClientRect().top + window.scrollY) + 'px';
            alertBox.style.left = (selection.getRangeAt(0).getBoundingClientRect().left + window.scrollX) + 'px';
            alertBox.style.backgroundColor = '#f2f2f2';
            alertBox.style.border = '1px solid #ccc';
            alertBox.style.padding = '10px';
            alertBox.innerHTML = 'Copied to clipboard';
            document.body.appendChild(alertBox);

            setTimeout(function() {{
                alertBox.style.display = 'none';
            }}, 1500);  // 1.5 seconds
        }})
        .catch(err => {{
            console.error('Could not copy text: ', err);
        }});
}}
</script>"""

    if split is not None:
        if max_parts is None:
            name = path
        else:
            name = "/".join(path.split(split)[-max_parts:])
        displayed_text = f"{display_prefix}{name}" if display_prefix else name
    else:
        displayed_text = path

    return f'{copy_to_clipboard_js}<a href="#" title="{path}" onclick="copyToClipboard(\'{path}\', event)">{displayed_text}</a>'


def _get_default_multi_index() -> pd.MultiIndex:
    return pd.MultiIndex.from_arrays(
        [[] for _ in range(len(INDEX_NAMES))], names=INDEX_NAMES
    )


def _get_paths_and_index(info: list[dict]) -> pd.Series:
    files: pd.Series = _get_file_series(info)
    dirs: pd.Series = _get_directory_series(info)

    if not len(files) and not len(dirs):
        return pd.Series(index=_get_default_multi_index())

    out = pd.Series(pd.concat([lst for lst in [files, dirs] if len(lst)])).sort_index(
        level=0
    )

    return out


def _get_directory_series(info):
    """pandas.Series of all directories in the list returned from dapla.ls(detail=True).

    Index is a MultiIndex of all zeros (because directories have no timestamp and size).
    """
    try:
        dirs = np.array([x["name"] for x in info if x["type"] == "directory"])
    except KeyError as e:
        is_list_of_empty_dict: bool = len(info) == 1 and not next(iter(info))
        if is_list_of_empty_dict:
            return pd.Series(
                index=pd.MultiIndex.from_arrays(
                    [[] for _ in range(len(INDEX_NAMES))], names=INDEX_NAMES
                )
            )
        raise e

    return pd.Series(
        dirs,
        index=pd.MultiIndex.from_arrays(
            [
                pd.DatetimeIndex(np.full(len(dirs), pd.NA)),
                np.zeros(len(dirs)),
                ["directory" for _ in range(len(dirs))],
            ],
            names=INDEX_NAMES,
        ),
    )


def _get_file_series(info: list[dict]) -> pd.Series:
    """pandas.Series of all files in the list returned from dapla.ls(detail=True).

    Index is a MultiIndex if timestamps, file size and types.
    """
    # 2d numpy array
    try:
        fileinfo = np.array(
            [
                (x["updated"], x["size"], x["name"])
                for x in info
                if x["type"] != "directory"
            ]
        )
    except KeyError as e:
        if len(info) == 1 and not next(iter(info)):
            return pd.Series(index=_get_default_multi_index())
        raise KeyError(e, info)

    if not len(fileinfo):
        return pd.Series(index=_get_default_multi_index())

    timestamp: pd.Index = _get_timestamps(pd.Index(fileinfo[:, 0], name="updated"))
    mb = pd.Index(fileinfo[:, 1], name="mb (int)").astype(float) / 1_000_000
    type_ = ["file" for _ in range(len(fileinfo))]

    index = pd.MultiIndex.from_arrays([timestamp, mb, type_], names=INDEX_NAMES)

    return (
        pd.Series(fileinfo[:, 2], index=index, name="path")
        # remove dirs
        [lambda x: ~x.str.endswith("/")].sort_index(level=0)
    )


def get_version_number(path: Path | str, pattern: str = VERSION_PATTERN) -> int | None:
    try:
        last_match = re.findall(pattern, path)[-1]
        return int(last_match)
    except IndexError:
        return None


def get_path_tree(
    paths: PathSeries | list[Path],
    base: str | Path,
    max_rows: int | None = 3,
    ascending: bool = True,
    indent: int = 4,
) -> Tree:

    tree = Tree()

    paths = PathSeries(paths).sort_values(ascending=ascending).files

    paths_grouped_by_dir = [
        paths[paths.str.contains(parent, regex=False)]
        for parent in {path.parent for path in paths}
    ]

    tree._add_html(
        split_path_and_make_copyable_html(base, None, display_prefix="") + " /"
    )
    tree._add(base + " /")

    already_printed: set[tuple[str]] = set()

    for dir_files in paths_grouped_by_dir:
        assert isinstance(dir_files, PathSeries)

        has_version_number = dir_files.version_number.notna()
        if max_rows is not None and sum(has_version_number) >= max_rows:
            dir_files = dir_files[has_version_number]

        # as tuple because it's hashable
        parts_so_far: tuple[str] = tuple(base.split("/"))

        j = 0

        for i, path in enumerate(dir_files):
            *folders, name = path.replace(base, "").strip("/").split("/")
            if i == 0:
                for j, folder in enumerate(folders):
                    parts_so_far += (folder,)

                    if parts_so_far in already_printed:
                        continue
                    spaces = " " * indent * (j + 1)

                    tree._add_html(
                        f"<pre>{spaces}└──{split_path_and_make_copyable_html('/'.join(parts_so_far), max_parts=1, display_prefix='')} /<pre>",
                    )
                    tree._add(spaces + f"└──{folder} /")

                    already_printed.add(parts_so_far)

            if max_rows is not None and i > max_rows - 1:
                tree._add_html(" " * indent * (j + 2) + "└──(...)")
                tree._add(" " * indent * (j + 2) + "└──(...)")
                break

            spaces = " " * indent * (j + 2)
            tree._add_html(
                f"<pre>{spaces}└──{split_path_and_make_copyable_html('/'.join(parts_so_far + (name,)), max_parts=1, display_prefix='')}<pre>",
            )
            tree._add(spaces + f"└──{name}")
    return tree


def _get_index_cols(schema: pyarrow.Schema, path_or_file: str | Path) -> list[str]:
    try:
        cols = json.loads(schema.metadata[b"pandas"])["index_columns"]
    except KeyError as e:
        raise KeyError(f"{e}. For {type(path_or_file)}: {path_or_file}")
    return [x for x in cols if not isinstance(x, dict)]


def _get_timestamps(date_strings: list[str] | str) -> pd.Timestamp | pd.DatetimeIndex:
    dates = pd.to_datetime(date_strings).round("s")
    try:
        dates = dates.tz_convert("Europe/Oslo").tz_localize(None)
    except TypeError:
        pass
    return dates.round("s")


def get_arguments(func: Callable | object) -> list[str]:
    """Get a list of a function's arguments."""
    relevant_keys = ["args", "varargs", "kwonlyargs"]
    specs: dict = inspect.getfullargspec(func)._asdict()
    return list(
        itertools.chain(
            *[specs[key] for key in relevant_keys if specs[key] is not None]
        )
    )


def get_schema(file) -> pyarrow.Schema:
    try:
        return pq.read_schema(file)
    except (
        PermissionError,
        pyarrow.ArrowInvalid,
        FileNotFoundError,
        IsADirectoryError,
        OSError,
    ) as e:
        # try:
        #     return ds.dataset(file).schema
        # except (TypeError, FileNotFoundError) as e:
        if not hasattr(file, "file_system"):
            raise e

        file_system = file.file_system

        def _get_schema(path):
            try:
                return pq.read_schema(path)
            except FileNotFoundError as e:
                try:
                    with file_system.open(path, "rb") as f:
                        return pq.read_schema(f)
                except Exception as e2:
                    raise e2.__class__(f"{e2}. {path}") from e

        child_paths = file_system.glob(file + "/**/*.parquet")
        if not len(child_paths):
            raise e.__class__(f"{e}: {file}") from e

        with ThreadPoolExecutor() as executor:
            schemas: list[pyarrow.Schema] = list(
                executor.map(_get_schema, file_system.glob(file + "/**/*.parquet"))
            )
        if not schemas:
            raise ValueError(f"Couldn't find any schemas among {child_paths}.") from e

        return pyarrow.unify_schemas(
            schemas,
            promote_options="permissive",
        )


def get_num_rows(file):
    try:
        return pq.read_metadata(file).num_rows
    except Exception as e:
        try:
            return ds.dataset(file).count_rows()
        except Exception as e2:
            if not hasattr(file, "glob"):
                raise e2 from 2

            def _get_num_rows(path):
                with path.open("rb") as file:
                    return pq.read_metadata(file).num_rows

            with ThreadPoolExecutor() as executor:
                return sum(executor.map(_get_num_rows, file.glob("**").files))


def get_shape(file) -> tuple[int, int]:
    schema = get_schema(file)
    index_cols = _get_index_cols(schema, file)
    ncol: int = sum(name not in index_cols for name in schema.names)
    nrow: int = get_num_rows(file)
    return nrow, ncol


def read_nrows(file, nrow: int) -> pd.DataFrame:
    """Read first n rows of a parquet file."""
    rows = next(pq.ParquetFile(file).iter_batches(nrow))
    return pyarrow.Table.from_batches([rows]).to_pandas()


def get_file_info(path) -> dict[str, str | float]:
    return {
        "updated": datetime.datetime.fromtimestamp(os.path.getmtime(path)),
        "size": os.path.getsize(path),
        "name": path,
        "type": "directory" if os.path.isdir(path) else "file",
    }


def is_hidden(path) -> bool:
    return any(part.startswith(".") for part in pathlib.Path(path).parts)


def as_str(obj) -> str:
    if isinstance(obj, str):
        return str(obj)
    if hasattr(obj, "__fspath__"):
        return obj.__fspath__()
    if hasattr(obj, "_str"):
        try:
            return str(obj._str())
        except TypeError:
            return str(obj._str)
    raise TypeError(type(obj))


def paths_are_equal(path1: Path | str, path2: Path | str) -> bool:
    return Path(path1).parts == Path(path2).parts


def sort_by_period(paths: Iterable[str]) -> Iterable[str]:
    try:
        periods = [pd.Timestamp(path.period) for path in paths]
    except ValueError:
        # select last period
        periods = [pd.Timestamp(next(iter(reversed(path.periods)))) for path in paths]
    combined = list(zip(periods, range(len(paths)), paths, strict=True))
    combined.sort()
    indices: list[int] = [x[1] for x in combined]
    try:
        return paths.iloc[indices]
    except AttributeError:
        return paths.__class__([x[2] for x in combined])


np_str_contains: Callable = np.vectorize(str.__contains__)
np_str_endswith: Callable = np.vectorize(str.endswith)
np_str_matches: Callable = np.vectorize(lambda txt, pat: bool(re.search(pat, txt)))
