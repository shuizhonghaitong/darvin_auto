#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""numpy 推理模块：图像真伪三分类（1 / 0_1 / 0_2）。

模型为 CPU 训练的小型 CNN（torch 训练，权重导出为 numpy），
推理仅依赖 numpy + Pillow，保证服务镜像轻量、响应稳定。

网络结构（与 model_train/train.py 的 Net 一一对应）:
    input 160x160x3, 归一化 (x-0.5)/0.5
    block x4: Conv3x3(pad=1) + BatchNorm(eval) + ReLU + MaxPool2
    通道 3 -> 32 -> 64 -> 128 -> 256
    GlobalAvgPool -> Linear(256, 3)
"""
import io
import os

import numpy as np
from PIL import Image

CLASSES = ["1", "0_1", "0_2"]
SIZE = 160
BN_EPS = 1e-5

CHANNELS = [3, 32, 64, 128, 256]


def _conv3x3(x, weight, bias):
    """x: [C, H, W] float32; weight: [O, C, 3, 3]; bias: [O] -> [O, H, W]"""
    c, h, w = x.shape
    o = weight.shape[0]
    x = np.pad(x, ((0, 0), (1, 1), (1, 1)), mode="constant")
    h += 2
    w += 2
    patches = np.lib.stride_tricks.sliding_window_view(x, (3, 3), axis=(1, 2))
    # patches: [C, H-2, W-2, 3, 3] -> [C, H-2, W-2, 9]
    patches = patches.reshape(c, h - 2, w - 2, 9)
    patches = patches.transpose(1, 2, 0, 3).reshape(-1, c * 9)
    kernel = weight.reshape(o, c * 9).T  # [c*9, o]
    out = patches @ kernel + bias
    return out.reshape(h - 2, w - 2, o).transpose(2, 0, 1)


def _batchnorm(x, gamma, beta, mean, var):
    # x: [C, H, W]
    x = (x - mean[:, None, None]) / np.sqrt(var[:, None, None] + BN_EPS)
    return x * gamma[:, None, None] + beta[:, None, None]


def _maxpool2(x):
    c, h, w = x.shape
    x = x.reshape(c, h // 2, 2, w // 2, 2)
    return x.max(axis=(2, 4))


class ImageAuthModel(object):
    def __init__(self, weights_path):
        self.weights_path = weights_path
        data = np.load(weights_path)
        self.convs = []
        for i in range(4):
            self.convs.append((
                data["conv%d.weight" % i], data["conv%d.bias" % i],
                data["bn%d.weight" % i], data["bn%d.bias" % i],
                data["bn%d.running_mean" % i], data["bn%d.running_var" % i],
            ))
        self.fc_weight = data["fc.weight"].astype(np.float32)
        self.fc_bias = data["fc.bias"].astype(np.float32)

    def preprocess(self, image_bytes):
        img = Image.open(io.BytesIO(image_bytes))
        img.verify()
        img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
        img = img.resize((SIZE, SIZE), Image.BILINEAR)
        arr = np.asarray(img, dtype=np.float32) / 255.0
        arr = (arr - 0.5) / 0.5
        return np.ascontiguousarray(arr.transpose(2, 0, 1))

    def forward(self, x):
        for i, (cw, cb, gw, gb, rm, rv) in enumerate(self.convs):
            x = _conv3x3(x, cw, cb)
            x = _batchnorm(x, gw, gb, rm, rv)
            x = np.maximum(x, 0)
            x = _maxpool2(x)
        x = x.mean(axis=(1, 2))  # global average pool
        logits = self.fc_weight @ x + self.fc_bias
        return logits

    def predict(self, image_bytes):
        x = self.preprocess(image_bytes)
        logits = self.forward(x)
        probs = np.exp(logits - logits.max())
        probs = probs / probs.sum()
        return CLASSES[int(np.argmax(probs))], list(probs.astype(float))


_MODEL = None


def get_model():
    global _MODEL
    if _MODEL is None:
        path = os.environ.get(
            "IMAGE_AUTH_MODEL_PATH",
            os.path.join(os.path.dirname(os.path.abspath(__file__)), "model_weights.npz"),
        )
        _MODEL = ImageAuthModel(path)
    return _MODEL
