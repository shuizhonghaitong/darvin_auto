"""TICKET-2 independent target-environment feasibility check (CPU 2-core, minimal).

Checks:
 1. Real weight load of dinov2-base safetensors (missing/unexpected keys evidence)
 2. Three-class head adaptation with explicit label mapping
 3. 3-dim output shape + softmax sanity
 4. One classification-head backward pass + parameter change
 5. Per-stage wall time under 2-core pinning (peak RSS from /usr/bin/time -v wrapper)

Synthetic pixel input ONLY: proves technical shape and gradient flow, NOT model quality.
"""
import json, os, sys, time

os.environ.setdefault("OMP_NUM_THREADS", "2")
os.environ.setdefault("MKL_NUM_THREADS", "2")
os.environ.setdefault("OPENBLAS_NUM_THREADS", "2")
os.environ.setdefault("OMP_DYNAMIC", "FALSE")

import torch
torch.manual_seed(0)
torch.set_num_threads(2)

WEIGHTS = "/mnt/disk3/liuyutong_home/workspace/darvin_auto/workflow/runs/t2-adaptable-20261108/independent-isolated-20261109/dinov2-base-f9e44-model.safetensors"
LABELS = ["1", "0_1", "0_2"]  # order per competition_spec output.label_space

out = {"torch_threads": torch.get_num_threads(), "torch_version": torch.__version__}

t0 = time.time()
from safetensors.torch import load_file
sd = load_file(WEIGHTS)
out["stage_load_file_s"] = round(time.time() - t0, 3)
out["num_tensors"] = len(sd)

# --- architecture derived from the weights themselves ---
hidden = int(sd["embeddings.cls_token"].shape[-1])
pos_shape = list(sd["embeddings.position_embeddings"].shape)
n_patch = pos_shape[1] - 1
import math
side = int(round(math.isqrt(n_patch)))
assert side * side == n_patch, f"pos grid not square: {n_patch}"
native_res = side * 14
proj = list(sd["embeddings.patch_embeddings.projection.weight"].shape)
mlp_h = int(sd["encoder.layer.0.mlp.fc1.weight"].shape[0])
layer_ids = sorted({int(k.split(".")[2]) for k in sd if k.startswith("encoder.layer")})
out["arch"] = {
    "hidden_size": hidden, "patch_size": proj[3], "num_hidden_layers": len(layer_ids),
    "intermediate_size": mlp_h, "native_position_grid": f"{side}x{side} ({native_res}px)",
    "total_params": int(sum(t.numel() for t in sd.values())),
}
w = sd["embeddings.patch_embeddings.projection.weight"].float()
out["weight_sanity"] = {"patch_proj_mean_abs": round(float(w.abs().mean()), 6),
                        "patch_proj_max_abs": round(float(w.abs().max()), 4),
                        "cls_token_norm": round(float(sd["embeddings.cls_token"].float().norm()), 4)}

# --- load into transformers Dinov2Model ---
from transformers import Dinov2Config, Dinov2Model
t0 = time.time()
# NOTE: checkpoint position embeddings are the native 518px grid (1370 tokens).
# transformers 4.57 derives num_position_embeddings from image_size, so we must
# set image_size=518 (canonical DINOv2 usage; model interpolates pos embeds for
# smaller inputs). A default 224 config causes a shape-mismatch load failure.
config = Dinov2Config(hidden_size=hidden, num_hidden_layers=len(layer_ids),
                      num_attention_heads=hidden // 64, intermediate_size=mlp_h,
                      image_size=native_res, patch_size=proj[3],
                      layer_scale_init=1.0, drop_path_rate=0.0)
