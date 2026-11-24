"""Measure the exported floor profile along a straight traversal, for evaluation only."""
import argparse
import json
from pathlib import Path

import numpy as np
from scipy.ndimage import gaussian_filter1d


def floor_profile(run, start, end, length, transform=None):
    with np.load(run/'outputs.npz') as data:
        track = data['trajectory']
    time = track[:, 0] - track[0, 0]
    traverse = track[(time >= start) & (time <= end), 1:4]
    if not (0 <= start < end <= time[-1] and len(traverse) >= 3 and length >= 2):
        raise ValueError('Select a straight traversal within this recording and a length of at least 2 m')
    if transform is not None:
        traverse = traverse @ transform[:3, :3].T + transform[:3, 3]
    xy = traverse[:, :2]
    _, _, axes = np.linalg.svd(xy-xy.mean(axis=0), full_matrices=False)
    direction = axes[0] * np.sign((xy[-1]-xy[0]) @ axes[0])
    centre = xy.mean(axis=0) + direction*((xy[0]-xy.mean(axis=0)) @ direction)
    along = (xy-centre) @ direction
    if np.max(along) < length-.5:
        raise ValueError('The selected traversal is shorter than the requested profile')
    with (run/'karte.pcd').open('rb') as f:
        header = {}
        for line in f:
            key, _, value = line.strip().partition(b' ')
            header[key] = value
            if key == b'DATA':
                break
        if (header.get(b'DATA'), header.get(b'FIELDS'), header.get(b'SIZE'), header.get(b'TYPE'),
                header.get(b'COUNT')) != (b'binary', b'x y z', b'4 4 4', b'F F F', b'1 1 1'):
            raise ValueError('Expected a binary XYZ PCD from the Hesai mapper')
        points = np.fromfile(f, '<f4').reshape(int(header[b'POINTS']), 3)
    if transform is not None:
        points = points @ transform[:3, :3].T + transform[:3, 3]
    offset = points[:, :2]-centre
    s = offset @ direction
    strip = abs(offset @ np.array([-direction[1], direction[0]])) <= .8
    heights = []
    for station in range(length+1):
        sensor_z = traverse[np.argmin(abs(along-station)), 2]
        z = points[strip & (abs(s-station) <= .5), 2]
        bins = np.arange(sensor_z-1.45, sensor_z-.12, .04)
        z = z[(z >= bins[0]) & (z < bins[-1])]
        hist = np.histogram(z, bins)[0]
        peak = bins[np.argmax(gaussian_filter1d(hist.astype(float), 1.15))]+.02
        floor = z[abs(z-peak) < .09]
        if len(floor) < 12:
            raise ValueError(f'Insufficient floor evidence at station {station} m')
        heights.append(float(np.median(floor)))
    return {'station_m': list(range(length+1)), 'floor_z_m': heights,
            'rise_m': heights[-1]-heights[0], 'height_range_m': max(heights)-min(heights)}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('run', type=Path, nargs='+')
    parser.add_argument('--traversal', nargs=2, type=float, required=True, metavar=('START_S', 'END_S'),
                        help='Seconds since the first LiDAR pose')
    parser.add_argument('--length', type=int, required=True, help='Profile length in metres')
    parser.add_argument('--level-as', type=Path, metavar='RUN',
                        help='Apply only the building-frame rotation of another export from the same recording')
    args = parser.parse_args()
    transform = None
    if args.level_as:
        reference = json.loads((args.level_as/'metrics.json').read_text())
        if reference['map_frame'] != 'building_level':
            parser.error('The reference run needs a confirmed building vertical')
        transform = np.asarray(reference['map_from_first_lidar_scan'])
    results = {}
    for run in args.run:
        if transform is not None:
            info = json.loads((run/'metrics.json').read_text())
            if info['map_frame'] != 'first_lidar_scan' or info.get('origin_ns') != reference.get('origin_ns'):
                parser.error('Compare first-scan maps with the same recording origin')
        results[str(run)] = floor_profile(run, *args.traversal, args.length, transform)
    print(json.dumps(results, indent=2))
