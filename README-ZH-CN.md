<div align="center">

<img src=".github/assets/send-to-back.svg" width="128" height="128" alt="Decky Localsend" />

# Decky LocalSend

![visitors](https://visitor-badge.laobi.icu/badge?page_id=moyoez/Decky-localsend) ![Release](https://img.shields.io/github/v/release/moyoez/decky-localsend) ![License](https://img.shields.io/badge/license-BSD--3--Clause-green) ![GitHub Actions Workflow Status](https://img.shields.io/github/actions/workflow/status/MoYoez/Decky-Localsend/build.yaml)



<p>



[ENGLISH](README.md) | [简体中文](README-ZH-CN.md)

![preview](https://raw.githubusercontent.com/moyoez/decky-localsend/main/.github/assets/preview_cn.jpg)

将 Localsend 特性带到 Steam 大屏幕模式中

相关后端项目: [MoYoez/localsend-go](https://github.com/MoYoez/localsend-go)

</div>

---

## 特点

- 全套 Localsend 协议 支持 (除 Web Localsend 外)
- Shared Via Link 链接单向传送文件
- 支持浏览截图上传
- 一些 Localsend 自己的特性 (e.g. 接受历史列表 PIN码 ，以及部分环境下 http / https 环境处理)

## 演示

![preview_cn_1](.github/assets/preview_cn_1.jpg)
![preview_cn_2](.github/assets/preview_cn_2.jpg)
![preview_cn_3](.github/assets/preview_cn_3.jpg)
![preview_cn_4](.github/assets/preview_cn_4.jpg)

## 使用方法

> 本插件需要在 Decky Loader 3.0 即以上运行

1. 在你的 Steam Deck 上安装本插件：  

   - 进入 Decky 商店下载 Decky Localsend
   - 或者从 release 下载最新 Release  
   - 或者在 Decky 中以 URL 格式安装 输入
  
     > https://ba.sh/63Vg

> 没有 Decky ? ｜ 请参考 [Decky-Loader](https://github.com/SteamDeckHomebrew/decky-loader) | 如果必要的话，你可以搜索一下 [B站](https://www.bilibili.com/video/BV1X5rGBdEDG) / [抖音](https://www.douyin.com/video/7593785753583340852) 以获取安装方式

1. 从快捷访问菜单中打开插件
2. 点击“启动后端”后，LocalSend 服务器会自动启动
3. 你的 Steam Deck 现在可以被其他 LocalSend 客户端发现
4. 从运行 LocalSend 的任意设备发送文件到你的 Steam Deck


## 配置说明

插件默认使用以下设置：

- **端口 (Port)：** 53317
- **协议 (Protocol)：** HTTPS
- **上传目录 (Upload Directory)：** `~/homebrew/data/decky-localsend/uploads`
- **配置文件 (Config File)：** `~/homebrew/settings/decky-localsend/localsend.yaml`

你可以在插件界面自定义这些设置。

## 项目结构

```
.
├── backend/             # Go 后端实现
│   └── localsend/       # LocalSend 协议实现
├── src/                 # 前端 React 组件
│   ├── index.tsx        # 插件主要入口
│   └── utils/           # 工具函数
├── main.py              # Python 后端桥接
├── plugin.json          # 插件元数据
└── package.json         # Node.js 依赖
```

## 待办事项

无🤔

## 已知BUG

- 在部分情况下，Decky-Localsend 无法扫描到开启时间较久的设备 (半分钟扫描一次， 默认超时为 500s，**可使用 主动扫描 来让其他设备检测到此插件** )，如果在可接受范围内没有找到远程设备，请考虑重启需要传输的 Localsend

- 在部分情况下，插件只能在相同的加密协议工作，即使有针对此情况的适配.

- 在大量且多（测试文件数量3000+）传输给 Deck 的时候，因为跑的线程很多，Localsend 传输端 可能会出现抽搐的情况（但实际不影响传输）

- HTTP 扫描可能会造成延迟增加，HTTP超时已经默认调整成 60s ,30s一次，默认使用 Notify 进行设备更新，可不用刷新获取设备

- 请尽量避免单次选择大量文件（建议不超过200个文件）进行传输，过多的文件可能导致 Decky UI 崩溃（文件夹本身数量不受影响，仅单次选择文件数需注意）。

### 兼容表

| 通信方式      | Decky-Localsend 支持 | 能发现的远程 Localsend 设备 | 说明                                      |
|---------------|---------------------|---------------------------|-------------------------------------------|
| UDP 扫描      | HTTP/HTTPS          | HTTP、HTTPS               | UDP 能发现任意协议设备                     |
| HTTP 通信     | HTTP                | HTTP                      | 仅支持与 HTTP 协议设备互通                 |
| HTTPS 通信    | HTTPS               | HTTPS                     | 仅支持与 HTTPS 协议设备互通                |

> UDP 通信下，无论远程设备是 HTTP 还是 HTTPS，Decky-Localsend 都能扫描并发现。


## 关于开发

```bash

# Fork 一份你自己的仓库 , 替换 {username} 为你的名字

git clone --recurse-submodules git@github.com:{username}/Decky-Localsend.git

cd Decky-Localsend/backend/localsend

# 需要 Golang >= 1.25.7

go mod tidy

cd Decky-Localsend/backend/localsend/web

# 需要 NodeJS > 20

npm i

npm build


```

### 编译

参考 [Github Action Build](.github/workflows/build.yaml)

### 发布版本

`package.json` 使用三段正式版本号（`X.Y.Z`），Release 标签必须为对应的 `vX.Y.Z`，安装 ZIP 内的版本也必须一致。CI 会在上传 Artifact 前检查源码、标签推送、构建 ZIP 和重新打包后的版本；不会自动发布 Release。

历史 `v0.45` 实际安装为 `0.4.5`，导致按标签比较版本的更新器反复提示更新。下一候选版本为 `0.45.1` / `v0.45.1`，高于 `0.4.5` 和 `0.45`（按 `0.45.0` 比较）。保留已有标签及下载链接，后续版本继续高于 `0.45.0`；回到 `0.4.x` 可能使跟踪旧标签的客户端无法正常升级。插件标识和用户设置保持不变。

手动创建 Release 前，在仓库根目录针对准备上传的实际 ZIP 执行以下检查，并按需替换标签和路径：

```bash
python3 -m unittest discover -s tests -v
python3 scripts/check_release_version.py --tag v0.45.1 --archive /path/to/decky-localsend.zip
```

分支和 PR 构建无需标签，也会校验版本。标签构建通过不代表之后手动上传的其他 ZIP 已经通过检查。

## 鸣谢

- [LocalSend](https://localsend.org)

> 这个插件是基于 Localsend 协议写的，所以快去给个Star吧！

- [Decky Loader](https://github.com/SteamDeckHomebrew/decky-loader)

- [ba.sh](https://app.ba.sh/)
