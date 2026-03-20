# Tested on Metashape version 2.3.0

import Metashape
import math

doc = Metashape.app.document
chunk = doc.chunk  # base chunk

# -----------------------------
# PARAMETERES
# -----------------------------
grid_x = 6
grid_y = 6
overlap_percent = 30 # buffer (%)

# -----------------------------
# INFO ORIGINAL REGION 
# -----------------------------
region = chunk.region
center = region.center
rot = region.rot
size = region.size

# Tile size
dx = size.x / grid_x
dy = size.y / grid_y
dz = size.z

# lower corner
offset = center - rot * size / 2

new_chunks = []

print("Starting split...")

# -----------------------------
# LOOP GRID
# -----------------------------
for j in range(grid_y):
    for i in range(grid_x):

        print(f"Creating chunk {i+1},{j+1}")

        new_chunk = chunk.copy()
        new_chunk.label = f"tile_{i+1}_{j+1}"

        # -----------------------------
        # NEW REGION
        # -----------------------------
        new_center = Metashape.Vector([
            (i + 0.5) * dx,
            (j + 0.5) * dy,
            0.5 * dz
        ])

        new_center = offset + rot * new_center

        new_size = Metashape.Vector([dx, dy, dz])

        # aplicar overlap
        scale = 1 + overlap_percent / 100.0
        new_size = new_size * scale

        new_region = Metashape.Region()
        new_region.center = new_center
        new_region.size = new_size
        new_region.rot = rot

        new_chunk.region = new_region

        # -----------------------------
        # FILTER CAMERAS
        # -----------------------------
        cameras_to_remove = []

        for cam in new_chunk.cameras:
            if not cam.transform:
                continue

            coord = cam.center

            # transform 
            local = new_region.rot.t() * (coord - new_region.center)

            if (abs(local.x) > new_region.size.x / 2 or
                abs(local.y) > new_region.size.y / 2):
                cameras_to_remove.append(cam)

        print(f"Removing {len(cameras_to_remove)} cameras")

        new_chunk.remove(cameras_to_remove)

        # -----------------------------
        # CLEAN other data (if existed)
        # -----------------------------
        if new_chunk.depth_maps:
            new_chunk.depth_maps.clear()

        #  sparse
        if new_chunk.point_cloud:
            pts = new_chunk.point_cloud.points
            for p in pts:
                if not p.valid:
                    continue

                coord = p.coord
                local = new_region.rot.t() * (coord - new_region.center)

                if (abs(local.x) > new_region.size.x / 2 or
                    abs(local.y) > new_region.size.y / 2):
                    p.valid = False

            new_chunk.point_cloud.removeSelectedPoints()

        new_chunks.append(new_chunk)

        doc.save()

print("Split finished!")
