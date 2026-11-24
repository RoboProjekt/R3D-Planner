"""Draw the static, embedded photo-textured GLB exported by the building mapper."""
import ctypes
import json
import struct

import cv2
import numpy as np
from OpenGL import GL


class TexturedBuilding:
    def __init__(self,path):
        with path.open('rb') as stream:
            magic,version,_=struct.unpack('<4sII',stream.read(12))
            if magic!=b'glTF' or version!=2: raise ValueError('Expected a glTF 2 building')
            length,_=struct.unpack('<II',stream.read(8))
            doc=json.loads(stream.read(length))
            length,_=struct.unpack('<II',stream.read(8))
            blob=stream.read(length)
        def data(view):
            v=doc['bufferViews'][view];s=v.get('byteOffset',0)
            return memoryview(blob)[s:s+v['byteLength']]
        def acc(idx):
            a=doc['accessors'][idx]
            n={'VEC2':2,'VEC3':3,'SCALAR':1}[a['type']]
            dtype={5125:'<u4',5126:'<f4'}[a['componentType']]
            return np.frombuffer(data(a['bufferView']),dtype,count=a['count']*n,offset=a.get('byteOffset',0)).reshape(-1,n)
        def buffer(gltype,arr):
            arr=np.ascontiguousarray(arr);handle=GL.glGenBuffers(1)
            GL.glBindBuffer(gltype,handle);GL.glBufferData(gltype,arr.nbytes,arr,GL.GL_STATIC_DRAW)
            return handle
        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT,1)
        self.parts=[];textures={}
        for prim in doc['meshes'][0]['primitives']:
            at=prim['attributes'];q=acc(at['POSITION'])
            pos=buffer(GL.GL_ARRAY_BUFFER,np.column_stack([q[:,0],-q[:,2],q[:,1]]))
            indices=acc(prim['indices'])
            faces=buffer(GL.GL_ELEMENT_ARRAY_BUFFER,indices)
            if 'TEXCOORD_0' in at:
                uv=buffer(GL.GL_ARRAY_BUFFER,acc(at['TEXCOORD_0']))
                mat=doc['materials'][prim['material']]['pbrMetallicRoughness']
                idx=doc['textures'][mat['baseColorTexture']['index']]['source']
                if idx not in textures:
                    image=cv2.imdecode(np.frombuffer(data(doc['images'][idx]['bufferView']),'u1'),cv2.IMREAD_COLOR)
                    h,w=image.shape[:2];texture=GL.glGenTextures(1);GL.glBindTexture(GL.GL_TEXTURE_2D,texture)
                    GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_MIN_FILTER,GL.GL_LINEAR_MIPMAP_LINEAR)
                    GL.glTexParameteri(GL.GL_TEXTURE_2D,GL.GL_TEXTURE_MAG_FILTER,GL.GL_LINEAR)
                    GL.glTexImage2D(GL.GL_TEXTURE_2D,0,GL.GL_RGB8,w,h,0,GL.GL_BGR,GL.GL_UNSIGNED_BYTE,image)
                    GL.glGenerateMipmap(GL.GL_TEXTURE_2D); textures[idx]=texture
                self.parts.append((pos,faces,indices.size,uv,textures[idx]))
            else:
                linear=acc(at['COLOR_0'])
                srgb=np.where(linear<=.0031308,12.92*linear,1.055*linear**(1/2.4)-.055).astype('f4')
                self.parts.append((pos,faces,indices.size,buffer(GL.GL_ARRAY_BUFFER,srgb),None))
        GL.glEnable(GL.GL_DEPTH_TEST)
        GL.glClearColor(.137,.141,.153,1.)
        self.count=sum(part[2]//3 for part in self.parts)

    def draw(self,pose,k,w,h):
        GL.glViewport(0,0,w,h)
        GL.glClear(GL.GL_COLOR_BUFFER_BIT|GL.GL_DEPTH_BUFFER_BIT)
        near=.055
        GL.glMatrixMode(GL.GL_PROJECTION);GL.glLoadIdentity()
        GL.glFrustum(-near*k[0,2]/k[0,0],near*(w-k[0,2])/k[0,0],-near*(h-k[1,2])/k[1,1],near*k[1,2]/k[1,1],near,100.)
        GL.glMatrixMode(GL.GL_MODELVIEW)
        view=np.diag([1.,-1.,-1.,1.])@np.linalg.inv(pose)
        GL.glLoadMatrixd(np.ascontiguousarray(view.T))
        ptr=ctypes.c_void_p(0);GL.glEnableClientState(GL.GL_VERTEX_ARRAY)
        for pos,faces,n,attrib,texture in self.parts:
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER,pos);GL.glVertexPointer(3,GL.GL_FLOAT,0,ptr)
            GL.glBindBuffer(GL.GL_ARRAY_BUFFER,attrib)
            if texture is None:
                GL.glDisable(GL.GL_TEXTURE_2D);GL.glEnableClientState(GL.GL_COLOR_ARRAY);GL.glColorPointer(3,GL.GL_FLOAT,0,ptr)
            else:
                GL.glEnable(GL.GL_TEXTURE_2D);GL.glColor3f(1.,1.,1.);GL.glBindTexture(GL.GL_TEXTURE_2D,texture)
                GL.glEnableClientState(GL.GL_TEXTURE_COORD_ARRAY);GL.glTexCoordPointer(2,GL.GL_FLOAT,0,ptr)
            GL.glBindBuffer(GL.GL_ELEMENT_ARRAY_BUFFER,faces)
            GL.glDrawElements(GL.GL_TRIANGLES,n,GL.GL_UNSIGNED_INT,ptr)
            GL.glDisableClientState(GL.GL_TEXTURE_COORD_ARRAY);GL.glDisableClientState(GL.GL_COLOR_ARRAY)
