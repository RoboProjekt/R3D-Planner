"""Carry measured point colours onto uncovered mesh vertices within a bounded support radius."""
import argparse
from pathlib import Path

import numpy as np
from scipy.spatial import cKDTree

from fuse_lyra_lidar import BASE, read_pcd, xyz


def fallback(work, measured_cloud=Path('reports/20261123_kamerakarte/karte_rgb.pcd')):
    cloud = read_pcd(measured_cloud, BASE)
    coloured = cloud[cloud['views'] > 0]
    tree = cKDTree(xyz(coloured))
    rgb = np.column_stack([(coloured['rgb'].view('u4') >> shift) & 255 for shift in (16, 8, 0)])
    with np.load(work/'surface.npz') as surface:
        verts = surface['v']
    colors = np.full((len(verts), 3), 124, dtype='u1')
    covered = 0
    for start in range(0, len(verts), 80000):
        pts = verts[start:start+80000]
        ds, ix = tree.query(pts, k=4, distance_upper_bound=.14, workers=4)
        valid = np.isfinite(ds[:, 0])
        weights = 1 / np.maximum(ds[valid], .01)**2
        values = rgb[np.minimum(ix[valid], len(rgb)-1)]
        colors[start:start+len(pts)][valid] = np.round((values*weights[:, :, None]).sum(1) / weights.sum(1)[:, None])
        covered += valid.sum()
    np.save(work/'fallback.npy', colors)
    print('Point colour supported vertices', covered, '/', len(verts))


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work', type=Path)
    fallback(parser.parse_args().work)
