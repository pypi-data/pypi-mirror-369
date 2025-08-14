# PCDKit

A lightweight and efficient Python library for working with PCD (Point Cloud Data) files.  
Supports both in-memory and memory-mapped processing, and provides modular tools for I/O, transformation, merge and metadata management.

## 📦 Features

- ✅ Read/write PCD files (ASCII, binary, and compressed)
- ✅ Structured NumPy or memory-mapped point cloud representation
- ✅ Add/drop/set custom fields
- ✅ Apply geometric transformations (e.g., rotation, translation)
- ✅ Metadata-aware, type-safe interface

## 🚀 Installation

```bash
pip install pcdkit
```

## 🧪 Usgae

```python
from pathlib import Path

import numpy as np
import pcloud

# Create a structured NumPy array with 5 3D points
array = np.array([
    (1.0, 2.0, 3.0),
    (4.0, 5.0, 6.0),
    (7.0, 8.0, 9.0),
    (10.0, 11.0, 12.0),
    (13.0, 14.0, 15.0),
], dtype=[("x", "f4"), ("y", "f4"), ("z", "f4")])

# Temporary paths for saving memory-mapped file and PCD
memmap_path = Path("test.memmap")
pcd_path = Path("test.pcd")

# ----------------------------
# 1. Construct PointCloud from NumPy array
# ----------------------------
cloud = pcloud.from_array(array, memmap_file_path=memmap_path)

# Add a new field called 'intensity' with default value 1.0
cloud.add_field("intensity", "f4", default=1.0)

# Set the intensity field to a constant value
cloud.set_field("intensity", 5.0)

# Overwrite the intensity field with a per-point array
cloud.set_field("intensity", np.array([10, 20, 30, 40, 50]))

# Apply an affine transformation (scale coordinates by 2)
transform = np.eye(4)
transform[:3, :3] *= 2
cloud.transform(transform)

# Drop the intensity field
cloud.drop_field("intensity")

# Save the point cloud to a binary PCD file
cloud.save(pcd_path, format="binary")
print(f"Saved PointCloud from array to: {pcd_path}")

# ----------------------------
# 2. Load the saved PCD back and verify structure
# ----------------------------
cloud_loaded = pcloud.load_pcd_from_path(
    file_path=pcd_path,
    memmap_file_path=memmap_path.with_suffix(".reloaded.memmap"),
    replace_nan_with_zero=True,
)

print("Reloaded PointCloud:")
print(cloud_loaded)

# ----------------------------
# 3. Merge the original and reloaded clouds
# ----------------------------
merged_cloud = pcloud.merge(
    [cloud, cloud_loaded],
    memmap_file_path=Path("merged.memmap")
)

print("Merged PointCloud:")
print(merged_cloud)
merged_cloud.save("merged.pcd", format="binary")


```
