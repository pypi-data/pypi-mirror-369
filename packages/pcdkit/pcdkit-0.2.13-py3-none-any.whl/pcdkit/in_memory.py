from typing import Union

import numpy as np
from typing_extensions import Self

from .pcd_metadata import PCDMetadata
from .point_cloud import PointCloud
from .utils import insert_field, remove_field


class InMemoryPointCloud(PointCloud):
    """
    A PointCloud implementation that stores all data in system memory using a structured NumPy array.

    Attributes:
        metadata (PCDMetadata): Metadata describing the structure and properties of the point cloud.
        pc_data (np.ndarray): The structured NumPy array containing point cloud data.
    """

    def __init__(self, metadata: PCDMetadata, pc_data: np.ndarray):
        """
        Initialize an InMemoryPointCloud.

        Args:
            metadata (PCDMetadata): Metadata describing the point cloud.
            pc_data (np.ndarray): A structured NumPy array with point data.
        """
        self.metadata = metadata
        self.pc_data = pc_data

    def add_field(
        self,
        name: str,
        dtype: Union[str, type, np.dtype],
        default=0,
    ) -> Self:
        """
        Add a new field (column) to the point cloud data in memory.

        Args:
            name (str): The name of the new field.
            dtype (str or np.dtype): The data type of the new field.
            default (float): The default value to assign to all entries in the new field.

        Returns:
            Self: The updated InMemoryPointCloud instance.

        Raises:
            ValueError: If the field already exists.
        """
        self.pc_data = insert_field(self.pc_data, name, dtype, default)
        self.metadata.add_field(name, np.dtype(dtype))
        return self

    def drop_field(self, name: str) -> Self:
        """
        Remove a field (column) from the point cloud data in memory.

        Args:
            name (str): The name of the field to remove.

        Returns:
            Self: The updated InMemoryPointCloud instance.

        Raises:
            ValueError: If the field does not exist.
        """
        self.pc_data = remove_field(self.pc_data, name)
        self.metadata.remove_field(name)
        return self

    def drop_points(self, indices: np.ndarray) -> Self:
        """
        Drop points by indices and convert to unorganized (height=1) point cloud.

        Args:
            indices (np.ndarray): Indices to remove.

        Returns:
            Self: Updated point cloud with selected points removed.
        """
        if not np.issubdtype(indices.dtype, np.integer):
            raise TypeError("Indices must be an integer array.")

        total_points = self.pc_data.shape[0]
        mask = np.ones(total_points, dtype=bool)
        mask[indices] = False

        new_pc_data = self.pc_data[mask]

        self.pc_data = new_pc_data
        self.metadata.points = new_pc_data.shape[0]
        self.metadata.width = new_pc_data.shape[0]
        self.metadata.height = 1

        return self
