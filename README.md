# CubeLander · 技术札记

中文技术博客，部署在 <https://cubelander.github.io>。第一组文章来自 BetterScale 的公开技术记录；不维护个人履历、职业经历或联系方式。

## 本地开发

需要 Node.js 22+、npm 和 Python 3（构建检查使用标准库）。

```sh
npm ci --ignore-scripts
npm run dev
npm test
```

`npm run dev` 在回环地址 8080 端口预览；修改内容后另开终端运行 `npm run build` 并刷新页面。使用 Eleventy 3.1.6，将 `src/` 生成到 `_site/`。阅读文章不依赖客户端 JavaScript，无外部字体、跟踪器或第三方前端请求。不要把 `_site/`、`node_modules/` 或本地私有资料提交到 Git。

## 写一篇文章

在 `src/posts/` 增加 Markdown，参照现有 front matter：

- `title`、`description`：标题与摘要；
- `date`：发布日期（显式填写）；
- `order`：系列阅读顺序；
- `category`、`topics`、`scope`：内容分类、标签和阅读边界；
- `series`、`snapshot`、`sources`：系列及公开证据快照，默认来自 BetterScale。

正文 URL 为 `/notes/<文件名>/`；构建同时产生含标题和来源的 `/text/<文件名>.md`。修改已发布文件名会改变链接，应保留原 URL 或添加重定向页面。新增非 BetterScale 专题时，调整目录数据、模板中的来源仓库和主题索引，不要让旧证据默认值泄漏到新文章。

## 发布

推送 `main` 后，GitHub Actions 执行锁定依赖安装、构建与站内检查，再发布 `_site/`。仓库 Pages source 配置为 GitHub Actions；只有构建产物公开到网站，仓库源文件本身仍为公开 GitHub 内容。

```sh
npm test
git add <明确的修改文件>
git commit -m "Update technical notes"
git push origin main
```

首页、专题页、404、Atom 订阅、sitemap、robots 和 Markdown 正文导出均由当前工程维护。`npm test` 检查内部链接及锚点、页面元数据、正文导出与 XML；不替代桌面/移动端视觉检查或外部证据核对。

## 证据与来源

首批四篇为新整理的阅读文章，不是原报告逐字转载，也不是新的硬件实验。主要依据 BetterScale 公开快照 `872b4133dd76c999b5709d52643cdac2602374f7`；三份主要报告和 RESULTS.md 与提供的本地材料 Git blob 完全一致。文章底部链接固定快照，避免 main 变化悄悄改变论据。

保留原项目与上游归属，不声明所有研究由个人独立完成。本站未复制 BetterScale 代码、图形资产或原始实验包。日期区分文章整理日期和实验发生日期。

## 构建依赖边界

2026-10-08 的 npm audit 报告 9 项传递构建/开发依赖告警（4 moderate、5 high），根因涉及 `braces` 与 `sprintf-js` 的拒绝服务问题，当前依赖树无可直接采用的修复；npm 建议回退到 Eleventy 0.6.0，不采用该破坏性降级。

这些包不发送到访客浏览器，网站没有服务端 Node 运行时。构建只消费维护者信任的仓库内容，开发服务器限定回环地址；不开放上传和不受信任模板渲染，也不为外部 PR 配置特权构建。更新依赖时重新核查，而非把审计告警当成已修复。

## 出租车交互展示

导航「出租车」指向 `/taxi/`。`public/taxi/index.html` 是去除报告人姓名、班级与署名的独立课堂展示，包含 2023—2024 年 NYC TLC 公开数据的统计结果、地图和交互。该文件由课程分析工程的公开导出命令生成，不手工修改内嵌数据；更新时只替换审查过的公开版 HTML，不复制课程 Word、截图或私有工程。

Eleventy 原样复制此目录，不对统计 JSON 或脚本求值。`npm test` 检查页面元数据、入口与锚点；图表数值和交互由分析工程的浏览器检查验证。网站源文件也公开，因此个人信息必须在提交前去除。

公开提交也应使用 `CubeLander` 与 GitHub `users.noreply.github.com` 隐私邮箱；不要继承本机可能含真实姓名/个人邮箱的默认 Git 身份。发布前同时检查文件内容和提交元数据。
