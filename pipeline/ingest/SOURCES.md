# 数据源清单与合规自查（T2.1）

研究对象：NVIDIA Corporation（NASDAQ: NVDA，CIK 0001045810）

## 数据源清单

| # | 来源 | 内容 | 访问方式 | 合规要点 |
|---|---|---|---|---|
| S1 | SEC EDGAR — submissions JSON | NVIDIA 申报文件索引（10-K/10-Q/8-K） | 公开 JSON API，`https://data.sec.gov/submissions/CIK0001045810.json` | SEC 要求声明 User-Agent（项目名+联系方式）；限速 ≤10 req/s |
| S2 | SEC EDGAR — 10-K 全文 | 年报原文（业务、客户集中度、供应链风险章节） | 公开 HTML，`https://www.sec.gov/Archives/...` | 同上；只取最新一份 10-K |
| S3 | NVIDIA 官方新闻稿 | 合作伙伴关系、投资公告 | 公开页面 | 遵守 robots，不绕任何控制 |
| S4 | 关联公司公开披露 | TSMC/SK Hynix 等财报/新闻中提及 NVIDIA 的内容 | 公开页面 | 同上 |

## 合规自查（对照验收清单第 03 条）

- [x] 全部为合法可访问公开资料：SEC EDGAR 与美国上市公司法定披露均为公开数据
- [x] 不绕过 robots / 登录 / 付费墙 / 验证码 / 限流：EDGAR JSON API 无需登录，遵守官方限速与 User-Agent 政策
- [x] 不提交密钥、个人数据、客户机密：采集对象为公司层面公开披露；LLM_API_KEY 仅存本地 .env（.gitignore 排除）
- [x] 采集结果快照落盘（pipeline/snapshots/），复核不依赖重新抓取

## 实体歧义 / 来源冲突 / 过期信息处理原则

- 实体歧义：以 SEC CIK 与证券代码为锚点建别名表（见 pipeline/resolve/）
- 来源冲突：官方申报文件（10-K/8-K）优先级高于新闻；冲突时状态降级为 inferred 并在 notes 记录
- 过期信息：关系设 valid_from/valid_to；证据带 published_at，评分做时效衰减