out["config_num_position_embeddings"] = (native_res // proj[3] + 1) ** 2 + 1  # derived from image_size in transformers 4.57
model = Dinov2Model(config)
missing, unexpected = model.load_state_dict(sd, strict=False)
out["stage_model_init_load_s"] = round(time.time() - t0, 3)
out["load_report"] = {
    "missing_keys_count": len(missing),
    "unexpected_keys_count": len(unexpected),
    "missing_keys": missing,
    "unexpected_keys": unexpected,
}
param_bytes = sum(p.numel() * p.element_size() for p in model.parameters())
out["model_mem_params_bytes"] = int(param_bytes)

def cls_feat(pixel_values):
    with torch.set_grad_enabled(True):
        logits_hidden = model(pixel_values).last_hidden_state
    return logits_hidden[:, 0]

head = torch.nn.Linear(hidden, len(LABELS))
head_w_before = head.weight.detach().clone()

IMAGENET_MEAN = torch.tensor([0.485, 0.456, 0.406]).view(1, 3, 1, 1)
IMAGENET_STD = torch.tensor([0.229, 0.224, 0.225]).view(1, 3, 1, 1)

def to_pixels(img_uint8):  # (B,3,224,224) uint8 -> float tensor
    x = img_uint8.float() / 255.0
    return (x - IMAGENET_MEAN) / IMAGENET_STD

# synthetic batch: one random, one near-constant (documented: NOT real competition data)
rand_img = torch.randint(0, 256, (2, 3, 224, 224), dtype=torch.uint8)
rand_img[1] = torch.randint(100, 120, (1, 3, 224, 224), dtype=torch.uint8)
x = to_pixels(rand_img)

t0 = time.time()
feat = cls_feat(x)
logits = head(feat)
out["stage_forward_s"] = round(time.time() - t0, 3)
out["forward"] = {
    "feat_shape": list(feat.shape),
    "logits_shape": list(logits.shape),
    "softmax_sums": [round(float(s), 6) for s in torch.softmax(logits, -1).sum(-1).tolist()],
    "argmax_to_label": [LABELS[i] for i in logits.argmax(-1).tolist()],
}

targets = torch.tensor([0, 2])  # 1 -> '1', 2 -> '0_2'
loss = torch.nn.functional.cross_entropy(logits, targets)
loss.backward()
g_head_w = head.weight.grad
g_head_b = head.bias.grad
enc_grad_sample = model.layernorm.weight.grad
out["backward"] = {
    "loss": round(float(loss), 6),
    "head_weight_grad_finite": bool(torch.isfinite(g_head_w).all()),
    "head_weight_grad_norm": round(float(g_head_w.norm()), 6),
    "head_bias_grad_norm": round(float(g_head_b.norm()), 6),
    "encoder_grad_present": None if enc_grad_sample is None else round(float(enc_grad_sample.norm()), 6),
}

opt = torch.optim.SGD([head.weight, head.bias], lr=0.1)
t0 = time.time()
opt.step()
out["stage_optimizer_step_s"] = round(time.time() - t0, 3)
dw = (head.weight.detach() - head_w_before).abs()
out["param_change"] = {
    "head_weight_max_abs_delta": round(float(dw.max()), 8),
    "head_weight_changed": bool(dw.max() > 0),
    "head_bias_max_abs_delta": round(float((head.bias.detach()).abs().max()), 8),
}

# check both input resolutions (224 = typical serving, 518 = native)
res_ok = {}
for res in (224, 518):
    try:
        xr = torch.randint(0, 256, (1, 3, res, res), dtype=torch.uint8)
        f2 = cls_feat(to_pixels(xr))
        l2 = head(f2)
        res_ok[str(res)] = {"ok": True, "logits_shape": list(l2.shape)}
    except Exception as e:
        res_ok[str(res)] = {"ok": False, "error": f"{type(e).__name__}: {e}"[:300]}
out["resolution_check"] = res_ok

# inference latency: 10 single-image forwards (224px, CPU 2-core)
model.eval()
with torch.no_grad():
    x1 = x[:1]
    t0 = time.time()
    for _ in range(10):
        f1 = cls_feat(x1)
        l1 = head(f1)
    out["stage_infer10_avg_ms"] = round((time.time() - t0) * 100.0, 1)
out["head_labels"] = LABELS
out["label_index_map"] = {lab: i for i, lab in enumerate(LABELS)}

print(json.dumps(out, indent=1, ensure_ascii=False))
with open(os.path.join(os.path.dirname(__file__), "validation_summary.json"), "w") as f:
    json.dump(out, f, indent=1, ensure_ascii=False)
print("SCRIPT_EXIT_OK", file=sys.stderr)
