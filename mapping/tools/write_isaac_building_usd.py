"""Author a self-contained, textured OpenUSD building with static PhysX collision."""
import argparse
from pathlib import Path
import tempfile
import numpy as np
from pxr import Gf,Sdf,Usd,UsdGeom,UsdLux,UsdPhysics,UsdShade,Vt


def shader(stage,path,node):
    s=UsdShade.Shader.Define(stage,path)
    s.CreateIdAttr(node)
    return s


def visual_material(stage,name,texture=None):
    path='/World/Materialien/'+name
    m=UsdShade.Material.Define(stage,path)
    surf=shader(stage,path+'/Surface','UsdPreviewSurface')
    surf.CreateInput('roughness',Sdf.ValueTypeNames.Float).Set(.95)
    surf.CreateInput('metallic',Sdf.ValueTypeNames.Float).Set(0.)
    surf.CreateInput('ior',Sdf.ValueTypeNames.Float).Set(1.35)
    if texture is None:
        surf.CreateInput('diffuseColor',Sdf.ValueTypeNames.Color3f).Set((.28,.27,.25))
    else:
        coords=shader(stage,path+'/UV','UsdPrimvarReader_float2')
        coords.CreateInput('varname',Sdf.ValueTypeNames.Token).Set('st')
        coords.CreateOutput('result',Sdf.ValueTypeNames.Float2)
        for slot,gain in [('diffuseColor',.65),('emissiveColor',.65)]:
            tex=shader(stage,path+'/'+slot,'UsdUVTexture')
            tex.CreateInput('file',Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+texture))
            tex.CreateInput('sourceColorSpace',Sdf.ValueTypeNames.Token).Set('sRGB')
            tex.CreateInput('wrapS',Sdf.ValueTypeNames.Token).Set('clamp')
            tex.CreateInput('wrapT',Sdf.ValueTypeNames.Token).Set('clamp')
            tex.CreateInput('scale',Sdf.ValueTypeNames.Float4).Set((gain,gain,gain,1.))
            tex.CreateInput('st',Sdf.ValueTypeNames.Float2).ConnectToSource(coords.ConnectableAPI(),'result')
            tex.CreateOutput('rgb',Sdf.ValueTypeNames.Float3)
            surf.CreateInput(slot,Sdf.ValueTypeNames.Color3f).ConnectToSource(tex.ConnectableAPI(),'rgb')
    surf.CreateOutput('surface',Sdf.ValueTypeNames.Token)
    m.CreateSurfaceOutput().ConnectToSource(surf.ConnectableAPI(),'surface')
    return m


def mesh_prim(stage,path,v,f):
    m=UsdGeom.Mesh.Define(stage,path)
    v=np.ascontiguousarray(v,dtype='f4'); f=np.ascontiguousarray(f,dtype='i4')
    m.CreatePointsAttr(Vt.Vec3fArray.FromNumpy(v))
    m.CreateExtentAttr(Vt.Vec3fArray.FromNumpy(np.stack((v.min(0),v.max(0)))))
    m.CreateFaceVertexCountsAttr(Vt.IntArray.FromNumpy(np.full(len(f),3,'i4')))
    m.CreateFaceVertexIndicesAttr(Vt.IntArray.FromNumpy(f.ravel()))
    m.CreateSubdivisionSchemeAttr('none')
    m.CreateDoubleSidedAttr(True)
    return m


def thick_collision(v,f,group):
    # Weld shared edges before generating the thin, closed wall and slab colliders.
    v,remap=np.unique(np.round(v,5),axis=0,return_inverse=True); f=remap[f]
    n=np.cross(v[f[:,1]]-v[f[:,0]],v[f[:,2]]-v[f[:,0]])
    good=np.linalg.norm(n,axis=1)>1.e-8;f,n=f[good],n[good]
    if group not in (0,1,3,4):return v,f
    thickness=np.zeros_like(v)
    if group==3:
        norm=np.zeros_like(v)
        for i in range(3):np.add.at(norm,f[:,i],n)
        thickness=-.027*norm/np.maximum(1.e-9,np.linalg.norm(norm,axis=1,keepdims=True))
    else: thickness[:,2]=.06 if group==4 else -.06
    edges=f[:,[0,1,1,2,2,0]].reshape(-1,2)
    _,idx,counts=np.unique(np.sort(edges,axis=1),axis=0,return_index=True,return_counts=True)
    a,b=edges[idx[counts==1]].T
    num=len(v)
    return np.vstack([v,v+thickness]),np.vstack([f,f[:,::-1]+num,np.c_[b,a,a+num],np.c_[b,a+num,b+num]])


