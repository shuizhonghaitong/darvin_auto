{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "# 图像真伪鉴定榜\n\n本次榜单从用户视角出发，重点判断图片是否为原图、是否被处理过、或是否完全由 AI 生成，帮助用户区分身边图片图片信息的真实性。\n\n本榜单数据集范围：文档类（发票/转账记录等）、风景类、人物动物类\n\n## 输入输出\n\n输入：图片，jpg/png等常见格式\n\n输出：鉴定结果文件。结果三分类\n\n- 1：原生无修实拍图\n- 0_1：已修图（**包括人工处理和 AI 局部处理**，例如 PS、醒图、美图、美颜、滤镜、拼接、加字、遮挡、AI 局部重绘、AI 换背景、AI 添加/删除物体等）\n- 0_2：AI 全图生成 \n\n## 指标\n\n1. **排序指标**\n\n0分类（已修图+AI全图生成）F1_0 = （ F1_0_1 + F1_0_2）/ 2\n\n\n\n1. **监测指标**\n\n- 准确率：全集 case 正确的数量 / 全集 case 量\n- 原图 F1_1\n- 已修图 F1_0_1\n- 已修图召回率R_0_1\n- 已修图精准率P_0_1\n- AI 全图生成F1_0_2\n- AI 全图生成召回率R_0_2\n- AI 全图生成精准率P_0_2\n- 平均响应时间 ms\n- 失败率\n\n\n\n**失败判定：**请求失败率超过 5%（返回结果为空）\n\n\n\n## 资源限制与提交方式\n\n1/2 A100-40g显存，2c4g\n\n提交结果文件\n\n\n\n数据集\n\n<cite doc-id=\"NSsFdVE57o0xemxcWRkcpFswnkh\" file-type=\"docx\" title=\"图像鉴定-训练集\" type=\"doc\"></cite>",
      "document_id": "GguVdTxCBoGul4xqTPscxfztn6g",
      "revision_id": 56
    }
  },
  "_notice": {
    "update": {
      "command": "lark-cli update",
      "current": "1.0.98",
      "latest": "1.0.99",
      "message": "lark-cli 1.0.99 available, current 1.0.98, run: lark-cli update"
    }
  }
}
