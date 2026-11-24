"""Rebake the calibrated stair and corridor charts using clean camera views."""
import numpy as np
import bake_building_photo_planes as planes
from clean_building_photos import ROOT,JOB


def capture(verts,faces,uv,atlas,colors):
    np.savez(JOB/'clean_surface.npz',v=verts,f=faces,uv=uv,atlas=atlas,colors=colors)
    return verts,faces,uv,atlas,colors,ROOT/'architecture/final_collision.npz'


if __name__=='__main__':
    planes.OUT=JOB/'planes'
    planes.BASE=JOB/'charts'
    planes._PHOTO_DIR=JOB/'photos'
    planes._MASK_DIR=JOB/'exclusion'
    planes.main(capture)
