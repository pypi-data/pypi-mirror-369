import copy
from pathlib import Path
from typing import List, Optional

import numpy as np

from .in_memory import InMemoryPointCloud
from .memmap import MemMapPointCloud
from .pcd_loader import PCDLoader
from .pcd_metadata import PCDMetadata
from .point_cloud import PointCloud
from .typings import PathLike


def merge(
    clouds: List["PointCloud"],
    memmap_file_path: Optional[PathLike] = None,
) -> "PointCloud":
    """
    Merge multiple PointCloud instances into a single PointCloud.

    Args:
        clouds (List[PointCloud]): A list of PointCloud instances to merge.
        memmap_file_path (Optional[PathLike]): Optional path to store the merged point cloud as a memory-mapped file.

    Returns:
        PointCloud: A new PointCloud instance containing the merged data.

    Raises:
        ValueError: If the input list is empty or if the point clouds have mismatched data types.
    """
    if not clouds:
        raise ValueError("At least one PointCloud must be provided")

    first_dtype = clouds[0].pc_data.dtype
    for c in clouds:
        if c.pc_data.dtype != first_dtype:
            raise ValueError("All PointClouds must have the same dtype structure")

    merged_data = np.concatenate([c.pc_data for c in clouds])
    merged_metadata = copy.deepcopy(clouds[0].metadata)
    merged_metadata.points = len(merged_data)
    merged_metadata.width = merged_metadata.points // merged_metadata.height

    return _create(merged_metadata, merged_data, memmap_file_path)


def load_pcd_from_path(
    file_path: PathLike,
    memmap_file_path: Optional[PathLike] = None,
    replace_nan_with_zero: bool = False,
) -> "PointCloud":
    """
    Load a PointCloud from a .pcd file path.

    Args:
        file_path (PathLike): Path to the PCD file.
        memmap_file_path (Optional[PathLike]): Optional path to store the data as a memory-mapped file.
        replace_nan_with_zero (bool): If True, replace NaN values with zero.

    Returns:
        PointCloud: A new PointCloud instance loaded from the file.
    """
    with Path(file_path).open("rb") as f:
        loader = PCDLoader(f)
        pc_data = loader.load(replace_nan_with_zero)
    return _create(loader.metadata, pc_data, memmap_file_path)


def from_array(
    array: np.ndarray,
    memmap_file_path: Optional[PathLike] = None,
) -> "PointCloud":
    """
    Create a PointCloud from a structured NumPy array.

    Args:
        array (np.ndarray): A structured NumPy array with named fields.
        memmap_file_path (Optional[PathLike]): Optional path to store the data as a memory-mapped file.

    Returns:
        PointCloud: A new PointCloud instance wrapping the provided array.

    Raises:
        ValueError: If the input array does not have named fields.
    """
    if not array.dtype.names:
        raise ValueError("Input array must be a structured array with named fields")
    metadata = PCDMetadata.from_array(array)
    return _create(metadata, array, memmap_file_path)


def _create(
    metadata: PCDMetadata,
    array: np.ndarray,
    memmap_file_path: Optional[PathLike],
) -> "PointCloud":
    """
    Internal helper to instantiate the appropriate PointCloud subclass.

    Args:
        metadata (PCDMetadata): Metadata for the point cloud.
        array (np.ndarray): The point cloud data.
        memmap_file_path (Optional[PathLike]): Path to use memory mapping if specified.

    Returns:
        PointCloud: An InMemoryPointCloud or MemMapPointCloud instance.
    """
    cls = MemMapPointCloud if memmap_file_path else InMemoryPointCloud
    return cls(metadata, array, memmap_file_path) if memmap_file_path else cls(metadata, array)
