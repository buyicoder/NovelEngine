---
name: novel-doctor
description: 项目体检——检查目录完整性、设定文件格式、实体索引健康状态和依赖项。
allowed-tools: Read Bash
argument-hint: "[--format text/json]"
---

# /novel-doctor — 项目体检

检查项目所有维度的健康状态。

## 检查项

1. **目录完整性**：三层结构（稳定/变量/动态）是否完整
2. **设定文件健康**：设定集文件格式是否正确
3. **实体索引健康**：人物/势力/地点索引是否同步
4. **大纲健康**：大纲文件是否存在、是否有明显断档
5. **质量门控健康**：维护文档 + 章记 Schema + 轮换池
6. **违禁句词表**：`稳定层/规则/forbidden_phrases.md` 是否存在
7. **最近章节健康**：最近 5 章是否有章记，轮换项是否异常重复

```bash
python webnovel.py --project-root . doctor
```

输出综合健康报告。
