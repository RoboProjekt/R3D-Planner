"""Open the native mesh, with a route through the building and free viewport navigation."""
import asyncio
import math
import os
from pathlib import Path
import time

import carb.input
import numpy as np
import omni.appwindow
import omni.kit.app
import omni.ui as ui
import omni.usd
from omni.kit.viewport.utility import get_active_viewport_window
from omni.kit.viewport.utility.camera_state import ViewportCameraState
from pxr import Gf, Usd


class MeshNavigation:
    def __init__(self, window, poses, bookmarks=(0,65,115), segment=None):
        self.window = window
        self.stage = window.viewport_api.stage
        self.poses = poses
        lengths=np.linalg.norm(np.diff(poses[:, :3, 3], axis=0), axis=1)
        if segment is not None:
            lengths[np.diff(segment)!=0]=0.
        self.distance = np.r_[0.,np.cumsum(lengths)]
        self.at = 0.
        self.window.viewport_api.camera_path = '/OmniverseKit_Persp'
        self.camera = ViewportCameraState('/OmniverseKit_Persp', self.window.viewport_api)
        self.bar = window.get_frame('Gebaeudenavigation')
        with self.bar:
            with ui.VStack(height=52):
                with ui.HStack(height=30, spacing=4):
                    for i, name in zip(bookmarks,('Treppenfuß','Podest','Flur 1. OG')):
                        ui.Button(name, width=100, clicked_fn=lambda i=i: self.go(self.distance[i]))
                    ui.Button('Zurück', width=70, clicked_fn=lambda: self.follow(-.6))
                    ui.Button('Vor', width=60, clicked_fn=lambda: self.follow(.6))
                ui.Label('WASD bewegen · Q runter / E hoch · Rechte Maustaste ziehen zum Umsehen · ↑/↓ Route',
                         height=22, tooltip='←/→ drehen · Bild ↑/↓ nach oben/unten schauen · Umschalt schneller')
        self.input = carb.input.acquire_input_interface()
        app_window = omni.appwindow.get_default_app_window()
        self.keyboard = app_window.get_keyboard()
        self.mouse = app_window.get_mouse()
        self.last = time.monotonic()
        self.tick = omni.kit.app.get_app().get_update_event_stream().create_subscription_to_pop(self.move,name='Gebaeuderoute')
        self.go(self.distance[bookmarks[0]])
        window.focus()

    def go(self, metres):
        if self.window.viewport_api.stage != self.stage:
            return
        self.window.viewport_api.camera_path = '/OmniverseKit_Persp'
        self.at = float(np.clip(metres, 0., self.distance[-1]))
        j = int(np.clip(np.searchsorted(self.distance, self.at, side='right'), 1, len(self.poses)-1))
        t = (self.at-self.distance[j-1]) / max(self.distance[j]-self.distance[j-1],1.e-9)
        pose = (1-t)*self.poses[j-1] + t*self.poses[j]
        self.camera.set_position_world(Gf.Vec3d(*pose[:3,3]), False)
        self.camera.set_target_world(Gf.Vec3d(*(pose[:3,3]+2*pose[:3,2])), True)

    def follow(self, delta):
        if self.window.viewport_api.stage != self.stage:
            return
        if self.at is None:
            # Rejoin the nearest point along a segment, even between recorded poses.
            starts = self.poses[:-1, :3, 3]
            segments = self.poses[1:, :3, 3] - starts
            eye = np.asarray(self.camera.position_world)
            lengths = np.diff(self.distance)
            t = np.clip(np.einsum('ij,ij->i', eye-starts, segments) /
                        np.maximum(lengths**2, 1.e-12), 0., 1.)
            j = np.argmin(np.linalg.norm(starts + t[:, None]*segments - eye, axis=1))
            self.at = self.distance[j] + t[j]*lengths[j]
        self.go(self.at + delta)

    def move(self, event):
        now = time.monotonic()
        dt = min(.15,now-self.last)
        self.last = now
        vp = self.window.viewport_api
        if not self.window.focused or vp.stage != self.stage or str(vp.camera_path) != '/OmniverseKit_Persp':
            return
        keys = carb.input.KeyboardInput
        def pressed(key):
            return self.input.get_keyboard_value(self.keyboard, key) > 0
        if any(pressed(key) for key in (keys.LEFT_CONTROL, keys.RIGHT_CONTROL, keys.LEFT_ALT, keys.RIGHT_ALT)):
            return
        # Kit owns mouse look and simultaneous WASD while the right button is down.
        if self.input.get_mouse_value(self.mouse, carb.input.MouseInput.RIGHT_BUTTON):
            self.at = None
            return

        speed = 3.4 if pressed(keys.LEFT_SHIFT) or pressed(keys.RIGHT_SHIFT) else 1.7
        route = pressed(keys.UP) - pressed(keys.DOWN)
        if route:
            self.follow(dt * speed * route)
            return
        ahead = pressed(keys.W) - pressed(keys.S)
        side = pressed(keys.D) - pressed(keys.A)
        up = pressed(keys.E) - pressed(keys.Q)
        turn = pressed(keys.RIGHT) - pressed(keys.LEFT)
        tilt = pressed(keys.PAGE_UP) - pressed(keys.PAGE_DOWN)
        if not any((ahead, side, up, turn, tilt)):
            return

        # Read the actual viewport pose so native mouse look and keyboard motion agree.
        matrix = self.camera.usd_camera.ComputeLocalToWorldTransform(Usd.TimeCode.Default())
        look = matrix.TransformDir(Gf.Vec3d(0, 0, -1)).GetNormalized()
        yaw = math.atan2(look[0], look[1]) + turn * 1.6 * dt
        pitch = math.atan2(look[2], math.hypot(look[0], look[1]))
        sy, cy = math.sin(yaw), math.cos(yaw)
        motion = np.array([ahead*sy + side*cy, ahead*cy - side*sy, up])
        eye = np.asarray(matrix.ExtractTranslation())
        if ahead or side or up:
            eye = eye + motion * (speed * dt / np.linalg.norm(motion))
            self.camera.set_position_world(Gf.Vec3d(*eye), False)
        if turn or tilt:
            pitch = np.clip(pitch + tilt * 1.6 * dt, -math.radians(88), math.radians(88))
            forward = np.array([sy*math.cos(pitch), cy*math.cos(pitch), math.sin(pitch)])
            self.camera.set_target_world(Gf.Vec3d(*(eye + 2.*forward)), True)
        self.at = None


async def open_building():
    root = Path(os.environ['MESH_PROJECT_DIR'])
    app=omni.kit.app.get_app()
    for _ in range(6):await app.next_update_async()
    context=omni.usd.get_context()
    scene = Path(os.environ.get('MESH_SCENE_PATH', root/'reports/20261123_feinmesh/Gebaeude.usdz'))
    success, reason=await context.open_stage_async(str(scene))
    if not success:raise RuntimeError(reason)
    for _ in range(6):await app.next_update_async()
    stage=context.get_stage()
    stage.SetEditTarget(stage.GetSessionLayer())
    route_file=scene.with_name('Kameraposen.npz')
    if not route_file.exists():
        route_file=root/'reports/20261123_lyra_detail/Kameraposen.npz'
    with np.load(route_file) as route:
        poses=np.linalg.inv(route['w2c'])
        bookmarks=route['bookmarks'] if 'bookmarks' in route else (0,65,115)
        segment=route['segment'] if 'segment' in route else None
    global navigation
    navigation=MeshNavigation(get_active_viewport_window(),poses,bookmarks,segment)
    print('FOTOMESH_BEREIT',stage.GetRootLayer().identifier,flush=True)


asyncio.ensure_future(open_building())
