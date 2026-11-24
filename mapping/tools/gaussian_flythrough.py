"""Standalone GLFW flythrough of a calibrated RGB Gaussian scene."""
import math
from pathlib import Path

import glfw
import numpy as np
from OpenGL import GL


def has_gaussian_field(path):
    required = {b'f_dc_0', b'f_dc_1', b'f_dc_2', b'opacity', b'scale_0', b'scale_1', b'scale_2',
                b'rot_0', b'rot_1', b'rot_2', b'rot_3'}
    with path.open('rb') as stream:
        if stream.readline(256).strip() != b'ply':
            return False
        vertex = False
        for _ in range(512):
            words = stream.readline(1024).split()
            if not words or words == [b'end_header']:
                break
            if words[0] == b'element':
                vertex = words[1:2] == [b'vertex']
            elif vertex and words[0] == b'property':
                required.discard(words[-1])
    return not required


class Navigation:
    def __init__(self, cameras):
        self.poses = np.linalg.inv(cameras['w2c'])
        self.bookmarks = cameras['bookmarks']
        self.go(self.bookmarks[0])

    def go(self, index):
        self.index = int(np.clip(index, 0, len(self.poses)-1))
        self.pose = self.poses[self.index].copy()

    def turn(self, yaw, pitch):
        forward = self.pose[:3, 2]
        az = math.atan2(forward[1], forward[0]) + yaw
        el = np.clip(math.atan2(forward[2], np.hypot(*forward[:2])) + pitch, -1.53, 1.53)
        right = np.array([math.sin(az), -math.cos(az), 0.])
        forward = np.array([math.cos(az)*math.cos(el), math.sin(az)*math.cos(el), math.sin(el)])
        self.pose[:3,:3] = np.column_stack([right, np.cross(forward, right), forward])
        self.index = None

    def move(self, forward, right, up, metres):
        delta = forward*self.pose[:3,2] + right*self.pose[:3,0] + np.array([0.,0.,up])
        self.pose[:3,3] += delta * (metres/max(1.,np.linalg.norm(delta)))
        self.index = None

    def step(self, increment):
        if self.index is None:
            self.index = np.linalg.norm(self.poses[:,:3,3]-self.pose[:3,3], axis=1).argmin()
        self.go(self.index+increment)


def make_rgb_renderer(path):
    from gsplat import rasterization
    from plyfile import PlyData
    import torch

    p = PlyData.read(str(path))['vertex']
    def gpu(a):
        return torch.as_tensor(np.ascontiguousarray(a), dtype=torch.float32, device='cuda')
    def cols(names):
        return gpu(np.column_stack([p[n] for n in names]))
    params = (cols('xyz'), cols([f'rot_{j}' for j in range(4)]), cols([f'scale_{j}' for j in range(3)]).exp(),
              gpu(p['opacity'].copy()).sigmoid(), cols([f'f_dc_{j}' for j in range(3)])*.28209479177387814+.5)

    @torch.inference_mode()
    def render(pose, k, width, height):
        rgb, alpha, _ = rasterization(*params, gpu(np.linalg.inv(pose)[None]), gpu(k[None]),
                                      width, height, near_plane=.08, far_plane=22.)
        return ((rgb[0]+.12*(1-alpha[0])).clamp(0,1)*255).round().byte().cpu().numpy()
    return render


