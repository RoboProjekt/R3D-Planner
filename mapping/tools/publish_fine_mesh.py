"""Publish the photo-textured building as a verified, portable Isaac USDZ and a glTF mesh."""
import argparse
import json
from pathlib import Path
import shutil
import struct
import tempfile

import numpy as np
from pxr import Sdf, Usd, UsdGeom, UsdPhysics, UsdShade, Vt

from write_isaac_building_usd import mesh_prim, shader, thick_collision


def linear(srgb):
    x = srgb.astype('f4') / 255
    return np.where(x <= .04045, x / 12.92, ((x + .055) / 1.055)**2.4)


ISAAC_EMISSION_SCALE = .00106


def material(stage, name, file=None):
    path = '/World/Materialien/' + name
    mat = UsdShade.Material.Define(stage, path)
    surf = shader(stage, path+'/Surface', 'UsdPreviewSurface')
    surf.CreateInput('diffuseColor', Sdf.ValueTypeNames.Color3f).Set((0., 0., 0.))
    surf.CreateInput('ior', Sdf.ValueTypeNames.Float).Set(1.)
    surf.CreateInput('roughness', Sdf.ValueTypeNames.Float).Set(1.)
    emit = surf.CreateInput('emissiveColor', Sdf.ValueTypeNames.Color3f)
    if file is None:
        src = shader(stage, path+'/Farbe', 'UsdPrimvarReader_float3')
        src.CreateInput('varname', Sdf.ValueTypeNames.Token).Set('displayColor')
        src.CreateOutput('result', Sdf.ValueTypeNames.Float3)
        emit.ConnectToSource(src.ConnectableAPI(), 'result')
    else:
        coord = shader(stage, path+'/UV', 'UsdPrimvarReader_float2')
        coord.CreateInput('varname', Sdf.ValueTypeNames.Token).Set('st')
        coord.CreateOutput('result', Sdf.ValueTypeNames.Float2)
        src = shader(stage, path+'/Foto', 'UsdUVTexture')
        src.CreateInput('file', Sdf.ValueTypeNames.Asset).Set(Sdf.AssetPath('textures/'+file))
        src.CreateInput('scale', Sdf.ValueTypeNames.Float4).Set((ISAAC_EMISSION_SCALE,)*3+(1.,))
        src.CreateInput('sourceColorSpace', Sdf.ValueTypeNames.Token).Set('sRGB')
        for key in ('wrapS','wrapT'):
            src.CreateInput(key, Sdf.ValueTypeNames.Token).Set('clamp')
        src.CreateInput('st', Sdf.ValueTypeNames.Float2).ConnectToSource(coord.ConnectableAPI(), 'result')
        src.CreateOutput('rgb', Sdf.ValueTypeNames.Float3)
        emit.ConnectToSource(src.ConnectableAPI(), 'rgb')
    surf.CreateOutput('surface', Sdf.ValueTypeNames.Token)
    mat.CreateSurfaceOutput().ConnectToSource(surf.ConnectableAPI(), 'surface')
    return mat


def group_faces(labels):
    order = labels.argsort(kind='stable')
    cuts = np.r_[0, np.flatnonzero(np.diff(labels[order]))+1, len(labels)]
    for a,b in zip(cuts,cuts[1:]):
        if a<b:
            yield int(labels[order[a]]), order[a:b]


