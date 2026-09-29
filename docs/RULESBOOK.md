# RULESBOOK — 可复用经验

本文件记录开发过程中沉淀的可复用经验、约定与坑。条目化、保持简短。
新经验随时追加；来自 exec-plans 归档的教训同步至此。

## 约定

- 文档用中文，代码与标识符用英文
- 文档目录与使用规则见 AGENTS.md

## 经验

- docker-compose 的 `env_file` 指向不存在的文件时整个配置校验失败；骨架/开源仓库场景应写 `env_file: [{path: .env, required: false}]`