def run(path):
    textured = path.suffix.lower()=='.glb'
    name = 'Fotomesh' if textured else 'Lyra'
    with np.load(path.with_name('Kameraposen.npz')) as c:
        nav = Navigation(c)
        base_k = c['intrinsics'][0]
        src_w, src_h = int(c['image_width']), int(c['image_height'])
    if not glfw.init():
        raise RuntimeError('GLFW konnte kein Fenster öffnen.')
    try:
        window = glfw.create_window(1024, 768, f'{name} Flythrough · Lade Welt …', None, None)
        if not window:
            raise RuntimeError('OpenGL-Fenster konnte nicht erstellt werden.')
        glfw.make_context_current(window)
        glfw.swap_interval(1)
        glfw.poll_events()
        if textured:
            from tools.flythrough_textured import TexturedBuilding
            mesh=TexturedBuilding(path)
        else:
            render = make_rgb_renderer(path)
        speed = 1.6
        last_cursor = None
        def on_key(win, key, scancode, action, mods):
            if action == glfw.RELEASE:
                return
            if key == glfw.KEY_ESCAPE:
                glfw.set_window_should_close(win, True)
            elif key in (glfw.KEY_F7, glfw.KEY_F8, glfw.KEY_F9):
                nav.go(nav.bookmarks[key-glfw.KEY_F7])
            elif key == glfw.KEY_R:
                nav.go(nav.bookmarks[0])
            elif key in (glfw.KEY_UP, glfw.KEY_DOWN):
                nav.step(1 if key==glfw.KEY_UP else -1)
        def on_button(win, button, action, mods):
            nonlocal last_cursor
            if button == glfw.MOUSE_BUTTON_LEFT:
                last_cursor = glfw.get_cursor_pos(win) if action == glfw.PRESS else None
        def on_cursor(win, x, y):
            nonlocal last_cursor
            if last_cursor is not None:
                nav.turn((last_cursor[0]-x)*.003, (last_cursor[1]-y)*.003)
                last_cursor = (x,y)
        def on_scroll(win, dx, dy):
            nonlocal speed
            speed = float(np.clip(speed*1.22**dy, .1, 12.))
        glfw.set_key_callback(window, on_key)
        glfw.set_mouse_button_callback(window, on_button)
        glfw.set_cursor_pos_callback(window, on_cursor)
        glfw.set_scroll_callback(window, on_scroll)
        def down(key):
            return glfw.get_key(window,key)==glfw.PRESS
        title = f'{name} Flythrough · WASD · Q/E Höhe · Maus links ziehen · F7 Treppe · F8 Podest · F9 Flur'
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 1)
        last_time = glfw.get_time()
        last_view = None
        while not glfw.window_should_close(window):
            now = glfw.get_time()
            dt = min(now-last_time,.12)
            last_time = now
            ahead = down(glfw.KEY_W)-down(glfw.KEY_S)
            side = down(glfw.KEY_D)-down(glfw.KEY_A)
            up = int(down(glfw.KEY_E) or down(glfw.KEY_SPACE)) - int(down(glfw.KEY_Q) or down(glfw.KEY_LEFT_CONTROL))
            turn = down(glfw.KEY_LEFT)-down(glfw.KEY_RIGHT)
            if turn:
                nav.turn(turn*1.5*dt,0)
            if ahead or side or up:
                nav.move(ahead,side,up,speed*dt*(3 if down(glfw.KEY_LEFT_SHIFT) else 1))
            w,h = glfw.get_framebuffer_size(window)
            view = (w,h,nav.pose.tobytes())
            if w>0 and h>0 and view!=last_view:
                scale = 1. if textured else min(1.,1280/w,960/h)
                rw,rh = max(1,round(w*scale)),max(1,round(h*scale))
                # Preserve the calibrated vertical field of view when the window changes shape.
                k = base_k.copy()
                k[:2] *= rh/src_h
                k[0,2] += (rw-src_w*rh/src_h)*.5
                if textured:
                    mesh.draw(nav.pose,k,rw,rh)
                else:
                    frame = render(nav.pose,k,rw,rh)
                    GL.glViewport(0,0,w,h)
                    GL.glWindowPos2i(0,h)
                    GL.glPixelZoom(w/rw,-h/rh)
                    GL.glDrawPixels(rw,rh,GL.GL_RGB,GL.GL_UNSIGNED_BYTE,frame)
                glfw.swap_buffers(window)
                if last_view is None:
                    glfw.set_window_title(window,title)
                    print(f'Flythrough bereit · {path.name} · {rw} × {rh}',flush=True)
                last_view = view
            glfw.wait_events_timeout(.008 if (ahead or side or up or turn) else .04)
    finally:
        glfw.terminate()
