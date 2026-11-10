{
  "ok": true,
  "identity": "user",
  "data": {
    "document": {
      "content": "<title>图像真伪鉴定榜接口文档</title>\n\n# SUT 镜像需要实现探活接口：\n\n```YAML\nhttpGet:\n  path: /ready\n  port: 80\n```\n\nstarting-kit 参考:\n\nhttps://gitlab.4pd.io/gaoziming/image_authenticity_verification_leaderboard/-/tree/main/starting-kit\n\n## 图像真伪鉴定\n\n### a. 接口说明\n\n<sheet sheet-id=\"RUblU0\" token=\"Gz7OsS2NIhYCYCt09ybca1Y6nud\"></sheet>\n\n评测请求仅包含图片内容和图片格式，不会提供图片 ID、文件名、文件路径或真实标签。评测图片的请求顺序会随机打乱。\n\n### b. 请求参数说明\n\n<sheet sheet-id=\"Cl5ExX\" token=\"Gz7OsS2NIhYCYCt09ybca1Y6nud\"></sheet>\n\n请求示例（application/json）：\n\n```Bash\nIMAGE_BASE64=$(base64 -w 0 test.jpg)\n\ncurl -X POST http://localhost:80/api/v1/image-authenticity \\\n  -H \"Content-Type: application/json\" \\\n  -d \"{\n    \\\"image_base64\\\": \\\"${IMAGE_BASE64}\\\",\n    \\\"image_format\\\": \\\"jpg\\\"\n  }\"\n```\n\n请求体示例：\n\n```JSON\n{\n  \"image_base64\": \"/9j/4AAQSkZJRgABAQ...\",\n  \"image_format\": \"jpg\"\n}\n```\n\n### c. 接口响应要求\n\n<sheet sheet-id=\"G2lxWB\" token=\"Gz7OsS2NIhYCYCt09ybca1Y6nud\"></sheet>\n\n响应样例：\n\n```JSON\n{\n  \"success\": true,\n  \"message\": \"鉴定完成\",\n  \"result\": \"0_1\"\n}\n```\n\n`result` 必须是以下三个字符串之一：\n\n```Plain Text\n\"1\"\n\"0_1\"\n\"0_2\"\n```",
      "document_id": "HL7JdRbb6ovlP1xwgN3cnNy7n3g",
      "revision_id": 29
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
