"""Segment people in the mapping photographs without modifying the originals."""
import argparse
import hashlib
from pathlib import Path

import numpy as np
import torch
from PIL import Image
from torchvision.models.detection import maskrcnn_resnet50_fpn_v2
from torchvision.transforms.functional import pil_to_tensor


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('photos', type=Path)
    parser.add_argument('weights', type=Path)
    parser.add_argument('out', type=Path)
    args = parser.parse_args()
    if not hashlib.sha256(args.weights.read_bytes()).hexdigest().startswith('73cbd019'):
        raise ValueError('Unexpected TorchVision checkpoint')
    args.out.mkdir(parents=True, exist_ok=True)
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    torch.set_num_threads(5)
    model = maskrcnn_resnet50_fpn_v2(weights=None, weights_backbone=None, min_size=640, max_size=900)
    model.load_state_dict(torch.load(args.weights, map_location='cpu', weights_only=True))
    model.to(device).eval()
    photos = sorted(args.photos.glob('*.jpg'))
    counts = []
    with torch.inference_mode():
        for start in range(0, len(photos), 3):
            batch = photos[start:start + 3]
            imgs = [pil_to_tensor(Image.open(p).convert('RGB')).to(device).float()/255 for p in batch]
            for path, result in zip(batch, model(imgs)):
                keep = (result['labels'] == 1) & (result['scores'] >= .40)
                shape = imgs[0].shape[-2:]
                mask = torch.zeros(shape, dtype=torch.bool, device=device)
                for region in result['masks'][keep, 0]:
                    mask |= region > .27
                binary = mask.cpu().numpy().astype(np.uint8) * 255
                Image.fromarray(binary).save(args.out / (path.stem + '.png'))
                counts.append(int(mask.sum()))
            if start % 90 == 0:
                print(device, start, sum(n > 0 for n in counts), flush=True)
    print('Segmented', len(photos), 'frames, detections in', sum(n > 0 for n in counts), flush=True)


if __name__ == '__main__':
    main()
