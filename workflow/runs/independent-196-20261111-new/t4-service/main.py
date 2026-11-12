#!/usr/bin/env python3
"""图像真伪鉴定榜 SUT 服务（真实推理，非 mock）。

接口与官方 starting-kit 保持同构：
  GET  /ready                     -> 模型加载完成后返回 200 "True"
  POST /api/v1/image-authenticity -> {image_base64, image_format} => {success, message, result}

平台约束（来自 T1 spec S1/S5/S6/S7）：
  - 监听 0.0.0.0:80；readiness probe 最长约 60 分钟；
  - 每个测试样本最终必须返回合法标签（result ∈ {"1","0_1","0_2"}），否则整次评测无效；
  - 因此任何解码/推理异常都走兜底：返回先验最高的合法标签（success=true），并在日志记录。
"""
import base64
import io
import json
import logging
import os
import sys
import threading

import torch
from flask import Flask, Response, request
from PIL import Image
from torchvision import transforms
from torchvision.models import resnet18

logging.basicConfig(stream=sys.stdout, level=logging.INFO,
                    format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("sut")

MODEL_PATH = os.getenv("MODEL_PATH", "/app/model/best.pt")
CLASS_TO_IDX = {"1": 0, "0_1": 1, "0_2": 2}
IDX_TO_LABEL = {v: k for k, v in CLASS_TO_IDX.items()}
IMG_SIZE = 224
MEAN = (0.485, 0.456, 0.406)
STD = (0.229, 0.224, 0.225)

# 训练集先验（各 400 张，均匀）；兜底标签取 0 号类 "1"（原生实拍在训练集中最常见之一且为先验最高并列时取字典序稳定值）
FALLBACK_LABEL = "1"

app = Flask(__name__)
state = {"model": None, "ready": False, "lock": threading.Lock()}

preprocess = transforms.Compose([
    transforms.Resize(int(IMG_SIZE * 256 / 224)),
    transforms.CenterCrop(IMG_SIZE),
    transforms.ToTensor(),
    transforms.Normalize(MEAN, STD),
])


def _load_model():
    device = "cuda" if torch.cuda.is_available() else "cpu"
    log.info("loading model from %s on %s", MODEL_PATH, device)
    ckpt = torch.load(MODEL_PATH, map_location="cpu", weights_only=False)
    model = resnet18()
    model.fc = torch.nn.Linear(512, 3)
    model.load_state_dict(ckpt["model"])
    model.eval()
    model.to(device)
    state["device"] = device
    state["model"] = model
    state["ready"] = True
    log.info("model loaded, params=%d", sum(p.numel() for p in model.parameters()))


@app.route("/ready", methods=["GET"])
def ready():
    if state["ready"]:
        return "True", 200
    return "loading", 503


@app.route("/api/v1/image-authenticity", methods=["POST"])
def inference_endpoint():
    if not state["ready"]:
        return _resp(False, "模型尚未就绪", None, 503)
    try:
        req_data = request.get_json(force=True, silent=True)
        if req_data is None:
            return _resp(False, "请求体不是有效的 JSON", None, 400)
        image_base64 = req_data.get("image_base64", "")
        if not image_base64:
            return _resp(False, "缺少必要参数: image_base64", None, 400)
        if image_base64.startswith("data:"):
            image_base64 = image_base64.split(",", 1)[1]
        image_bytes = base64.b64decode(image_base64, validate=False)
        if not image_bytes:
            return _resp(False, "图片内容为空", None, 400)

        with Image.open(io.BytesIO(image_bytes)) as im:
            im = im.convert("RGB")
            tensor = preprocess(im).unsqueeze(0)

        model = state["model"]
        with torch.no_grad():
            tensor = tensor.to(state["device"])
            logits = model(tensor)
            idx = int(logits.argmax(1).item())
        label = IDX_TO_LABEL[idx]
        conf = float(torch.softmax(logits, 1).max().item())
        return _resp(True, "鉴定完成", label, 200, extra={"confidence": round(conf, 4)})
    except Exception:
        log.exception("inference error; falling back to prior label %s", FALLBACK_LABEL)
        return _resp(True, "鉴定完成(兜底)", FALLBACK_LABEL, 200)


def _resp(success, message, result, code, extra=None):
    payload = {"success": success, "message": message}
    if result is not None:
        payload["result"] = result
    if extra:
        payload.update(extra)
    return Response(json.dumps(payload, ensure_ascii=False),
                    status=code, mimetype="application/json; charset=utf-8")


if __name__ == "__main__":
    port = int(os.getenv("PORT", "80"))
    threading.Thread(target=_load_model, daemon=False).start()
    log.info("starting server on 0.0.0.0:%d", port)
    app.run(host="0.0.0.0", port=port, debug=False, threaded=True)
