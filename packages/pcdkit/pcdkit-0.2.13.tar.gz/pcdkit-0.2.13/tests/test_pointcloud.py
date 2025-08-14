from pathlib import Path

import numpy as np

from pcdkit import (
    MemMapPointCloud,
    PointCloud,
    from_array,
    merge,
)


def make_structured_xyz(n=10):
    return np.array(
        [(i, i * 2, i * 3) for i in range(n)],
        dtype=[("x", "f4"), ("y", "f4"), ("z", "f4")],
    )


def test_inmemory_add_drop_set_transform(tmp_path):
    arr = make_structured_xyz(5)
    cloud = from_array(arr)

    # test add_field
    cloud.add_field("intensity", "f4", default=1.0)
    assert "intensity" in cloud.pc_data.dtype.names
    assert np.all(cloud.pc_data["intensity"] == 1.0)

    # test set_field constant
    cloud.set_field("intensity", 5.0)
    assert np.all(cloud.pc_data["intensity"] == 5.0)

    # test set_field array
    new_vals = np.array([10, 20, 30, 40, 50], dtype="f4")
    cloud.set_field("intensity", new_vals)
    assert np.all(cloud.pc_data["intensity"] == new_vals)

    # test transform
    transform = np.eye(4)
    transform[:3, :3] *= 2  # scale
    cloud.transform(transform)
    assert np.all(cloud.pc_data["x"] == arr["x"] * 2)

    # test drop_field
    cloud.drop_field("intensity")
    assert "intensity" not in cloud.pc_data.dtype.names

    # test save
    save_path = tmp_path / "test.pcd"
    cloud.save(save_path, format="binary")
    assert save_path.exists()

    # test drop_points
    cloud = from_array(make_structured_xyz(5))
    cloud.drop_points(np.array([0, 2]))
    assert cloud.pc_data.shape[0] == 3
    assert cloud.metadata.points == 3
    assert cloud.metadata.height == 1
    assert cloud.metadata.width == 3
    np.testing.assert_array_equal(cloud.pc_data["x"], np.array([1, 3, 4], dtype="f4"))


def test_memmap_add_drop_set(tmp_path):
    arr = make_structured_xyz(5)
    mmap_path = tmp_path / "memmap.bin"

    cloud = from_array(arr, memmap_file_path=mmap_path)
    assert isinstance(cloud, MemMapPointCloud)

    # test add_field
    cloud.add_field("intensity", "f4", default=2.0)
    assert "intensity" in cloud.pc_data.dtype.names
    assert np.all(cloud.pc_data["intensity"] == 2.0)

    # test set_field + flush
    cloud.set_field("intensity", 7.0)
    assert np.all(cloud.pc_data["intensity"] == 7.0)

    # test drop_field
    cloud.drop_field("intensity")
    assert "intensity" not in cloud.pc_data.dtype.names

    # test save
    save_path = tmp_path / "out.pcd"
    cloud.save(save_path, format="binary_compressed")
    assert save_path.exists()

    # test drop_points
    cloud = from_array(make_structured_xyz(5), memmap_file_path=mmap_path)
    cloud.drop_points(np.array([1, 3]))
    assert cloud.pc_data.shape[0] == 3
    assert cloud.metadata.points == 3
    assert cloud.metadata.height == 1
    assert cloud.metadata.width == 3
    np.testing.assert_array_equal(cloud.pc_data["y"], np.array([0, 4, 8], dtype="f4"))


def create_test_cloud(values: list[tuple[float, float, float]]) -> PointCloud:
    arr = np.array(values, dtype=[("x", "f4"), ("y", "f4"), ("z", "f4")])
    return from_array(arr)


def test_pointcloud_merge(tmp_path: Path):
    # Create two point clouds
    cloud1 = create_test_cloud([(1, 2, 3), (4, 5, 6)])
    cloud2 = create_test_cloud([(7, 8, 9)])

    # Merge them
    merged = merge([cloud1, cloud2], memmap_file_path=tmp_path / "merged.memmap")

    # Assert shape
    assert merged.pc_data.shape == (3,)
    assert merged.metadata.points == 3

    # Assert content
    expected = np.array(
        [
            (1.0, 2.0, 3.0),
            (4.0, 5.0, 6.0),
            (7.0, 8.0, 9.0),
        ],
        dtype=merged.pc_data.dtype,
    )

    np.testing.assert_array_equal(merged.pc_data, expected)

    # Check if memmap file exists
    assert (tmp_path / "merged.memmap").exists()
