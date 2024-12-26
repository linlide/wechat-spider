# 微信公众号文章爬虫

这是一个用于抓取微信公众号文章信息的爬虫工具。它可以自动获取文章标题、发布时间、阅读量和点赞数等信息，并将数据保存到MySQL数据库中。

## 功能特点

- 自动获取文章标题、发布时间、阅读量和点赞数
- 支持自动滚动页面，持续抓取数据
- 数据实时保存到MySQL数据库
- 支持导出数据到Excel文件
- 防重复抓取机制
- 详细的日志记录

## 系统要求

- Python 3.8+
- MySQL 5.7+
- Android设备（用于运行微信）
- ADB工具（用于与Android设备通信）

## 目录结构

```
wechat-spider/
├── core/               # 核心代码目录
│   └── crawler.py      # 爬虫核心代码
├── utils/              # 工具类目录
│   └── mysqldb.py     # 数据库工具类
├── scripts/            # 脚本目录
│   └── convert_to_excel.py  # Excel转换脚本
├── sql/               # SQL脚本目录
│   └── init.sql       # 数据库初始化脚本
├── logs/              # 日志目录
└── requirements.txt   # 项目依赖
```

## 安装步骤

1. 克隆项目到本地：
   ```bash
   git clone https://github.com/linlide/wechat-spider.git
   cd wechat-spider
   ```

2. 创建并激活虚拟环境（推荐）：
   ```bash
   python -m venv venv
   # Windows
   venv\Scripts\activate
   # macOS/Linux
   source venv/bin/activate
   ```

3. 安装依赖：
   ```bash
   pip install -r requirements.txt
   ```

4. 安装 ADB 工具：
   - macOS: `brew install android-platform-tools`
   - Linux: `sudo apt-get install android-tools-adb`
   - Windows: 下载 [Android SDK Platform Tools](https://developer.android.com/studio/releases/platform-tools)

5. 配置MySQL数据库：
   ```bash
   mysql -u root -p < sql/init.sql
   ```

## 使用说明

1. 连接Android设备：
   ```bash
   adb devices
   ```
   确保设备已正确连接并授权。

2. 在Android设备上打开微信公众号文章列表页面。

3. 运行爬虫：
   ```bash
   python core/crawler.py
   ```

4. 导出数据到Excel：
   ```bash
   python scripts/convert_to_excel.py
   ```
   生成的Excel文件将包含以下列：
   - 文章标题
   - 发布时间
   - 阅读量
   - 点赞数
   - 抓取时间

## 配置说明

1. 数据库配置（在代码中修改）：
   ```python
   db_config = {
       'ip': 'localhost',
       'port': 3306,
       'db': 'wechat',
       'user': 'your_username',
       'passwd': 'your_password'
   }
   ```

## 注意事项

1. 确保Android设备已启用USB调试模式
2. 运行爬虫前，请确保微信已打开并显示文章列表页面
3. 建议使用虚拟环境运行项目
4. 定期备份数据库
5. 遵守微信使用条款和相关法律法规
6. 数据仅用于学习研究，请勿用于商业用途

## 常见问题

1. 数据库连接失败
   - 检查数据库配置是否正确
   - 确保MySQL服务已启动
   - 验证用户名和密码

2. ADB连接问题
   - 检查USB连接
   - 确认设备已授权ADB调试
   - 重启ADB服务：`adb kill-server && adb start-server`

3. 数据导出失败
   - 检查数据库中是否有数据
   - 确保有足够的磁盘空间
   - 验证Excel文件未被其他程序占用

4. 爬虫无法获取数据
   - 确保微信页面正确显示文章列表
   - 检查Android设备是否保持唤醒状态
   - 验证ADB连接是否稳定

## 开发说明

1. 代码结构
   - `core/crawler.py`: 爬虫核心逻辑，负责数据抓取
   - `utils/mysqldb.py`: 数据库操作封装
   - `scripts/convert_to_excel.py`: 数据导出工具

2. 扩展开发
   - 遵循代码风格和结构
   - 添加新功能时注意兼容性
   - 确保添加适当的错误处理
   - 更新文档说明

## 许可证

MIT License

## 免责声明

本项目仅供学习研究使用，请勿用于非法用途。使用本工具所产生的一切后果由使用者自行承担。


