"""Publish the selected photo mesh, calibrated bookmarks and the recording's spawn references."""
import argparse
import json
from pathlib import Path
import shutil
import tempfile
import zipfile
import numpy as np
from pxr import Gf, Sdf, Usd, UsdGeom, UsdPhysics, UsdShade

DEST=Path('reports/20261124_fotomesh_hd');WORK=Path('.runtime/scan1123/photomesh_hd')
def publish(source):
    a=np.load('.runtime/scan1123/architecture/scene.npz');b=a['b'];steps=a['steps'];left,right,low=a['stair_bounds']
    route=np.load(DEST/'Kameraposen.npz');ids=route['bookmarks']
    pos=np.linalg.inv(route['w2c'])
    with tempfile.TemporaryDirectory(dir=WORK) as tmp:
        tmp=Path(tmp)
        with zipfile.ZipFile(source/'Gebaeude.usdz') as z:z.extractall(tmp)
        native=tmp/'Gebaeude.usdc';s=Usd.Stage.Open(str(native.resolve()));layer=s.GetRootLayer()
        for name,i in zip(('Treppe','Podest','Flur'),ids):
            path='/World/Kameras/Lyra_'+name
            p=s.GetPrimAtPath(path)
            if p:s.RemovePrim(path)
            cam=UsdGeom.Camera.Define(s,path);pose=pos[i];k=route['intrinsics'][i]
            cam.AddTransformOp().Set(Gf.Matrix4d((pose@np.diag([1.,-1.,-1.,1.])).T.tolist()))
            cam.CreateClippingRangeAttr((.05,100));cam.CreateFocalLengthAttr(20.)
            cam.CreateHorizontalApertureAttr(640*20/k[0,0]);cam.CreateVerticalApertureAttr(480*20/k[1,1])
            cam.CreateHorizontalApertureOffsetAttr((320-k[0,2])*20/k[0,0])
            cam.CreateVerticalApertureOffsetAttr((k[1,2]-240)*20/k[1,1])
            for key,val in {'exposure':0.,'exposure:fStop':1.,'exposure:iso':0.,'exposure:responsivity':1.,'exposure:time':1.}.items():
                cam.GetPrim().CreateAttribute(key,Sdf.ValueTypeNames.Float).Set(val)
        pose=pos[ids[0]];meta=layer.customLayerData
        meta['cameraSettings']={'boundCamera':'/World/Kameras/Lyra_Treppe','Perspective':{'position':Gf.Vec3d(*pose[:3,3]),'target':Gf.Vec3d(*(pose[:3,3]+2*pose[:3,2]))}}
        layer.customLayerData=meta
        for name,loc,heading in [('Start_EG',[(left+right)*.5,steps[0,0]-.54,low],b[:,1]),('Start_1OG',[2.,-7.75,steps[-1,1]],b[:,0])]:
            spawn=s.GetPrimAtPath('/World/Startpunkte/'+name)
            assert spawn.GetAttribute('xformOp:translate').Set(Gf.Vec3d(*(np.array(loc)@b.T)))
            assert spawn.GetAttribute('xformOp:rotateZ').Set(float(np.degrees(np.arctan2(heading[1],heading[0]))))
        layer.Save()
        package=tmp/'release.usdz'
        with Sdf.ZipFileWriter.CreateNew(str(package)) as z:
            z.AddFile(str(native.resolve()),native.name)
            for p in sorted((tmp/'textures').glob('*.jpg')):z.AddFile(str(p.resolve()),'textures/'+p.name)
        check=Usd.Stage.Open(str(package.resolve()))
        assert len([p for p in check.Traverse() if p.HasAPI(UsdPhysics.CollisionAPI)])==7
        textures=[UsdShade.Shader(p).GetInput('file').Get() for p in check.Traverse() if p.GetTypeName()=='Shader' and UsdShade.Shader(p).GetIdAttr().Get()=='UsdUVTexture']
        assert textures and all(a.resolvedPath for a in textures)
        package.replace(DEST/'Gebaeude.usdz')
    target=DEST/'Gebaeude.partial.glb';shutil.copyfile(source/'Gebaeude.glb',target);target.replace(DEST/'Gebaeude.glb')
    print('DELIVERED',source,len(textures),flush=True)
if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__);parser.add_argument('source',type=Path);publish(parser.parse_args().source)
