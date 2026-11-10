# T3 独立复跑记录

在本目录执行：

```sh
/mnt/disk3/liuyutong_home/miniconda3/envs/evo/bin/python predict.py --samples samples.txt --json results/independent-predictions.json > logs/independent-predict.log 2> logs/independent-predict.stderr
```

退出状态：0。六张本地训练图像的预测依次为 `0_1, 1, 0_1, 1, 0_2, 0_2`；路径标签依次为 `1, 1, 0_1, 0_1, 0_2, 0_2`。完整 logits、概率和样例路径见 `results/independent-predictions.json`。这些训练样例只证明推理运行，不能作为泛化能力评估。

模型和 Python 环境仍引用原有本地绝对路径，不是自包含部署包；服务、容器和提交均未验证。