def write_isaac(work, out, v, f, uv, atlas, colors, collision_geometry=None):
    if collision_geometry is None:
        src = Path('reports/20261123_lyra_detail/Treppe_Flur.usdc').resolve()
    else:
        src = Path(__file__).resolve().parents[1] / 'templates' / 'building.usda'
    layer = Sdf.Layer.OpenAsAnonymous(str(src))
    stage = Usd.Stage.Open(layer)
    if collision_geometry is None and not stage.RemovePrim('/World/Lyra'):
        raise ValueError('Missing source field')
    meta = layer.customLayerData
    meta['renderSettings'] = {k:v for k,v in meta['renderSettings'].items() if 'gaussian' not in k}
    layer.customLayerData = meta
    root = '/World/Gebaeude/Fotomesh'
    UsdGeom.Xform.Define(stage, root)
    textures = []
    for page, ids in group_faces(atlas):
        used,local = np.unique(f[ids], return_inverse=True)
        name = 'Punktfarben' if page < 0 else f'Atlas_{page:02d}'
        mesh = mesh_prim(stage, root+'/'+name, v[used], local.reshape(-1,3))
        if page < 0:
            mesh.CreateDisplayColorPrimvar(UsdGeom.Tokens.vertex).Set(Vt.Vec3fArray.FromNumpy(linear(colors[used])*ISAAC_EMISSION_SCALE))
            surface = material(stage, name)
        else:
            tex = f'detail_{page:02d}.jpg'
            textures.append(tex)
            st = UsdGeom.PrimvarsAPI(mesh).CreatePrimvar('st', Sdf.ValueTypeNames.TexCoord2fArray, UsdGeom.Tokens.faceVarying)
            st.Set(Vt.Vec2fArray.FromNumpy(np.ascontiguousarray(uv[ids].reshape(-1,2))))
            surface = material(stage, name, tex)
        UsdShade.MaterialBindingAPI.Apply(mesh.GetPrim()).Bind(surface)
    expected_colliders=6
    if collision_geometry is not None:
        collision_root='/World/Gebaeude/Kollision'
        stage.RemovePrim(collision_root)
        UsdGeom.Scope.Define(stage,collision_root)
        phys=UsdShade.Material.Get(stage,'/World/Materialien/Gebaeudekontakt')
        names=['Boden_EG','Boden_1OG','Treppe','Waende','Decke_Flur_1OG','Einbauten']
        with np.load(collision_geometry) as data:
            points,faces,groups=data['v'],data['f'],data['g']
            solid=bool(data['already_solid']) if 'already_solid' in data else False
        expected_colliders=0
        for group,name in enumerate(names):
            selected=faces[groups==group]
            if not len(selected):
                continue
            used,indices=np.unique(selected,return_inverse=True)
            vv,ff=(points[used],indices.reshape(-1,3)) if solid else thick_collision(points[used],indices.reshape(-1,3),group)
            collider=mesh_prim(stage,collision_root+'/'+name,vv,ff)
            collider.CreateVisibilityAttr('invisible')
            collider.CreatePurposeAttr('guide')
            UsdPhysics.CollisionAPI.Apply(collider.GetPrim()).CreateCollisionEnabledAttr(True)
            UsdPhysics.MeshCollisionAPI.Apply(collider.GetPrim()).CreateApproximationAttr('none')
            UsdShade.MaterialBindingAPI.Apply(collider.GetPrim()).Bind(phys,UsdShade.Tokens.weakerThanDescendants,'physics')
            expected_colliders+=1
    if (work/'rail.npz').exists():
        with np.load(work/'rail.npz') as rail:
            collider=mesh_prim(stage,'/World/Gebaeude/Kollision/Treppengelaender',rail['v'],rail['f'])
        collider.CreateVisibilityAttr('invisible')
        collider.CreatePurposeAttr('guide')
        UsdPhysics.CollisionAPI.Apply(collider.GetPrim()).CreateCollisionEnabledAttr(True)
        UsdPhysics.MeshCollisionAPI.Apply(collider.GetPrim()).CreateApproximationAttr('none')
        phys=UsdShade.Material.Get(stage,'/World/Materialien/Gebaeudekontakt')
        UsdShade.MaterialBindingAPI.Apply(collider.GetPrim()).Bind(phys,UsdShade.Tokens.weakerThanDescendants,'physics')
        expected_colliders+=1
    with tempfile.TemporaryDirectory(dir=work) as tmp:
        tmp = Path(tmp)
        stage_file = tmp/'Gebaeude.usdc'
        layer.Export(str(stage_file))
        package = tmp/'Gebaeude.usdz'
        writer_type = Sdf.ZipFileWriter if hasattr(Sdf, "ZipFileWriter") else Usd.ZipFileWriter
        with writer_type.CreateNew(str(package)) as writer:
            writer.AddFile(str(stage_file.resolve()), stage_file.name)
            for tex in textures:
                writer.AddFile(str((work/'textures'/tex).resolve()), 'textures/'+tex)
        check = Usd.Stage.Open(str(package.resolve()))
        collisions = [p for p in check.Traverse() if p.HasAPI(UsdPhysics.CollisionAPI)]
        polygons = sum(len(UsdGeom.Mesh(p).GetFaceVertexCountsAttr().Get()) for p in check.GetPrimAtPath(root).GetChildren())
        resolved = [UsdShade.Shader(p).GetInput('file').Get() for p in check.Traverse() if p.IsA(UsdShade.Shader) and UsdShade.Shader(p).GetIdAttr().Get()=='UsdUVTexture']
        if len(collisions)!=expected_colliders or polygons!=len(f) or len(resolved)!=len(textures) or any(not t.resolvedPath for t in resolved):
            raise ValueError('Package geometry, collisions or internal texture resolution failed')
        package.replace(out/'Gebaeude.usdz')
    print('USDZ', len(f), 'triangles,',len(textures),'resolved textures,',len(collisions),'colliders',flush=True)


