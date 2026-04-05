**中文** · [English](README.md)

---

# DailyCheck · 本地打卡追踪器

一个完全运行在本地的个人习惯打卡应用,无需注册账号、无需联网、数据完全掌握在自己手中。

---

## 功能特性

**打卡核心**

- 每天打卡一次,自动维护连续天数计数(`day1`、`day2`、`day3`......)
- 主动点击「不打卡」或当天无操作,连续计数归零(回到 `day0`)
- 支持打卡/跳过时附加文字备注
- 可随时撤销或修改当天及任意历史记录(纠错功能)

**历史足迹**

- **列表视图**:按日期倒序展示所有记录,支持内联编辑与删除
- **日历热力图**:类 GitHub 贡献日历,连签天数越多颜色越深
  - 按年展示(全年 52 周,格子大小自适应容器宽度)
  - 按月展示(自然日历网格,格子内显示日期数字)
  - 自定义时间区间(`auto-fill` 网格,自动适应任意跨度)
  - 可切换「周一 / 周日起始」
  - 鼠标悬停显示当日详情(状态、连签天数、备注)
  - 实时统计徽章(已打卡 X / Y 天)

**数据管理**

- 一键导出全部记录为 JSON 文件
- 从 JSON 文件导入,支持「合并」与「完全替换」两种模式
- 提供旧格式转换脚本(`convert.py`),可将 `.txt` 记录迁移为标准格式

**界面**

- 响应式设计:桌面端侧边栏 + 双栏布局,移动端底部导航栏
- 操作即时反馈(Toast 提示、Loading 遮罩)

---

## 技术栈

| 层 | 技术 |
|---|---|
| 后端 | Python 3 · Flask · flask-cors |
| 前端 | Vue 3(CDN)· Tailwind CSS(CDN)· Day.js · Font Awesome |
| 存储 | 本地 JSON 文件(`checkin_data.json`) |
| 依赖 | 无数据库、无云服务、无构建工具 |

---

## 快速开始

**1. 克隆仓库**

```bash
git clone https://github.com/your-username/dailycheck.git
cd dailycheck
```

**2. 安装后端依赖**

```bash
pip install flask flask-cors
```

**3. 启动服务**

```bash
python app.py
```

**4. 打开浏览器**

访问 [http://localhost:8191](http://localhost:8191),即可开始打卡。

---

## 目录结构

```
dailycheck/
├── app.py              # Flask 后端,提供全部 REST API
├── checkin_data.json   # 数据文件(首次打卡后自动生成)
├── convert.py          # 旧格式迁移脚本
└── static/
    └── index.html      # 前端单文件应用
```

---

## API 文档

| 方法 | 路径 | 说明 |
|---|---|---|
| `GET` | `/api/status` | 今日状态 + 当前连续天数 |
| `GET` | `/api/records` | 全部历史记录(支持 `?start=` `?end=` 过滤) |
| `POST` | `/api/checkin` | 今日打卡 |
| `POST` | `/api/skip` | 今日不打卡(计数清零) |
| `PUT` | `/api/records/:date` | 修改指定日期记录 |
| `DELETE` | `/api/records/:date` | 删除指定日期记录 |
| `GET` | `/api/export` | 导出全部数据为 JSON |
| `POST` | `/api/import` | 导入 JSON 数据(`merge` / `replace`) |

---

## 数据格式

`checkin_data.json` 的结构如下,可直接用文本编辑器查看和修改:

```json
{
  "records": {
    "2025-01-08": {
      "checked": true,
      "note": "完成了今天的任务",
      "streak": 7,
      "timestamp": "2025-01-08T09:30:00",
      "updated_at": null
    },
    "2025-01-09": {
      "checked": false,
      "note": "",
      "streak": 0,
      "timestamp": "2025-01-09T22:00:00",
      "updated_at": null
    }
  }
}
```

- `checked: true` — 当天已打卡
- `checked: false` — 当天主动跳过
- 某日期不存在于 `records` — 当天缺卡
- `streak` — 截至当天的连续打卡天数,`0` 表示中断

---

## 旧数据迁移

如果你有以下格式的历史记录文件(`input.txt`):

```
## 2024
10.01 day0
10.02 day1
10.03 day2（完成了今天的任务）

## 2025
01.01 day0
01.02 day1
```

运行转换脚本即可生成标准 `checkin_data.json`:

```bash
python convert.py
```

格式说明:
- `MM.DD dayN` — N > 0 为已打卡,N = 0 为不打卡
- `MM.DD dayN（备注）` — 带备注,使用**全角括号**包裹
- `MM.DD`(无 day 信息)— 信息缺失,转换时跳过

---

## 许可证

[GPLv3](LICENSE)
