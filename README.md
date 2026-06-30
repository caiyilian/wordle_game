# Wordle Game | 猜单词游戏

多人互动式 Wordle（猜单词）游戏，支持 Web 端、Electron 桌面端、微信小程序三端。

- **后端**: Python FastAPI + SQLAlchemy + PostgreSQL/SQLite
- **前端**: Vue 3 + TypeScript + Tailwind CSS + Pinia
- **桌面**: Electron + electron-builder
- **小程序**: uni-app (mp-weixin)

---

## 目录结构

```
wordle_game/
├── backend/          # FastAPI 后端
│   ├── core/         # 核心逻辑 (游戏、评分、成就)
│   ├── routers/      # API 路由
│   ├── ws/           # WebSocket 处理
│   ├── models/       # 数据库模型
│   └── tests/        # 测试 (43 个)
├── frontend/         # Vue 3 前端 (Web + Electron)
│   ├── src/          # Vue 源码
│   ├── electron/     # Electron 主进程
│   └── dist_electron/# Electron 打包产物
├── miniapp/          # 微信小程序 (uni-app)
│   ├── src/
│   │   ├── api/      # HTTP + WebSocket 客户端
│   │   ├── store/    # Pinia 状态管理
│   │   ├── components/   # 游戏组件
│   │   └── pages/    # 页面
│   └── pages.json
├── resources/        # 词库 + 字体
└── deploy/           # 部署配置
```

---

## 后端 (FastAPI)

### 启动

```bash
# 安装依赖
pip install -r backend/requirements.txt

# 启动开发服务器（默认 SQLite）
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 初始化数据库（首次需要）
python scripts/init_db.py
```

API 文档：`http://localhost:8000/docs`

### 测试

```bash
cd backend
python -m pytest -v
```

---

## Web 前端 (Vue 3)

### 启动

```bash
cd frontend
npm install
npm run dev
```

访问 `http://localhost:5173`

### 构建

```bash
npm run build
```

---

## Electron 桌面端

### 开发模式

```bash
cd frontend
npm run dev:electron
```

### 打包为安装包

```bash
cd frontend
npm run build:electron
```

打包产物位于 `frontend/dist_electron/`：

| 平台 | 文件 |
|------|------|
| Windows | `Web Wordle Setup 1.0.0.exe` (NSIS 安装包) |
| macOS | 需在 macOS 上运行 `npm run build:electron` |
| Linux | 需在 Linux 上运行 `npm run build:electron` |

> **注意**: 打包时如遇到网络超时，可以设置国内镜像源：
> ```bash
> $env:ELECTRON_MIRROR = "https://npmmirror.com/mirrors/electron/"
> ```

### 运行安装包

1. 双击 `Web Wordle Setup 1.0.0.exe` 安装
2. 安装后启动应用，会在本地启动后端服务器并打开游戏窗口
3. 确保后端已在 `localhost:8000` 运行

---

## 微信小程序 (uni-app)

### 开发现状

小程序已完成基础功能开发，共 14 个文件：

| 目录 | 内容 |
|------|------|
| `src/api/http.ts` | HTTP 客户端（自动带 token） |
| `src/api/websocket.ts` | WebSocket 客户端（自动重连 + 心跳） |
| `src/store/user.ts` | 用户状态 (登录/注册/登出) |
| `src/store/room.ts` | 房间状态 |
| `src/store/game.ts` | 游戏状态 (键盘颜色追踪) |
| `src/components/GameBoard/Row/Cell` | 游戏棋盘组件 |
| `src/components/VirtualKeyboard` | 虚拟键盘 (三行 QWERTY) |
| `src/components/ChatPanel` | 聊天面板 |
| `src/pages/index/index` | 首页 (登录/注册/微信登录/创建加入房间) |
| `src/pages/game/index` | 游戏页 (棋盘 + 键盘 + 聊天) |
| `src/pages/stats/index` | 统计页 (统计卡片 + 猜词分布 + 排行榜) |

### 构建和预览

项目使用 uni-app 框架，需要 HBuilderX 或微信开发者工具。

#### 方式 1：HBuilderX

1. 安装 [HBuilderX](https://www.dcloud.io/hbuilderx.html)
2. 打开项目：`文件 → 导入 → 从本地导入`，选择 `miniapp/` 目录
3. 菜单：`运行 → 运行到小程序模拟器 → 微信开发者工具`

#### 方式 2：CLI 构建

```bash
cd miniapp
npm install
npm run build:mp-weixin
```

构建产物在 `miniapp/dist/build/mp-weixin/`，用微信开发者工具打开该目录即可预览。

#### 方式 3：微信开发者工具

1. 下载安装 [微信开发者工具](https://developers.weixin.qq.com/miniprogram/dev/devtools/download.html)
2. 打开工具 → 导入项目 → 选择 `miniapp/` 目录
3. 需要填写 AppID（在 `manifest.json` 中配置）

### 准备工作

1. **配置微信 AppID**: 修改 `miniapp/manifest.json` 中的 `mp-weixin.appid` 为你的微信小程序 AppID
2. **后端地址**: 小程序代码中后端地址默认为 `http://localhost:8000`
   - 本地开发时，在微信开发者工具中勾选"不校验合法域名..."
   - 生产环境需将 `http://localhost:8000` 替换为实际服务器域名，并在微信小程序后台配置白名单

### 功能清单

- [x] 用户注册/登录（账号密码）
- [x] 微信登录（按钮已集成，需配置微信 AppID 后使用）
- [x] 创建/加入房间
- [x] 游戏棋盘（彩色字母网格）
- [x] 虚拟键盘（颜色同步）
- [x] 聊天面板
- [x] 统计页面（猜词分布 + 排行榜）

---

## 部署

```bash
# 使用 deploy/ 下的配置
cd deploy
# 查看 README.md 获取详细部署说明
```

---

## 规则

每局游戏有 6 次猜测机会，每次猜测后字母会显示颜色反馈：

- 🟩 **绿色** — 位置正确
- 🟨 **黄色** — 存在但位置错误
- ⬜ **灰色** — 不存在于答案中
