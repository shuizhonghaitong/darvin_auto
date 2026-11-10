#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""最小三分类图像真伪推理（1 / 0_1 / 0_2），复用既有本地训练权重。

模型来源（均为既有本地文件，未复制、未训练、未下载）:
    权重: /mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/out/model_full.pt
    结构/标签/预处理的原始定义: 同目录 train.py（Net, CLASSES, to_tensor, SIZE=160）

本文件独立重写了 Net 结构（与 train.py 逐层对照），并用
--expect-keys 校验权重 state_dict 的键名与形状后 strict 加载；
标签映射 index 0->"1", 1->"0_1", 2->"0_2" 与 train.py/serve_model.py 的 CLASSES 一致。
预处理: PIL 打开 -> convert("RGB") -> resize(160x160, BILINEAR) -> /255 -> (x-0.5)/0.5 -> CHW float32。

用法:
    python predict.py IMG [IMG ...] [--weights PATH] [--json results/predictions.json]

无网络、无训练、无 HTTP 服务。任何异常打印到 stderr 并以非 0 退出，
不实现“出错时固定返回某类别”的兜底。
"""
import argparse
import json
import os
import sys
import time

import torch
import torch.nn as nn
from PIL import Image

CLASSES = ["1", "0_1", "0_2"]
SIZE = 160

# 与 train.py collect_images 的类根一致（仅用于记录“来自路径的标签”，不影响推理）
CLASS_ROOT_HINTS = [
    (os.path.join("train_1_0_1", "1"), "1"),
    (os.path.join("train_1_0_1", "0_1"), "0_1"),
    ("train_0_2", "0_2"),
]


def make_net():
    """与 image_auth_repo/model_train/train.py 的 Net 完全同构。"""
    net = nn.Sequential(
        nn.Conv2d(3, 32, 3, padding=1), nn.BatchNorm2d(32), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(32, 64, 3, padding=1), nn.BatchNorm2d(64), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(64, 128, 3, padding=1), nn.BatchNorm2d(128), nn.ReLU(), nn.MaxPool2d(2),
        nn.Conv2d(128, 256, 3, padding=1), nn.BatchNorm2d(256), nn.ReLU(), nn.MaxPool2d(2),
    )
    pool = nn.AdaptiveAvgPool2d(1)
    fc = nn.Linear(256, 3)

    class Model(nn.Module):
        def __init__(self):
            super().__init__()
            self.net = net
            self.pool = pool
            self.fc = fc

        def forward(self, x):
            x = self.net(x)
            x = self.pool(x).flatten(1)
            return self.fc(x)

    return Model()


# state_dict 键 -> 期望形状（独立核对，来自 Net 定义与 train_report.json 的 390147 参数）
EXPECTED_KEYS = {
    "net.0.weight": (32, 3, 3, 3), "net.0.bias": (32,),
    "net.1.weight": (32,), "net.1.bias": (32,), "net.1.running_mean": (32,), "net.1.running_var": (32,), "net.1.num_batches_tracked": (),
    "net.4.weight": (64, 32, 3, 3), "net.4.bias": (64,),
    "net.5.weight": (64,), "net.5.bias": (64,), "net.5.running_mean": (64,), "net.5.running_var": (64,), "net.5.num_batches_tracked": (),
    "net.8.weight": (128, 64, 3, 3), "net.8.bias": (128,),
    "net.9.weight": (128,), "net.9.bias": (128,), "net.9.running_mean": (128,), "net.9.running_var": (128,), "net.9.num_batches_tracked": (),
    "net.12.weight": (256, 128, 3, 3), "net.12.bias": (256,),
    "net.13.weight": (256,), "net.13.bias": (256,), "net.13.running_mean": (256,), "net.13.running_var": (256,), "net.13.num_batches_tracked": (),
    "fc.weight": (3, 256), "fc.bias": (3,),
}


def load_model(weights_path):
    model = make_net()
    state = torch.load(weights_path, map_location="cpu")
    missing = set(EXPECTED_KEYS) - set(state)
    extra = set(state) - set(EXPECTED_KEYS)
    if missing or extra:
        raise RuntimeError("state_dict 键不一致: missing=%s extra=%s" % (sorted(missing), sorted(extra)))
    for k, shape in EXPECTED_KEYS.items():
        if tuple(state[k].shape) != shape:
            raise RuntimeError("形状不一致: %s 期望 %s 实际 %s" % (k, shape, tuple(state[k].shape)))
    model.load_state_dict(state, strict=True)
    model.eval()
    return model


def preprocess(path):
    img = Image.open(path)
    img.load()
    img = img.convert("RGB").resize((SIZE, SIZE), Image.BILINEAR)
    import numpy as np
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - 0.5) / 0.5
    return torch.from_numpy(arr).permute(2, 0, 1).contiguous()


def label_from_path(path):
    norm = path.replace(os.sep, "/")
    for hint, cls in CLASS_ROOT_HINTS:
        if ("/" + hint + "/") in norm and "__MACOSX" not in norm:
            return cls
    return None


def predict_image(model, path, device="cpu"):
    t = preprocess(path).unsqueeze(0).to(device)
    with torch.no_grad():
        logits = model(t).cpu().numpy()[0]
    probs = torch.softmax(torch.tensor(logits), dim=0).numpy()
    idx = int(logits.argmax())
    return {
        "input": path,
        "label_from_path": label_from_path(path),
        "prediction": CLASSES[idx],
        "logits": [float(v) for v in logits],
        "probs": [float(v) for v in probs],
    }


def main():
    ap = argparse.ArgumentParser(description="三分类图像真伪推理（复用既有本地权重）")
    ap.add_argument("images", nargs="*")
    ap.add_argument("--weights", default="/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/out/model_full.pt")
    ap.add_argument("--samples", default=None, help="文本文件，每行一个图像路径（保留空格）")
    ap.add_argument("--json", dest="json_out", default=None, help="将逐图结果写入 JSON 文件")
    args = ap.parse_args()

    paths = list(args.images or [])
    if args.samples:
        with open(args.samples) as f:
            paths.extend(line.strip() for line in f if line.strip())
    if not paths:
        ap.error("需要 images 或 --samples")

    model = load_model(args.weights)
    t0 = time.time()
    results = [predict_image(model, p) for p in paths]
    load_ms = (time.time() - t0) * 1000

    out = {
        "weights": args.weights,
        "classes": CLASSES,
        "size": SIZE,
        "inference_ms": round(load_ms, 1),
        "n": len(results),
        "correct_vs_path_label": sum(1 for r in results if r["label_from_path"] and r["prediction"] == r["label_from_path"]),
        "items": results,
    }
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.json_out:
        with open(args.json_out, "w") as f:
            f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
