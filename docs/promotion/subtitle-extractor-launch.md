# Subtitle Studio 公众号发布稿

## 标题候选

1. 一个链接或一个文件，直接生成 SRT 字幕
2. 我把 YouTube、B站、X 和本地视频的字幕提取做成了一个工具
3. 别再手动扒字幕了：先取字幕轨，没有再转写

## 摘要

Subtitle Studio 支持粘贴 YouTube、Bilibili、X/Twitter 链接，或上传本地视频、音频，直接输出 SRT、VTT 和 TXT。它优先提取平台现成字幕轨；没有字幕轨时，再用 Whisper 做语音转写。B站弹幕不会被当成字幕。

在线体验：https://subtitle.powcai.top/

Agent skill：https://github.com/powcai001/ai-plugin

## 正文草稿

### 一个很常见的小麻烦

看视频时想保存字幕，通常会遇到三种情况：

1. 平台明明有字幕，却不知道怎么导出。
2. 视频没有字幕轨，只能靠语音转写。
3. 视频和字幕都在本地，格式却各不相同。

更麻烦的是，很多“字幕下载工具”把 B站弹幕也混在一起。可弹幕是评论，不是字幕；做学习笔记、翻译、剪辑或归档时，我们要的是带时间轴的字幕文件。

### 我做了什么

我做了一个 Subtitle Studio，现在支持四类输入：

- YouTube 视频链接
- Bilibili 视频链接
- X/Twitter 视频链接
- 本地视频或音频文件

输出格式有三种：

- SRT：剪辑软件和播放器最通用
- VTT：网页播放器常用
- TXT：只要文本内容时最方便

你可以在这里直接试用：

https://subtitle.powcai.top/

### 它的处理逻辑

这个工具不是一开始就转写，而是分两步：

第一步，优先找现成字幕轨。平台字幕、自动字幕、本地视频内嵌文本字幕会被直接提取并转换。这样速度更快，也尽量保留原始文字。

第二步，只有找不到可用字幕轨时，才提取语音并用 Whisper 转写。转写支持自动识别语言，也可以手动指定中文、英文、日文、韩文。

所以它能分清三种结果：

- 字幕轨提取：来自平台或视频文件
- 语音转写：由音频生成
- 不支持的情况：烧录在画面里的硬字幕需要 OCR，目前暂不支持

### 文件和隐私

网页版支持上传本地视频和音频，最大 500MB。站点只处理你提交的媒体；上传媒体和临时音轨在处理完成后立即清理，生成结果最多保留 2 小时。

如果你更希望完全在自己的电脑上运行，也可以使用 Agent skill。把它装进 Codex 或兼容 Agent 后，直接丢给 Agent 一个链接或本地文件路径，它会按同样规则输出字幕文件。

安装命令：

```bash
npx skills add https://github.com/powcai001/ai-plugin \
  --skill subtitle-extractor -g -y
```

### 适合谁用

- 做课程笔记的人：把讲座、教程和访谈变成可搜索文本
- 做翻译的人：先拿时间轴字幕，再进入编辑和翻译流程
- 做剪辑的人：快速给素材生成 SRT 草稿
- 做资料归档的人：把视频里的语音变成可检索记录

### 边界也说清楚

这个工具不承诺“任何视频都能成功”。平台登录、地区限制、视频权限、无有效语音、纯音乐视频，都会影响结果。硬字幕 OCR 也在后续计划里，当前版本不会误报支持。

如果你在使用中遇到失败案例，欢迎把链接或场景发给我。工具会优先解决真实工作流里的问题。

## 短推广文案

### 公众号导语

YouTube、B站、X、本地音视频，统一导出 SRT/VTT/TXT。先提取现成字幕轨，没有再 Whisper 转写；只要字幕，不收弹幕。

### 朋友圈 / 社群

做了一个字幕工具：粘贴链接或上传音视频，直接生成 SRT/VTT/TXT。它会优先取现成字幕，没有字幕才转写，B站弹幕也不会混进来。试用：https://subtitle.powcai.top/

### X / Twitter

Subtitle Studio: turn YouTube, Bilibili, X, or local media into SRT/VTT/TXT subtitles.

It extracts existing subtitle tracks first, then falls back to local Whisper transcription when needed.

Try it: https://subtitle.powcai.top/

### 一句话介绍

先取字幕轨，没有再转写；把链接或本地音视频变成能用的字幕文件。

## 发布检查

- [ ] 标题、摘要、正文中的功能范围一致
- [ ] 首图或截图展示输入、输出格式和结果预览
- [ ] 文末放置网站二维码
- [ ] 文末放置 GitHub 链接
- [ ] 发布前用公开视频链接做一次实测
- [ ] 发布前用一个本地视频做一次实测
- [ ] 不宣传硬字幕 OCR
