"""Caching decorator implementation for Polars DataFrames and LazyFrames."""

from __future__ import annotations

import functools
import hashlib
import os
import tempfile
import urllib.parse
from pathlib import Path
from typing import TYPE_CHECKING, overload

import diskcache
import polars as pl

from ._debugging import snoop
from ._parse_sizes import _parse_size

if TYPE_CHECKING:
    from .types import CallableFn, FilenameCallback

_DEFAULT_SYMLINK_NAME = "output.parquet"


class PolarsCache:
    """A diskcache wrapper for Polars DataFrames and LazyFrames with configurable readable cache structure."""

    def __init__(
        self,
        cache_dir: str | None = None,
        use_tmp: bool = False,
        hidden: bool = True,
        size_limit: int | str = "1GB",
        symlinks_dir: str = "functions",
        nested: bool = True,
        trim_arg: int = 50,
        symlink_name: str | FilenameCallback | None = None,
    ):
        """Initialise the cache.

        Args:
            cache_dir: Directory for cache storage. If None, uses current working directory.
            use_tmp: If True and cache_dir is None, put cache dir in system temp directory.
            hidden: If True, prefix directory name with dot (e.g. '.polars_cache').
            size_limit: Maximum cache size in bytes (int) or as a string. Default: "1GB".
            symlinks_dir: Name of the readable directory. Default: "functions".
            nested: If True, split module.function into module/function dirs.
                    If False, use percent-encoded function qualname as single dir.
            trim_arg: Maximum length for argument values in directory names.
            symlink_name: Custom name for symlink files. Can be a string or a callable
                          which will receive the function being cached, its args, its kwargs,
                          the result, and cache key. If None, uses default of "output.parquet".
        """
        if cache_dir is None:
            dir_name = ".polars_cache" if hidden else "polars_cache"
            if use_tmp:
                cache_dir = Path(tempfile.gettempdir()) / dir_name
            else:
                cache_dir = Path.cwd() / dir_name

        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True, parents=True)

        # Configuration
        self.symlink_name = symlink_name
        self.symlinks_dir_name = symlinks_dir
        self.nested = nested
        self.trim_arg = trim_arg

        # Use diskcache for metadata (function calls -> parquet file paths)
        self.cache = diskcache.Cache(
            str(self.cache_dir / "metadata"), size_limit=_parse_size(size_limit)
        )

        # Directory for parquet files (blobs)
        self.parquet_dir = self.cache_dir / "blobs"
        self.parquet_dir.mkdir(exist_ok=True)

        # Directory for readable structure
        self.readable_dir = self.cache_dir / self.symlinks_dir_name
        self.readable_dir.mkdir(exist_ok=True)

    def _get_cache_key(
        self,
        func: CallableFn[..., pl.DataFrame | pl.LazyFrame],
        args: tuple,
        kwargs: dict,
    ) -> str:
        """Generate a cache key from function name and arguments.

        Creates a unique hash-based key by combining the function's module path,
        qualname, and all arguments to ensure cache hits only occur for identical calls.

        Args:
            func: The function being cached.
            args: Positional arguments passed to the function.
            kwargs: Keyword arguments passed to the function.

        Returns:
            A SHA256 hash string representing the unique cache key.
        """
        # Create a string representation of the function call
        ident = f"{func.__module__}.{func.__qualname__}({args}, {kwargs})"
        # Hash it to get a consistent key
        cache_key = hashlib.sha256(ident.encode()).hexdigest()
        return cache_key

    def _get_parquet_path(self, cache_key: str) -> Path:
        """Get the parquet file path for a cache key (in blobs directory).

        Args:
            cache_key: The unique cache key for the cached result.

        Returns:
            Path object pointing to the parquet file location in the blobs directory.
        """
        return self.parquet_dir / f"{cache_key}.parquet"

    def _save_polars_result(
        self, result: pl.DataFrame | pl.LazyFrame, cache_key: str
    ) -> str:
        """Save a Polars DataFrame or LazyFrame to parquet and return the path.

        Args:
            result: The Polars DataFrame or LazyFrame to save.
            cache_key: The unique cache key for this result.

        Returns:
            String path to the saved parquet file.

        Raises:
            TypeError: If result is not a DataFrame or LazyFrame.
        """
        parquet_path = self._get_parquet_path(cache_key)

        if isinstance(result, pl.DataFrame):
            result.write_parquet(parquet_path)
        elif isinstance(result, pl.LazyFrame):
            result.sink_parquet(parquet_path)
        else:
            raise TypeError(f"Expected DataFrame or LazyFrame, got {type(result)}")

        return str(parquet_path)

    @overload
    def _load_polars_result(
        self, parquet_path: str, lazy: bool = True
    ) -> pl.LazyFrame: ...

    @overload
    def _load_polars_result(
        self, parquet_path: str, lazy: bool = False
    ) -> pl.DataFrame: ...

    def _load_polars_result(
        self, parquet_path: str, lazy: bool = False
    ) -> pl.DataFrame | pl.LazyFrame:
        """Load a Polars DataFrame or LazyFrame from parquet.

        Args:
            parquet_path: Path to the parquet file to load.
            lazy: If True, return a LazyFrame; if False, return a DataFrame.

        Returns:
            A Polars DataFrame if lazy=False, or LazyFrame if lazy=True.
        """
        if lazy:
            return pl.scan_parquet(parquet_path)
        else:
            return pl.read_parquet(parquet_path)

    def cache_polars(
        self,
        symlinks_dir: str | None = None,
        nested: bool | None = None,
        trim_arg: int | None = None,
        symlink_name: str | FilenameCallback | None = None,
    ):
        """Decorator for caching Polars DataFrames and LazyFrames.

        This decorator will cache function results that return Polars DataFrames or
        LazyFrames. The cache uses function signatures (module, name, args, kwargs)
        to determine cache hits. Results are stored as parquet files with metadata
        tracked via diskcache, and readable symlink structures are created for
        easy file system navigation.

        Args:
            symlinks_dir: Override instance setting for readable directory name.
            nested: Override instance setting for module path splitting.
            trim_arg: Override instance setting for max argument length.
            symlink_name: Override instance setting for symlink filename.

        Returns:
            A decorator function that can be applied to functions returning
            Polars DataFrames or LazyFrames.
        """
        # Use instance defaults if not overridden
        use_dir_name = (
            symlinks_dir if symlinks_dir is not None else self.symlinks_dir_name
        )
        use_split_module = nested if nested is not None else self.nested
        use_max_arg_len = trim_arg if trim_arg is not None else self.trim_arg
        use_symlink_name = (
            symlink_name if symlink_name is not None else self.symlink_name
        )

        def decorator(
            func: CallableFn[..., pl.DataFrame | pl.LazyFrame],
        ) -> CallableFn[..., pl.DataFrame | pl.LazyFrame]:
            @functools.wraps(func)
            def wrapper(*args, **kwargs):
                # Generate cache key
                cache_key = self._get_cache_key(func, args, kwargs)

                # Check if result is cached
                if cache_key in self.cache:
                    cached_data = self.cache[cache_key]
                    parquet_path = cached_data["path"]
                    is_lazy = cached_data["is_lazy"]

                    # Verify the parquet file still exists
                    if os.path.exists(parquet_path):
                        return self._load_polars_result(parquet_path, is_lazy)
                    else:
                        # File was deleted, remove from cache
                        del self.cache[cache_key]

                # Execute function and cache result
                result = func(*args, **kwargs)

                # Only cache if result is a DataFrame or LazyFrame
                if isinstance(result, (pl.DataFrame, pl.LazyFrame)):
                    is_lazy = isinstance(result, pl.LazyFrame)

                    # Save to parquet
                    parquet_path = self._save_polars_result(result, cache_key)

                    # Store path and type info in cache
                    self.cache[cache_key] = {"path": parquet_path, "is_lazy": is_lazy}

                    # Create readable symlink
                    # Temporarily override instance settings for this call
                    old_dir_name = self.symlinks_dir_name
                    old_split = self.nested
                    old_max_arg = self.trim_arg
                    old_symlink_name = self.symlink_name

                    self.symlinks_dir_name = use_dir_name
                    self.nested = use_split_module
                    self.trim_arg = use_max_arg_len
                    self.symlink_name = use_symlink_name

                    try:
                        self._create_readable_symlink(
                            func, args, kwargs, cache_key, result
                        )
                    finally:
                        # Restore instance settings
                        self.symlinks_dir_name = old_dir_name
                        self.nested = old_split
                        self.trim_arg = old_max_arg
                        self.symlink_name = old_symlink_name

                    return result

                return result

            return wrapper

        return decorator

    def _create_readable_symlink(
        self,
        func: CallableFn[..., pl.DataFrame | pl.LazyFrame],
        args: tuple,
        kwargs: dict,
        cache_key: str,
        result: pl.DataFrame | pl.LazyFrame,
    ):
        """Create a readable symlink structure pointing to the blob.

        Creates a human-readable directory structure with symlinks that point
        to the actual parquet files, making it easier to browse cached results
        in the file system. The structure can be nested (module/function/args)
        or flat (module.function/args) based on configuration.

        Args:
            func: The cached function.
            args: Positional arguments from the function call.
            kwargs: Keyword arguments from the function call.
            cache_key: The unique cache key for this result.
            result: The function result (used for determining file type).
        """
        # Get module and function info
        module_name = func.__module__
        func_qualname = func.__qualname__

        # Build the readable path structure
        if self.nested:
            # Split: readable_dir/encoded_module/encoded_qualname/args/
            encoded_module = urllib.parse.quote(module_name, safe="")
            encoded_qualname = urllib.parse.quote(func_qualname, safe="")
            readable_path = self.readable_dir / encoded_module / encoded_qualname
        else:
            # Flat: readable_dir/encoded_full_qualname/args/
            full_qualname = f"{module_name}.{func_qualname}"
            encoded_qualname = urllib.parse.quote(full_qualname, safe="")
            readable_path = self.readable_dir / encoded_qualname

        # Create args directory name
        args_parts = []
        for i, arg in enumerate(args):
            arg_str = str(arg)[: self.trim_arg]
            encoded_arg = urllib.parse.quote(arg_str, safe="")
            args_parts.append(f"arg{i}={encoded_arg}")

        for key, value in kwargs.items():
            value_str = str(value)[: self.trim_arg]
            encoded_value = urllib.parse.quote(value_str, safe="")
            args_parts.append(f"{key}={encoded_value}")

        args_dir_name = "_".join(args_parts) if args_parts else "no_args"
        final_readable_dir = readable_path / args_dir_name
        final_readable_dir.mkdir(parents=True, exist_ok=True)

        # Determine filename based on result type
        if callable(self.symlink_name):
            try:
                symlink_name = self.symlink_name(func, args, kwargs, result, cache_key)
                if not isinstance(symlink_name, str) or not symlink_name.strip():
                    symlink_name = _DEFAULT_SYMLINK_NAME
            except Exception:
                symlink_name = _DEFAULT_SYMLINK_NAME
        elif isinstance(self.symlink_name, str):
            symlink_name = self.symlink_name
        else:
            symlink_name = _DEFAULT_SYMLINK_NAME

        # Create symlink
        symlink_path = final_readable_dir / symlink_name
        blob_path = self.parquet_dir / f"{cache_key}.parquet"

        # Create relative path for symlink
        try:
            relative_blob = os.path.relpath(blob_path, final_readable_dir)
            if not symlink_path.exists():
                symlink_path.symlink_to(relative_blob)
        except (OSError, FileExistsError):
            # Symlink creation failed, but that's okay - cache still works
            pass

    def clear(self):
        """Clear all cached data.

        Removes all cached metadata, parquet files, and the readable symlink
        structure. This completely resets the cache to an empty state while
        preserving the cache directory structure for future use.
        """
        self.cache.clear()
        # Remove parquet files
        for parquet_file in self.parquet_dir.glob("*.parquet"):
            parquet_file.unlink()
        # Remove readable structure
        if self.readable_dir.exists():
            import shutil

            shutil.rmtree(self.readable_dir, ignore_errors=True)
            self.readable_dir.mkdir(exist_ok=True)