def set_camera(stage,name,eye,forward):
    p='/World/Kameras/'+name
    c=UsdGeom.Camera.Define(stage,p)
    c.CreateClippingRangeAttr((.05,100.)); c.CreateFocalLengthAttr(19.)
    c.CreateHorizontalApertureAttr(24.);c.CreateVerticalApertureAttr(14.)
    eye=Gf.Vec3d(*eye);target=eye+Gf.Vec3d(*forward)
    mat=Gf.Matrix4d().SetLookAt(eye,target,Gf.Vec3d(0,0,1)).GetInverse()
    c.AddTransformOp().Set(mat)
    return p


def publish(prepared,destination):
    destination=destination.resolve()
    if destination.exists():raise FileExistsError(destination)
    with np.load(prepared/'scene.npz') as d:
        v,f,g,uv,atlas,textures,b,steps,stairs,route=[d[k] for k in (
            'v','f','g','uv','atlas','textures','b','steps','stair_bounds','trajectory')]
    stage_path=(prepared/'Gebaeude.usdc').resolve()
    stage=Usd.Stage.CreateNew(str(stage_path))
    world=UsdGeom.Xform.Define(stage,'/World'); stage.SetDefaultPrim(world.GetPrim())
    UsdGeom.SetStageMetersPerUnit(stage,1.);UsdGeom.SetStageUpAxis(stage,UsdGeom.Tokens.z)
    UsdPhysics.SetStageKilogramsPerUnit(stage,1.)
    UsdGeom.Xform.Define(stage,'/World/Gebaeude')
    UsdGeom.Scope.Define(stage,'/World/Materialien')
    for path in ['Sichtbar','Kollision']:UsdGeom.Scope.Define(stage,'/World/Gebaeude/'+path)
    names=['Boden_EG','Boden_1OG','Treppe','Waende','Decke_Flur_1OG','Einbauten']
    materials=[visual_material(stage,Path(t).stem,t) for t in textures]
    default=visual_material(stage,'Unbeobachtete_Einbauten')
    phys=UsdShade.Material.Define(stage,'/World/Materialien/Gebaeudekontakt')
    param=UsdPhysics.MaterialAPI.Apply(phys.GetPrim())
    param.CreateStaticFrictionAttr(.8);param.CreateDynamicFrictionAttr(.65);param.CreateRestitutionAttr(.0)
    for i,name in enumerate(names):
        sel=g==i
        for mat in np.unique(atlas[sel]):
            ids=np.flatnonzero(sel&(atlas==mat))
            used,ids_remap=np.unique(f[ids],return_inverse=True)
            m=mesh_prim(stage,f'/World/Gebaeude/Sichtbar/{name}/Teil_{mat+1:02d}',v[used],ids_remap.reshape(-1,3))
            UsdShade.MaterialBindingAPI.Apply(m.GetPrim()).Bind(materials[mat] if mat>=0 else default)
            if mat>=0:
                st=UsdGeom.PrimvarsAPI(m).CreatePrimvar('st',Sdf.ValueTypeNames.TexCoord2fArray,UsdGeom.Tokens.faceVarying)
                st.Set(Vt.Vec2fArray.FromNumpy(np.ascontiguousarray(uv[ids].reshape(-1,2))))
        used,remap=np.unique(f[sel],return_inverse=True)
        cv,cf=thick_collision(v[used],remap.reshape(-1,3),i)
        collider=mesh_prim(stage,'/World/Gebaeude/Kollision/'+name,cv,cf)
        collider.CreateVisibilityAttr('invisible')
        collider.CreatePurposeAttr('guide')
        UsdPhysics.CollisionAPI.Apply(collider.GetPrim()).CreateCollisionEnabledAttr(True)
        UsdPhysics.MeshCollisionAPI.Apply(collider.GetPrim()).CreateApproximationAttr('none')
        UsdShade.MaterialBindingAPI.Apply(collider.GetPrim()).Bind(phys,UsdShade.Tokens.weakerThanDescendants,'physics')
    physics=UsdPhysics.Scene.Define(stage,'/World/Physik')
    physics.CreateGravityDirectionAttr((0,0,-1));physics.CreateGravityMagnitudeAttr(9.81)
    dome=UsdLux.DomeLight.Define(stage,'/World/Licht/Umgebung'); dome.CreateIntensityAttr(300.)
    # Light the robot in the interior as well as the photo-textured static building.
    lightpts=[(x,-7.75,4.65) for x in np.arange(-3,33,6)]
    lightpts += [(-11.30,-13.,3.8),(-11.3,-17.7,2.65),(-7.8,-9.,1.85),(.2,-3.6,1.8)]
    for i,pt in enumerate(lightpts):
        lamp=UsdLux.SphereLight.Define(stage,f'/World/Licht/Innen_{i:02d}')
        lamp.AddTranslateOp().Set(Gf.Vec3d(*(np.asarray(pt)@b.T)))
        lamp.CreateRadiusAttr(.20);lamp.CreateIntensityAttr(1800.);lamp.CreateColorAttr((1.,.97,.92))
        lamp.GetPrim().CreateAttribute('primvars:doNotCastShadows',Sdf.ValueTypeNames.Bool).Set(True)
        lamp.GetPrim().CreateAttribute('inputs:enableColorTemperature',Sdf.ValueTypeNames.Bool).Set(False)
    # Frames are ground-contact markers. The robot's own base height is added at spawn.
    for name,pt in [('Start_EG',(0.,0.,-.55)),('Start_1OG',(4.,-7.80,float(steps[-1,1])))]:
        world_pos=np.array(pt)@b.T
        if name=='Start_EG':
            verts=v[np.unique(f[g==0])]
            world_pos[2]=verts[np.argmin(np.linalg.norm(verts[:,:2]-world_pos[:2],axis=1)),2]
        marker=UsdGeom.Xform.Define(stage,'/World/Startpunkte/'+name)
        marker.AddTranslateOp().Set(Gf.Vec3d(*world_pos))
        yaw=np.degrees(np.arctan2(b[1,0],b[0,0]))+(-90. if name=='Start_EG' else 0.)
        marker.AddRotateZOp().Set(float(yaw))
    eye=np.array([3.94,-8.11,3.49])@b.T
    forward=np.array([-.972,-.049,-.06])@b.T
    cam=set_camera(stage,'Flur_1OG',eye,forward)
    set_camera(stage,'Treppenaufgang',np.array([-11.37,-16.87,.47])@b.T,np.array([-.107,.958,.14])@b.T)
    stage.GetRootLayer().customLayerData={'cameraSettings':{'boundCamera':cam,
        'Perspective':{'position':Gf.Vec3d(*eye),'target':Gf.Vec3d(*(eye+5*forward))}}}
    stage.GetRootLayer().Save()
    destination.parent.mkdir(parents=True,exist_ok=True)
    with tempfile.TemporaryDirectory(dir=destination.parent) as temp:
        pack=Path(temp)/destination.name
        with Usd.ZipFileWriter.CreateNew(str(pack)) as writer:
            writer.AddFile(str(stage_path),stage_path.name)
            for name in textures:writer.AddFile(str((prepared/'textures'/name).resolve()),'textures/'+name)
        test=Usd.Stage.Open(str(pack))
        if not test or not test.GetDefaultPrim() or len([p for p in test.Traverse() if p.HasAPI(UsdPhysics.CollisionAPI)])!=len(names):
            raise ValueError('Stage failed collider validation')
        for prim in test.Traverse():
            if prim.IsA(UsdShade.Shader) and UsdShade.Shader(prim).GetIdAttr().Get()=='UsdUVTexture':
                asset=UsdShade.Shader(prim).GetInput('file').Get()
                if not asset.resolvedPath: raise ValueError(f'Unresolved texture {asset.path}')
        pack.rename(destination)
    wrapper_path=destination.with_name('Fahrszene.usda')
    if wrapper_path.exists():raise FileExistsError(wrapper_path)
    wrapper=Usd.Stage.CreateNew(str(wrapper_path))
    root=UsdGeom.Xform.Define(wrapper,'/World')
    root.GetPrim().GetReferences().AddReference('./'+destination.name,'/World')
    wrapper.SetDefaultPrim(root.GetPrim());UsdGeom.SetStageMetersPerUnit(wrapper,1.)
    UsdGeom.SetStageUpAxis(wrapper,UsdGeom.Tokens.z);UsdPhysics.SetStageKilogramsPerUnit(wrapper,1.)
    wrapper.GetRootLayer().customLayerData=stage.GetRootLayer().customLayerData
    wrapper.GetRootLayer().Save()
    print(destination,flush=True)

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('prepared',type=Path);p.add_argument('output',type=Path)
    a=p.parse_args();publish(a.prepared,a.output)
