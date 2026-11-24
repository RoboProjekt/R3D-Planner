"""Compare identical, excluded camera poses in the original and reconstructed Isaac stages."""
import argparse
import json
from pathlib import Path

import cv2
import numpy as np
from PIL import Image,ImageDraw,ImageFont


def ssim(a,b):
    a=cv2.cvtColor(a,cv2.COLOR_RGB2GRAY).astype('f4')/255
    b=cv2.cvtColor(b,cv2.COLOR_RGB2GRAY).astype('f4')/255
    blur=lambda x:cv2.GaussianBlur(x,(11,11),1.5)
    ma,mb=blur(a),blur(b)
    va,vb=blur(a*a)-ma*ma,blur(b*b)-mb*mb
    return float(np.mean(((2*ma*mb+.01**2)*(2*(blur(a*b)-ma*mb)+.03**2))/
                         ((ma*ma+mb*mb+.01**2)*(va+vb+.03**2))))


def compare(route,runtime,photos):
    scores=json.loads((runtime/'results/evaluation.json').read_text())
    calib=np.load(route/'Kameraposen.npz')
    rows=[]
    for record in scores['tests']:
        i=record['view'];fid=record['source'];assert calib['source_frame_id'][i]==fid
        truth=np.asarray(Image.open(photos/f'{fid:04d}.jpg').convert('RGB'))
        info={'index':i,'source_id':fid}
        for method in ('baseline','spark_render'):
            image=np.asarray(Image.open(runtime/method/f'{i:03d}.png').convert('RGB'))
            info[method]={'psnr_db':float(cv2.PSNR(truth,image)),'ssim':ssim(truth,image)}
        rows.append(info)
    summary={name:{metric:float(np.mean([row[name][metric] for row in rows]))
        for metric in ('psnr_db','ssim')} for name in ('baseline','spark_render')}
    report={'input_views':scores['input'],'reconstruction_views':scores['training'],'held_out_views':len(rows),
            'splats':scores['splats'],'isaac_comparison':summary,'individual':rows,
            'renderers':{'baseline':'Original desktop stage, Isaac Sim 5.1.0',
                         'spark_render':'Native ParticleField, Isaac Sim 6.1.0'},
            'physics':json.loads((runtime/'spark_render/isaac.json').read_text())}
    (route/'Pruefung.json').write_text(json.dumps(report,indent=2)+'\n')
    columns=['Kamerabild','Bisherige Isaac-Szene','Lyra in Isaac Sim']
    width,height,gap,padding=416,312,12,18
    canvas=Image.new('RGB',(2*padding+3*width+2*gap,65+3*height+2*gap+padding),(22,25,29))
    draw=ImageDraw.Draw(canvas)
    font=ImageFont.truetype('/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf',23)
    for j,title in enumerate(columns):draw.text((padding+j*(gap+width),18),title,font=font,fill='white')
    for row,i in enumerate((25,65,115)):
        fid=calib['source_frame_id'][i]
        paths=(photos/f'{fid:04d}.jpg',runtime/'baseline'/f'{i:03d}.png',runtime/'spark_render'/f'{i:03d}.png')
        for j,p in enumerate(paths):
            with Image.open(p) as im:
                canvas.paste(im.convert('RGB').resize((width,height),Image.Resampling.LANCZOS),
                             (padding+j*(width+gap),65+row*(height+gap)))
    canvas.save(route/'Vergleich.jpg',quality=93)
    print(json.dumps(summary),flush=True)


if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--route',type=Path,default=Path('reports/20261123_lyra_test'))
    p.add_argument('--runtime',type=Path,default=Path('.runtime/lyra'))
    p.add_argument('--photos',type=Path,default=Path('.runtime/isaac_building/photos'))
    a=p.parse_args();compare(a.route,a.runtime,a.photos)