class _DummyCache:
    """A dummy cache that does nothing - just executes functions normally."""

    cache_dir = None

    def cache_polars(self, **kwargs):
        """Return a no-op decorator that doesn't cache anything.

        Args:
            **kwargs: Ignored keyword arguments for compatibility.

        Returns:
            A decorator that returns the original function unchanged.
        """

        def decorator(func):
            return func  # Just return the original function unchanged

        return decorator


# Convenience function for creating a global cache instance. Initialise with dummy cache
_global_cache: PolarsCache | _DummyCache = _DummyCache()


@snoop()
def cache(
    cache_dir: str | None = None,
    use_tmp: bool = False,
    hidden: bool = True,
    size_limit: int | str = "1GB",
    symlinks_dir: str = "functions",
    nested: bool = True,
    trim_arg: int = 50,
    symlink_name: str | None = None,
):
    """Convenience decorator for caching Polars DataFrames and LazyFrames.

    This function provides a simple interface to create and use a global cache
    instance for decorating functions that return Polars DataFrames or LazyFrames.
    On first call, it initializes the global cache with the provided settings.
    Subsequent calls will reuse the existing cache unless a different cache_dir
    is specified.

    Args:
        cache_dir: Directory for cache storage. If None, uses current working directory
                   or system temp directory if use_tmp is True.
        use_tmp: If True and cache_dir is None, put cache dir in system temp directory.
        hidden: If True, prefix directory name with dot (e.g. '.polars_cache').
        size_limit: Maximum cache size in bytes (int) or as a string. Default: "1GB".
        symlinks_dir: Name of the readable directory ("functions", "cache", etc.).
        nested: If True, split module.function into module/function dirs.
                If False, use encoded full qualname as single dir.
        trim_arg: Maximum length for argument values in directory names.
        symlink_name: Custom name for symlink files. If None, uses default.

    Returns:
        A decorator function that can be applied to functions returning
        Polars DataFrames or LazyFrames.

    Example:
        ```python
        from plcache import cache

        @cache(cache_dir="./my_cache", size_limit="500MB")
        def load_data() -> pl.DataFrame:
            return pl.read_csv("large_file.csv")
        ```
    """
    global _global_cache
    uncached = isinstance(_global_cache, _DummyCache)

    # Create new cache if we're still using the dummy (first call to `cache()`)
    if uncached or (
        cache_dir is not None and Path(_global_cache.cache_dir) != Path(cache_dir)
    ):
        _global_cache = PolarsCache(
            cache_dir=cache_dir,
            use_tmp=use_tmp,
            hidden=hidden,
            size_limit=_parse_size(size_limit),
            symlinks_dir=symlinks_dir,
            nested=nested,
            symlink_name=symlink_name,
            trim_arg=trim_arg,
        )

    return _global_cache.cache_polars(
        symlinks_dir=symlinks_dir,
        nested=nested,
        trim_arg=trim_arg,
        symlink_name=symlink_name,
    )
