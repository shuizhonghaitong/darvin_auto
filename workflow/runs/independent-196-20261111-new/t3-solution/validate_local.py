#!/usr/bin/env python3
"""T3 本地验证：模拟服务全链路（base64 解码→PIL→预处理→CPU 推理→argmax）。"""
import base64, io, json, random, time, sys
from pathlib import Path
import torch
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet18

random.seed(7)
MEAN=(0.485,0.456,0.406); STD=(0.229,0.224,0.225); SZ=224
tfm = transforms.Compose([transforms.resize if False else transforms.Resize(int(SZ*256/224)),
                          transforms.CenterCrop(SZ), transforms.ToTensor(), transforms.Normalize(MEAN,STD)])
IDX={0:"1",1:"0_1",2:"0_2"}
m = resnet18(); m.fc=torch.nn.Linear(512,3)
ck = torch.load("model/best.pt", map_location="cpu", weights_only=False)
m.load_state_dict(ck["model"]); m.eval()

roots = {"1": Path("/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/train_1_0_1/1"),
         "0_1": Path("/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/train_1_0_1/0_1"),
         "0_2": Path("/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth/train_0_2/训练集 0_2/0_2")}
samples=[]
for cls, r in roots.items():
    ps=[p for p in r.rglob("*") if p.is_file() and p.suffix.lower() in {".jpg",".png",".tiff"}]
    samples += random.sample(ps, 10)

t0=time.time(); first=None
correct=0; per_cls={}
for p in samples:
    ts=time.time()
    b64=base64.b64encode(p.read_bytes()).decode()
    raw=base64.b64decode(b64)
    with Image.open(io.BytesIO(raw)) as im:
        im=im.convert("RGB"); x=tfm(im).unsqueeze(0)
    with torch.no_grad():
        pred=int(m(x).argmax(1).item())
    dt=(time.time()-ts)*1000
    if first is None: first=dt
    true=p.name and {str(k):k for k in roots}.get(None) or None
    cls_true = [c for c,r in roots.items() if r in p.parents][0]
    ok = (IDX[pred]==cls_true)
    correct += ok
    per_cls.setdefault(cls_true, [0,0]); per_cls[cls_true][0]+=ok; per_cls[cls_true][1]+=1
wall=(time.time()-t0)/len(samples)*1000
print(json.dumps({"n":len(samples),"correct":correct,"acc":round(correct/len(samples),4),
                  "per_class_acc":{k:[v[0],v[1]] for k,v in per_cls.items()},
                  "avg_ms_per_image":round(wall,1),"first_ms":round(first,1)}, indent=1))
# 异常路径测试
for name, payload in [("truncated", "aGVsbG8="), ("empty",""), ("notimage", base64.b64encode(b"hello world").decode())]:
    try:
        raw=base64.b64decode(payload, validate=False)
        with Image.open(io.BytesIO(raw)) as im: im.verify()
        print(name, "-> decoded OK (unexpected)")
    except Exception as e:
        print(name, "-> decode fails as expected:", type(e).__name__)
