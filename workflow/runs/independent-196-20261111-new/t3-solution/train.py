#!/usr/bin/env python3
"""T3: ResNet-18 三分类微调（CPU）。数据来自已核验的本地缓存。"""
import json
import random
import sys
import time
from collections import Counter
from pathlib import Path

import numpy as np
import torch
import torch.nn as nn
from PIL import Image, UnidentifiedImageError
from torch.utils.data import Dataset
from torchvision import transforms
from torchvision.models import ResNet18_Weights, resnet18

DATA_ROOT = Path("/mnt/disk3/liuyutong_home/workspace/darwin_auto/datasets/image_auth")
CLASS_DIRS = {
    "1": DATA_ROOT / "train_1_0_1" / "1",
    "0_1": DATA_ROOT / "train_1_0_1" / "0_1",
    "0_2": DATA_ROOT / "train_0_2" / "训练集 0_2" / "0_2",
}
EXTS = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tif", ".tiff"}
SEED = 196
VAL_FRAC = 0.25
EPOCHS = int(sys.argv[1]) if len(sys.argv) > 1 else 12
BATCH = 32
IMG_SIZE = 224
OUT_DIR = Path(__file__).parent / "model"

MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)


def collect_files():
    files = {cls: [] for cls in CLASS_DIRS}
    for cls, root in CLASS_DIRS.items():
        for p in root.rglob("*"):
            if p.is_file() and p.suffix.lower() in EXTS and "__MACOSX" not in str(p):
                files[cls].append(p)
    for cls in files:
        random.shuffle(files[cls])
    return files


class ImgDataset(Dataset):
    def __init__(self, items, tfm):
        self.items = items  # (path, class_idx)
        self.tfm = tfm

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        path, cls = self.items[idx]
        try:
            with Image.open(path) as im:
                im = im.convert("RGB")
                img = self.tfm(im)
        except (UnidentifiedImageError, OSError, ValueError) as e:
            print(f"[skip] unreadable {path}: {e}", file=sys.stderr)
            img = torch.zeros(3, IMG_SIZE, IMG_SIZE)
        return img, cls


