#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""独立核对：证明预测输出来自模型权重与图像内容，而非固定类别。

检查项（全部只读引用既有本地文件）:
  V1 parity  : torch model_full.pt 与旧工程 starting-kit/model_weights.npz（numpy 推理）
               在同批图像上的 logit 差 < 1e-3 且 argmax 一致
               （复用 export_numpy.py 的导出-验证口径，独立重跑）
  V2 permute : 将 fc 权重/偏置按行 (0,1,2)->(1,0,2) 置换后重跑，
               期望预测类别按同一置换变化 —— 证明标签走 fc 行索引
  V3 checkpts: model_full.pt 与 model_valbest.pt 两 checkpoint 在同批图像上
               至少存在预测差异 —— 证明输出依赖具体权重文件

用法:
    python verify_model.py --images A B C ... [--json results/verify.json]
"""
import argparse
import copy
import json
import os
import sys

import torch

import predict as P

STARTING_KIT = "/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/starting-kit"
FULL_PT = "/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/out/model_full.pt"
VALBEST_PT = "/mnt/disk3/liuyutong_home/workspace/darwin_auto/image_auth_repo/model_train/out/model_valbest.pt"
NPZ = os.path.join(STARTING_KIT, "model_weights.npz")


def v1_parity(images):
    sys.path.insert(0, STARTING_KIT)
    from serve_model import ImageAuthModel  # noqa: E402
    torch_model = P.load_model(FULL_PT)
    np_model = ImageAuthModel(NPZ)
    rows, max_diff, mismatch = [], 0.0, 0
    for path in images:
        with torch.no_grad():
            tl = torch_model(P.preprocess(path).unsqueeze(0)).numpy()[0]
        with open(path, "rb") as f:
            nl = np_model.forward(np_model.preprocess(f.read()))
        d = float(abs(tl - nl).max())
        max_diff = max(max_diff, d)
        if int(tl.argmax()) != int(nl.argmax()):
            mismatch += 1
        rows.append({"input": path, "torch_logit_diff_max": d,
                     "torch_argmax": int(tl.argmax()), "numpy_argmax": int(nl.argmax())})
    return {"check": "V1_torch_numpy_parity",
            "max_logit_diff": max_diff, "argmax_mismatch": mismatch,
            "pass": max_diff < 1e-3 and mismatch == 0, "rows": rows}


def v2_permute(images):
    base = P.load_model(FULL_PT)
    state = base.state_dict()
    perm = torch.tensor([1, 0, 2])
    pmodel = copy.deepcopy(base)
    pmodel.fc.weight.data = pmodel.fc.weight.data[perm].clone()
    pmodel.fc.bias.data = pmodel.fc.bias.data[perm].clone()
    pmodel.eval()
    rows, consistent = [], True
    for path in images:
        with torch.no_grad():
            lb = base(P.preprocess(path).unsqueeze(0)).argmax().item()
            lp = pmodel(P.preprocess(path).unsqueeze(0)).argmax().item()
        # 行置换 (0,1,2)->(1,0,2) 后，原 argmax=i 应变为 argmax=perm[i]
        ok = (lp == perm[lb].item())
        consistent &= ok
        rows.append({"input": os.path.basename(path), "orig_index": lb, "permuted_index": lp, "as_expected": ok})
    return {"check": "V2_fc_row_permutation", "permutation": [1, 0, 2],
            "all_as_expected": consistent, "pass": consistent, "rows": rows}


def v3_checkpoints(images):
    m1 = P.load_model(FULL_PT)
    m2 = P.load_model(VALBEST_PT)
    rows, diff = [], 0
    for path in images:
        with torch.no_grad():
            a = m1(P.preprocess(path).unsqueeze(0)).argmax().item()
            b = m2(P.preprocess(path).unsqueeze(0)).argmax().item()
        if a != b:
            diff += 1
        rows.append({"input": os.path.basename(path), "model_full": a, "model_valbest": b, "same": a == b})
    return {"check": "V3_checkpoint_sensitivity", "n_differing": diff,
            "pass": diff > 0, "rows": rows}


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--images", nargs="*")
    ap.add_argument("--samples", default=None, help="文本文件，每行一个图像路径（保留空格）")
    ap.add_argument("--json", dest="json_out", default=None)
    args = ap.parse_args()
    images = list(args.images or [])
    if args.samples:
        with open(args.samples) as f:
            images.extend(line.strip() for line in f if line.strip())
    if not images:
        ap.error("需要 --images 或 --samples")
    results = [
        v1_parity(images),
        v2_permute(images),
        v3_checkpoints(images),
    ]
    out = {"results": results, "all_pass": all(r["pass"] for r in results)}
    text = json.dumps(out, ensure_ascii=False, indent=2)
    if args.json_out:
        with open(args.json_out, "w") as f:
            f.write(text + "\n")
    print(text)


if __name__ == "__main__":
    main()
