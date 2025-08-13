import os
import logging
import tarfile
from pathlib import Path

from .utils import timed_fn, safe_unlink, CacheValidationError
from .constants import TAR_COMPRESSION_LEVEL, MAX_CACHE_SIZE_MB

logger = logging.getLogger(__name__)


class ArchiveError(Exception):
    """Archive operation failed."""

    pass


def validate_path(path: Path, allowed_prefixes: list[str]) -> None:
    """Validate that a file path is within allowed directory prefixes for security.

    This function prevents directory traversal attacks by ensuring that resolved
    paths only point to locations within specified allowed directories.

    Args:
        path: The file path to validate.
        allowed_prefixes: List of allowed directory prefix strings that the
                         resolved path must start with.

    Raises:
        CacheValidationError: If the resolved path is not within any of the
                            allowed prefixes.
    """
    resolved_path = str(path.resolve())

    if any(resolved_path.startswith(prefix) for prefix in allowed_prefixes):
        return

    raise CacheValidationError(
        f"Path {resolved_path} outside allowed: {allowed_prefixes}"
    )


def get_file_size_mb(file_path: Path) -> float:
    """Get the size of a file in megabytes.

    Args:
        file_path: Path to the file to measure.

    Returns:
        float: File size in megabytes, or 0.0 if file doesn't exist or
               can't be accessed.

    Raises:
        No exceptions are raised; OSError is caught and returns 0.0.
    """
    try:
        return file_path.stat().st_size / (1024 * 1024)
    except OSError:
        return 0.0


def _compress_directory_to_tar(source_dir: Path, target_file: Path) -> None:
    """Compress directory contents to a gzipped tar archive.

    This function recursively compresses all files in the source directory
    into a gzipped tar archive, preserving relative paths within the archive.

    Args:
        source_dir: Path to the directory to compress.
        target_file: Path where the compressed archive will be created.

    Raises:
        OSError: If source directory can't be read or target file can't be written.
        TarError: If archive creation fails.
    """
    with tarfile.open(target_file, "w:gz", compresslevel=TAR_COMPRESSION_LEVEL) as tar:
        for item in source_dir.rglob("*"):
            if item.is_file():
                arcname = item.relative_to(source_dir)
                tar.add(item, arcname=arcname)


@timed_fn(logger=logger, name="Creating archive")
def create_archive(
    source_dir: Path, target_file: Path, max_size_mb: int = MAX_CACHE_SIZE_MB
) -> None:
    """Create a compressed archive with path validation and size limits.

    This function safely creates a gzipped tar archive from a source directory
    with security validation and size constraints. It validates paths to prevent
    directory traversal attacks and enforces maximum archive size limits.

    Args:
        source_dir: Path to the directory to archive. Must exist and be within
                   allowed directories (/tmp/ or its parent).
        target_file: Path where the archive will be created. Must be within
                    allowed directories (/app or /cache).
        max_size_mb: Maximum allowed archive size in megabytes. Defaults to MAX_CACHE_SIZE_MB.

    Raises:
        CacheValidationError: If paths are outside allowed directories.
        ArchiveError: If source directory doesn't exist, archive creation fails,
                     or archive exceeds size limit.
    """
    # Validate paths
    validate_path(source_dir, ["/tmp/", str(source_dir.parent)])
    validate_path(target_file, ["/app", "/cache"])

    if not source_dir.exists():
        raise ArchiveError(f"Source directory missing: {source_dir}")

    target_file.parent.mkdir(parents=True, exist_ok=True)

    try:
        _compress_directory_to_tar(source_dir, target_file)
        size_mb = get_file_size_mb(target_file)

        if size_mb > max_size_mb:
            safe_unlink(
                target_file, f"Failed to delete oversized archive {target_file}"
            )
            raise ArchiveError(f"Archive too large: {size_mb:.1f}MB > {max_size_mb}MB")

    except Exception as e:
        safe_unlink(target_file, f"Failed to cleanup failed archive {target_file}")
        raise ArchiveError(f"Archive creation failed: {e}") from e


@timed_fn(logger=logger, name="Extracting archive")
def extract_archive(archive_file: Path, target_dir: Path) -> None:
    """Extract a compressed archive with security validation.

    This function safely extracts a gzipped tar archive to a target directory
    with security checks to prevent directory traversal attacks. It validates
    both the archive and target paths, and inspects archive contents for
    malicious paths before extraction.

    Args:
        archive_file: Path to the archive file to extract. Must exist and be
                     within allowed directories (/app or /cache).
        target_dir: Path to the directory where files will be extracted. Must
                   be within allowed directories (/tmp/ or its parent).

    Raises:
        CacheValidationError: If paths are outside allowed directories or if
                            archive contains unsafe paths (absolute paths or
                            paths with '..' components).
        ArchiveError: If archive file doesn't exist or extraction fails.
    """
    # Validate paths
    validate_path(archive_file, ["/app", "/cache"])
    validate_path(target_dir, ["/tmp/", str(target_dir.parent)])

    if not archive_file.exists():
        raise ArchiveError(f"Archive missing: {archive_file}")

    try:
        target_dir.mkdir(parents=True, exist_ok=True)

        with tarfile.open(archive_file, "r:gz") as tar:
            # Security check
            for member in tar.getmembers():
                if os.path.isabs(member.name) or ".." in member.name:
                    raise CacheValidationError(f"Unsafe path in archive: {member.name}")

            tar.extractall(path=target_dir)

    except Exception as e:
        raise ArchiveError(f"Extraction failed: {e}") from e
