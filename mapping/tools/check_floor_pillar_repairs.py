"""Probe repaired architecture and nearby openings on both sides of an export."""
import json

import numpy as np


def cases(model_dir, architecture):
    fitted = json.loads((model_dir / "geometry.json").read_text())
    origins, directions, limits, expected, labels = [], [], [], [], []

    def add(origin, direction, limit, distance, label):
        origins.append(origin)
        directions.append(direction)
        limits.append(limit)
        expected.append(distance)
        labels.append(label)

    for x, y, z in np.load(model_dir / "floor_probes.npy"):
        add([x, y, z + .22], [0, 0, -1], .31, .22, "floor")
    for c in fitted["solid_columns"]:
        for z in np.linspace(c["bottom"] + .16, c["top"] - .16, 9):
            for t in (.20, .50, .80):
                x = c["x0"] * (1 - t) + c["x1"] * t
                # The rear is embedded in the corridor wall.
                y = c["front_y"] * (1 - t) - 6.42 * t
                add([x, c["front_y"] - .09, z], [0, 1, 0], .15, .09, "pier_front")
                add([c["x0"] - .09, y, z], [1, 0, 0], .15, .09, "pier_flank")
                add([c["x1"] + .09, y, z], [-1, 0, 0], .15, .09, "pier_flank")
    for s in fitted["landing_guard_segments"]:
        axis = s["axis"]
        direction = np.eye(3)[axis]
        for ts, wanted, label in [(s["posts"], .026, "landing_post"),
                                  ([(a+b)*.5 for a,b in zip(s["posts"],s["posts"][1:])
                                    if .075 < b-a < .155], -1, "landing_gap")]:
            for t in ts:
                origin = np.zeros(3)
                origin[1-axis] = t
                # Approach posts from +axis. At the corner the adjacent
                # perpendicular run extends into the negative-axis approach.
                post = label=="landing_post"
                origin[axis] = s["level"] + (.04 if post else -.10)
                origin[2] = s["floor"] + .47
                add(origin, -direction if post else direction, .18, wanted, label)
    z = architecture["steps"][-1,1]
    if 'surface_evidence' in fitted:
        from filter_surface_evidence import measured_post_gaps
        for recess in fitted['surface_evidence']['surveyed_recesses']:
            if not recess.get('enclosed') or 'front' not in recess:
                continue
            axis=recess['axis']
            direction=np.eye(3)[axis]*np.sign(recess['rear']-recess['front'])
            for along in np.linspace(recess['along_min']+.21,recess['along_max']-.21,5):
                for height in np.linspace(recess['bottom']+.24,recess['top']-.22,5):
                    origin=np.zeros(3);origin[axis]=recess['front']-.10*direction[axis]
                    origin[1-axis]=along;origin[2]=height
                    depth=abs(recess['rear']-recess['front'])+.10
                    add(origin,direction,depth+.10,depth,'recess_back')
        with np.load(model_dir/'rail.npz') as rail:
            pairs=measured_post_gaps(rail['v']@architecture['b'],rail['f'])
        for first,last in pairs:
            mid=(first+last)*.5
            width=np.linalg.norm(last[:2]-first[:2])
            if not (.075<width<.145 and architecture['steps'][0,0]<mid[1]<architecture['steps'][-1,0]-.15):
                continue
            if abs(mid[0]-architecture['stair_bounds'][1])>.085:
                continue
            normal=np.r_[last[1]-first[1],first[0]-last[0],0]/width
            for t in (.33,.65):
                point=np.r_[mid[:2],(1-t)*mid[2]+t*mid[3]]
                add(point-.085*normal,normal,.17,-1,'stair_guard_gap')
    for x in np.arange(-10.20,-8.14,.3):
        for y in np.arange(-12.76,-9.91,.35):
            add([x, y, z + .09], [0,0,-1], .38, -1, "atrium")
    basis = architecture["b"].T
    return dict(origins=np.array(origins) @ basis, directions=np.array(directions) @ basis,
                limits=np.array(limits), expected=np.array(expected), labels=np.array(labels))


def summarize(probes, hits):
    results = {}
    for label in np.unique(probes["labels"]):
        mask = probes["labels"] == label
        distance = hits[mask]
        wanted = probes["expected"][mask]
        tolerance = .010 if label=="landing_post" else .035
        valid = np.where(wanted < 0, distance > probes["limits"][mask],
                         np.abs(distance-wanted) < tolerance)
        results[str(label)] = {"passed": int(valid.sum()), "total": len(valid)}
    return results


if __name__ == "__main__":
    import argparse
    from pathlib import Path
    import open3d as o3d
    from check_building_photos import Model

    parser = argparse.ArgumentParser(description=__doc__)
    for name in ["model_dir","architecture","old","new","results_dir"]:
        parser.add_argument(name,type=Path)
    args = parser.parse_args()
    probes = cases(args.model_dir, np.load(args.architecture))
    np.savez(args.results_dir/"probes.npz", **probes)
    rays = o3d.core.Tensor(np.c_[probes["origins"],probes["directions"]].astype("f4"))
    results = {}
    for key, path in [("previous",args.old),("repaired",args.new)]:
        model = Model(path)
        hits = model.scene.cast_rays(rays,nthreads=5)["t_hit"].numpy()
        results[key] = summarize(probes,hits)
        if key=="repaired":
            np.save(args.results_dir/"visible_hits.npy",hits)
    (args.results_dir/"visible.json").write_text(json.dumps(results,indent=2))
    print(json.dumps(results),flush=True)