def write_glb(work, out, v, f, uv, atlas, colors):
    # glTF is Y-up. Rotate the mesh, preserving the metric scale and handedness.
    pos = np.column_stack((v[:,0],v[:,2],-v[:,1])).astype('<f4')
    prims=[]; views=[]; acc=[]; images=[]; mats=[]; textures=[]
    with tempfile.TemporaryFile(dir=work) as blob:
        def buffer_view(data, target=None):
            blob.seek(0,2)
            blob.write(b'\x00'*(-blob.tell()%4))
            offset=blob.tell()
            blob.write(data)
            entry=dict(buffer=0, byteOffset=offset, byteLength=blob.tell()-offset)
            if target:entry['target']=target
            views.append(entry)
            return len(views)-1
        def accessor(array, dt, fmt, target, bounds=False):
            item=dict(bufferView=buffer_view(memoryview(np.ascontiguousarray(array)).cast('B'),target),
                      componentType=dt, count=len(array), type=fmt)
            if bounds:item.update(min=array.min(0).tolist(),max=array.max(0).tolist())
            acc.append(item)
            return len(acc)-1
        for page,ids in group_faces(atlas):
            indices=f[ids].ravel()
            param={'metallicFactor':0.,'roughnessFactor':1.}
            attributes={}
            if page>=0:
                st=uv[ids].reshape(-1,2).copy()
                st[:,1]=1-st[:,1]
                pairs=np.column_stack((indices.astype('u4'),st.view('u4')))
                _,which,local=np.unique(pairs.view('V12').ravel(),return_index=True,return_inverse=True)
                used=indices[which]
                attributes['TEXCOORD_0']=accessor(st[which],5126,'VEC2',34962)
                img=(work/'textures'/f'detail_{page:02d}.jpg').read_bytes()
                images.append(dict(mimeType='image/jpeg',bufferView=buffer_view(img)))
                textures.append(dict(source=len(images)-1))
                param['baseColorTexture']={'index':len(textures)-1}
            else:
                used,local=np.unique(indices,return_inverse=True)
                attributes['COLOR_0']=accessor(linear(colors[used]),5126,'VEC3',34962)
            attributes['POSITION']=accessor(pos[used],5126,'VEC3',34962,True)
            mats.append(dict(pbrMetallicRoughness=param,doubleSided=True,extensions={'KHR_materials_unlit':{}}))
            prims.append(dict(attributes=attributes,indices=accessor(local.astype('<u4').ravel(),5125,'SCALAR',34963),
                              mode=4,material=len(mats)-1))
        blob.write(b'\x00'*(-blob.tell()%4))
        n=blob.tell()
        doc=dict(asset={'version':'2.0','generator':'R3D'},extensionsUsed=['KHR_materials_unlit'],
                 scene=0,scenes=[{'nodes':[0]}],nodes=[{'name':'Gebaeude','mesh':0}],meshes=[{'primitives':prims}],
                 buffers=[{'byteLength':n}],bufferViews=views,accessors=acc,materials=mats,images=images,textures=textures)
        j=json.dumps(doc,separators=(',',':')).encode()
        j+=b' '*(-len(j)%4)
        dest=out/'Gebaeude.glb'
        with tempfile.NamedTemporaryFile(dir=out,delete=False) as g:
            tmp=Path(g.name)
            g.write(struct.pack('<4sII',b'glTF',2,28+len(j)+n))
            g.write(struct.pack('<I4s',len(j),b'JSON'));g.write(j)
            g.write(struct.pack('<I4s',n,b'BIN\0'));blob.seek(0);shutil.copyfileobj(blob,g)
        if tmp.stat().st_size!=28+len(j)+n:raise ValueError('glTF length mismatch')
        tmp.replace(dest);dest.chmod(0o644)
    print('glTF', len(prims), 'primitives',flush=True)


if __name__=='__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('work',type=Path)
    parser.add_argument('out',type=Path)
    parser.add_argument('--lidar-scans',type=Path,
                        help='Registered endpoint and trajectory NPZ from the same mapping run. Defaults to TSDF provenance.')
    parser.add_argument('--keep-floaters',action='store_true',help='Keep the original visual triangles for a comparison.')
    parser.add_argument('--collision-geometry',type=Path,help='Replace the reference colliders using this measured scene NPZ.')
    args=parser.parse_args()
    with np.load(args.work/'surface.npz') as surface:v,f=surface['v'],surface['f']
    with np.load(args.work/'materials.npz') as mat:
        uv,atlas=mat['uv'],mat['atlas']
        labels=mat['labels'] if 'labels' in mat else None
    colors=np.load(args.work/'fallback.npy')
    info=None
    if not args.keep_floaters and labels is None:
        if args.lidar_scans is not None:
            parser.error('Filtering requires the original per-face labels in materials.npz')
        info={'status':'skipped','reason':'legacy materials without structural labels'}
    if not args.keep_floaters and labels is not None:
        from filter_mesh_floaters import floater_mask
        scans=args.lidar_scans
        manifest=(args.work/'tsdf.json').resolve()
        if scans is None and manifest.exists():
            recorded=json.loads(manifest.read_text()).get('lidar_scans')
            if recorded:
                scans=manifest.parent/recorded
        keep,info=floater_mask(v,f,labels,args.work,scans)
        f,uv,atlas=f[keep],uv[keep],atlas[keep]
    args.out.mkdir(parents=True,exist_ok=True)
    write_isaac(args.work,args.out,v,f,uv,atlas,colors,args.collision_geometry)
    write_glb(args.work,args.out,v,f,uv,atlas,colors)
    if info is not None:
        print('Floater filter',json.dumps(info),flush=True)
