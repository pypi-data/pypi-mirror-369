import time
from typing import Dict, List

import matplotlib.pyplot as plt
import numpy as np
import torch as tc
import torch.nn as nn
from PIL import Image
from torch.utils.data import Dataset


def model_size(m: nn.Module):
    a = sum(p.numel() for p in m.parameters())
    b = sum(p.numel() for p in m.parameters() if p.requires_grad)
    return f"trainable: {b}/{a}"


class WindowDataset(Dataset):
    def __init__(s, x, W):
        s.x, s.W = x, W

    def __len__(s):
        return len(s.x) - s.W + 1

    def __getitem__(s, idx):
        return s.x[idx : idx + s.W]


# ==============================

D_TYPE = Dict[str, np.ndarray]
D2_TYPE = Dict[str, D_TYPE]


def slice_xy(xy: D2_TYPE, r1, r2, num=None):
    xy2 = {}
    for sym, d in xy.items():
        x, y = d["x"], d["y"]
        n = len(x)
        i1, i2 = int(r1 * n), int(r2 * n)
        step = max(1, (i2 - i1) // num) if num else 1
        x, y = x[i1:i2:step], y[i1:i2:step]
        xy2[sym] = dict(x=x, y=y)
    print(f"slice_xy: n: {n}, i1: {i1}, i2: {i2}, step: {step}, n2: {len(x)}")
    return xy2


def timer(func):
    def func2(*args, **kwargs):
        t1 = time.time()
        res = func(*args, **kwargs)
        print(f"{func.__name__} took {time.time() - t1:.3f} seconds")
        return res

    return func2


def tensor(x):
    if isinstance(x, np.ndarray):
        return tc.from_numpy(x.copy()).float()
    if isinstance(x, dict):
        return {k: tensor(v) for k, v in x.items()}
    if isinstance(x, list):
        return [tensor(v) for v in x]
    return x


def to_np(x):
    if isinstance(x, tc.Tensor):
        return x.detach().numpy()
    if isinstance(x, dict):
        return {k: to_np(v) for k, v in x.items()}
    if isinstance(x, list):
        return np.array([to_np(v) for v in x])
    return x


def shape(x):
    if isinstance(x, (np.ndarray, tc.Tensor)):
        return x.shape
    if isinstance(x, dict):
        return {k: shape(v) for k, v in x.items()}
    if isinstance(x, list):
        return {shape(v) for v in x}


# ==================================


def plot_general(plots: D_TYPE, id, C=2):
    R = int(np.ceil(len(plots) / C))
    plt.figure(figsize=(4 * C, 3 * R))
    i = 0
    for k, v in plots.items():
        v = to_np(v)
        i += 1
        plt.subplot(R, C, i)
        plt.title(k)
        if k.endswith("dist"):
            if isinstance(v, dict):
                plt.hist(v["x"].flatten(), bins=100, range=v["range"])
            else:
                v = v.flatten()
                mean, std = v.mean(), v.std() * 3
                plt.hist(v, bins=100, range=[mean - std, mean + std])
        else:
            x = np.arange(len(v))
            if np.any(np.isnan(v)):
                plt.scatter(x, v, s=3)
            else:
                plt.plot(x, v)
    plt.tight_layout()
    plt.savefig(id)
    plt.close()


def transpose_records(records: List[Dict]):
    return {k: np.array([r[k] for r in records]) for k in records[0]}


def plot_records(records: List[Dict], id, C=1):
    dic = transpose_records(records)
    R = int(np.ceil(len(dic) / C))
    plt.figure(figsize=(4 * C, 3 * R))
    i = 0
    for k, v in dic.items():
        i += 1
        plt.subplot(R, C, i)
        plt.title(k)
        x = np.arange(len(v))
        if np.any(np.isnan(v)):
            plt.scatter(x, v, s=3)
        else:
            plt.plot(x, v)
    plt.tight_layout()
    plt.savefig(id)
    plt.close()


def plot_xy(xy: D2_TYPE, id="xy"):
    R, C = 5, 2
    plt.figure(figsize=(4 * C, 3 * R))
    i = 0
    for sym, d in xy.items():
        i += 1
        x, y = d["x"], d["y"]
        plt.subplot(R, C, i)
        plt.title(sym)
        for k in range(x.shape[1]):
            plt.plot(x[:, k], label=f"x[:, {k}]")
        plt.legend()
        i += 1
        plt.subplot(R, C, i)
        plt.plot(y)
        if i == R * C:
            break
    plt.tight_layout()
    plt.savefig(id)
    plt.close()


# =====================


class GIFMaker:
    def __init__(s):
        s.frames: List[Image.Image] = []

    def add(s, path):
        s.frames.append(Image.open(path).copy())

    def save(s, id, fps=10):
        s.frames[0].save(
            f"{id}.gif",
            format="GIF",
            append_images=s.frames[1:],
            save_all=True,
            duration=int(1000 / fps),
            loop=0,
            optimize=True,
        )
