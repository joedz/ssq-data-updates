# 双色球数据包

此仓库只发布 `ssq-update-v1` 开奖数据包，供“双色球本地助手”下载。它不接收或保存用户彩票、策略、备份或任何个人数据。

发布前需使用中国福彩网和中彩网（或省级福彩）交叉核对 `data/ssq-source.json` 中的期号、开奖日和号码。提交后 GitHub Actions 会生成根目录的 `ssq-update.json`；GitHub Pages 地址为：

`https://joedz.github.io/ssq-data-updates/ssq-update.json`

当前基线数据为第 2026096 期。后续将已复核的新记录追加至 `data/ssq-source.json`，不要修改已发布的历史号码。
Verified, local-first SSQ draw update packages