def main():
    random.seed(SEED)
    np.random.seed(SEED)
    CLASS_TO_IDX = {"1": 0, "0_1": 1, "0_2": 2}
    torch.manual_seed(SEED)
    torch.set_num_threads(16)

    train_tfm = transforms.Compose([
        transforms.RandomResizedCrop(IMG_SIZE, scale=(0.7, 1.0)),
        transforms.RandomHorizontalFlip(),
        transforms.ColorJitter(0.2, 0.2, 0.2, 0.05),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])
    val_tfm = transforms.Compose([
        transforms.Resize(int(IMG_SIZE * 256 / 224)),
        transforms.CenterCrop(IMG_SIZE),
        transforms.ToTensor(),
        transforms.Normalize(MEAN, STD),
    ])

    files = collect_files()
    all_items = []
    for cls, paths in files.items():
        all_items.extend((p, cls) for p in paths)
    print(f"[data] total={len(all_items)} per_class={ {k: len(v) for k, v in files.items()} }", flush=True)

    train_items, val_items = [], []
    for cls, paths in files.items():
        idx = CLASS_TO_IDX[cls]
        n_val = int(len(paths) * VAL_FRAC)
        val_items.extend((p, idx) for p in paths[:n_val])
        train_items.extend((p, idx) for p in paths[n_val:])
    random.shuffle(train_items)
    random.shuffle(val_items)
    print(f"[split] train={len(train_items)} val={len(val_items)}", flush=True)

    train_ds = ImgDataset(train_items, train_tfm)
    val_ds = ImgDataset(val_items, val_tfm)

    model = resnet18(weights=ResNet18_Weights.IMAGENET1K_V1)
    model.fc = nn.Linear(512, 3)
    backbone = [p for n, p in model.named_parameters() if not n.startswith("fc.")]
    head = [p for n, p in model.named_parameters() if n.startswith("fc.")]
    opt = torch.optim.AdamW([{"params": backbone, "lr": 1e-4}, {"params": head, "lr": 1e-3}], weight_decay=1e-4)
    crit = nn.CrossEntropyLoss()

    train_loader = torch.utils.data.DataLoader(train_ds, batch_size=BATCH, shuffle=True, num_workers=4, drop_last=False)
    val_loader = torch.utils.data.DataLoader(val_ds, batch_size=BATCH, shuffle=False, num_workers=4)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    (OUT_DIR / "class_map.json").write_text(json.dumps({"1": 0, "0_1": 1, "0_2": 2}, indent=2))

    best = {"f1_0": -1.0, "epoch": -1, "metrics": {}}
    t0 = time.time()
    for epoch in range(1, EPOCHS + 1):
        model.train()
        run_loss, run_n = 0.0, 0
        for xb, yb in train_loader:
            opt.zero_grad()
            logits = model(xb)
            loss = crit(logits, yb)
            loss.backward()
            opt.step()
            run_loss += loss.item() * len(yb)
            run_n += len(yb)
        vpred, vtrue = [], []
        model.eval()
        with torch.no_grad():
            for xb, yb in val_loader:
                vpred.extend(model(xb).argmax(1).tolist())
                vtrue.extend(yb.tolist())
        cm = confusion(vtrue, vpred)
        m = metrics_from_cm(cm)
        elapsed = time.time() - t0
        print(f"[epoch {epoch}/{EPOCHS}] loss={run_loss/run_n:.4f} acc={m['accuracy']:.4f} "
              f"f1_0={m['f1_0']:.4f} f1_1={m['f1_1']:.4f} f1_0_1={m['f1_0_1']:.4f} f1_0_2={m['f1_0_2']:.4f} "
              f"elapsed={elapsed/60:.1f}m", flush=True)
        if m["f1_0"] > best["f1_0"]:
            best = {"f1_0": m["f1_0"], "epoch": epoch, "metrics": m, "confusion": cm}
            torch.save({"model": model.state_dict(), "class_to_idx": {"1": 0, "0_1": 1, "0_2": 2},
                        "mean": MEAN, "std": STD, "img_size": IMG_SIZE, "val_metrics": m, "train_epoch": epoch},
                       OUT_DIR / "best.pt")
            print(f"[best] epoch {epoch} f1_0={m['f1_0']:.4f} saved", flush=True)
    (OUT_DIR / "best_summary.json").write_text(json.dumps(best, indent=2, ensure_ascii=False))
    print(f"[done] best={best['epoch']} f1_0={best['f1_0']:.4f} total={ (time.time()-t0)/60:.1f}m", flush=True)


def confusion(ytrue, ypred, k=3):
    cm = np.zeros((k, k), dtype=int)
    for t, p in zip(ytrue, ypred):
        cm[t][p] += 1
    return cm.tolist()


def metrics_from_cm(cm):
    cls = ["1", "0_1", "0_2"]
    out = {}
    for i, c in enumerate(cls):
        tp = cm[i][i]
        fp = sum(cm[j][i] for j in range(3)) - tp
        fn = sum(cm[i][j] for j in range(3)) - tp
        prec = tp / (tp + fp) if tp + fp else 0.0
        rec = tp / (tp + fn) if tp + fn else 0.0
        f1 = 2 * prec * rec / (prec + rec) if prec + rec else 0.0
        out[f"precision_{c}"] = prec
        out[f"recall_{c}"] = rec
        out[f"f1_{c}"] = f1
    total = sum(sum(r) for r in cm)
    out["accuracy"] = sum(cm[i][i] for i in range(3)) / total if total else 0.0
    out["f1_0"] = (out["f1_0_1"] + out["f1_0_2"]) / 2
    return out


if __name__ == "__main__":
    main()
