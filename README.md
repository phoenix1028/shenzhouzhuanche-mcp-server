# 神州专车MCP服务器

这是一个基于最新MCP Python SDK 1.12.0构建的神州专车服务MCP服务器，使用streamable-http传输协议。

## 功能特性

- ✅ 创建专车订单 (`create_order`)
- ✅ 取消专车订单 (`cancel_order`)
- ✅ 修改上车地点 (`update_pickup_location`)
- ✅ 修改下车地点 (`update_dropoff_location`)
- ✅ 获取司机真实电话 (`get_driver_phone`)
- ✅ 获取城市服务信息 (`get_city_services`)
- ✅ 价格预估 (`estimate_price`)
- ✅ 多种OAuth2认证模式支持
- ✅ 自动Token管理和刷新
- ✅ 异步API调用
- ✅ 完整的类型注解

## 系统要求

- Python 3.10+
- MCP Python SDK 1.12.0+
- uv包管理器（推荐）

## 安装

### 方法1: 使用uv (推荐)

```bash
# 如果还没有安装uv
curl -LsSf https://astral.sh/uv/install.sh | sh

# 克隆或进入项目目录
cd shenzhouzhuanche-mcp-server

# uv会自动根据pyproject.toml安装依赖
uv sync
```

### 方法2: 使用pip

```bash
pip install "mcp>=1.12.0" "requests>=2.31.0" "aiohttp>=3.8.0" "uvicorn>=0.24.0" "pydantic>=2.0.0"
```

## 认证配置

神州专车MCP支持多种认证方式，按优先级自动选择：

### 1. 环境变量配置（推荐）

```bash
# 密码模式认证（企业账号）
export SHENZHOU_USERNAME="your_username"
export SHENZHOU_PASSWORD="your_password"

# 是否启用交互式授权
export SHENZHOU_INTERACTIVE="false"
```

### 2. 认证优先级

1. **已保存Token** - 优先使用本地保存的有效token
2. **密码模式** - 如果配置了用户名密码，自动使用密码模式认证
3. **授权码模式** - 如果启用交互模式，提供授权URL供用户手动授权

## 🚀 快速开始

### 最简单的启动方式：

```bash
# 1. 安装uv（如果未安装）
curl -LsSf https://astral.sh/uv/install.sh | sh

# 2. 进入项目目录
cd shenzhouzhuanche-mcp-server

# 3. 一键启动（自动安装依赖和启动服务器）
uv run python server.py
```

### 带认证配置的启动：

```bash
# 设置认证信息（可选）
export SHENZHOU_USERNAME="your_username"
export SHENZHOU_PASSWORD="your_password"

# 启动服务器
uv run python server.py
```

## 运行方式

### 方法1: 使用uv直接启动（推荐）

```bash
# 进入项目目录
cd shenzhouzhuanche-mcp-server

# 使用uv直接启动（会自动安装依赖）
uv run python server.py
```

### 方法2: 使用启动脚本

```bash
# 使用原始启动脚本
./start_http_server.sh

# 或使用改进版启动脚本
./start.sh
```

### 启动后效果

服务器启动后会显示：
- 🚗 服务器运行在 `http://127.0.0.1:8000`
- 📋 可用的7个MCP工具
- 📦 可用的2个MCP资源
- 🔐 当前认证配置状态
- 按 `Ctrl+C` 停止服务器

## MCP工具说明

### 1. create_order - 创建专车订单

创建一个新的神州专车订单。

**参数:**
- `passenger_mobile` (str): 乘客手机号
- `start_lat` (float): 上车地点纬度
- `start_lng` (float): 上车地点经度
- `start_name` (str): 上车地点名称
- `start_address` (str): 上车地点详细地址
- `end_lat` (float): 下车地点纬度
- `end_lng` (float): 下车地点经度
- `end_name` (str): 下车地点名称
- `end_address` (str): 下车地点详细地址
- `passenger_name` (str, 可选): 乘客姓名，默认"乘客"
- `service_id` (int, 可选): 服务类型ID，默认14（立即叫车）
- `car_group_id` (int, 可选): 车型ID，默认2（公务车型）

**返回:** JSON格式的订单创建结果，包含订单ID

### 2. cancel_order - 取消专车订单

取消一个已创建的专车订单。

**参数:**
- `order_id` (str): 订单ID
- `force` (bool, 可选): 是否强制取消，默认False
- `reason` (str, 可选): 取消原因，默认"用户取消"
- `reason_id` (int, 可选): 取消原因ID，默认1

### 3. update_pickup_location - 修改上车地点

修改订单的上车地点。

**参数:**
- `order_id` (str): 订单ID
- `latitude` (float): 新上车地点纬度
- `longitude` (float): 新上车地点经度
- `name` (str): 新上车地点名称
- `address` (str): 新上车地点详细地址

### 4. update_dropoff_location - 修改下车地点

修改订单的下车地点。

**参数:**
- `order_id` (str): 订单ID
- `latitude` (float): 新下车地点纬度
- `longitude` (float): 新下车地点经度
- `name` (str): 新下车地点名称
- `address` (str): 新下车地点详细地址

### 5. get_driver_phone - 获取司机真实电话

获取订单对应司机的真实电话号码。

**参数:**
- `order_id` (str): 订单ID
- `ptn_order_id` (str, 可选): 第三方订单ID

**返回:** 包含司机电话的响应

### 6. get_city_services - 获取城市服务信息

获取神州专车支持的城市及服务信息。

**返回:** 城市服务信息列表

### 7. estimate_price - 价格预估

预估行程价格。

**参数:**
- `start_lat` (float): 出发地纬度
- `start_lng` (float): 出发地经度
- `end_lat` (float): 目的地纬度
- `end_lng` (float): 目的地经度
- `service_id` (int, 可选): 服务类型ID，默认14
- `car_group_id` (int, 可选): 车型ID，默认2

## MCP资源

### shenzhou://config - 配置信息

访问神州专车服务的配置信息（不包含敏感数据）。

### shenzhou://token-status - Token状态

获取当前认证Token的状态信息。

## 开发和调试

### 运行测试套件

```bash
# 基础功能测试
uv run python test_server.py

# 如果配置了密码认证，会自动测试完整订单流程
export SHENZHOU_USERNAME="test_username"
export SHENZHOU_PASSWORD="test_password"
uv run python test_server.py
```

### 类型检查

```bash
# 安装mypy
uv add --dev mypy

# 运行类型检查
uv run mypy *.py
```

### 代码格式化

```bash
# 安装ruff
uv add --dev ruff

# 运行代码检查
uv run ruff check .

# 自动修复
uv run ruff check --fix .
```

## 项目结构

```
shenzhouzhuanche-mcp-server/
├── pyproject.toml          # 项目配置和依赖
├── server.py               # MCP服务器主文件
├── config.py              # 配置管理
├── models.py              # 数据模型定义
├── auth_manager.py        # 认证管理器
├── shenzhou_client.py     # 神州专车API客户端
├── token_manager.py       # Token生命周期管理
├── test_server.py         # 测试套件
├── start_http_server.sh   # 启动脚本
└── README.md              # 项目文档
```

## API权限说明

不同认证模式有不同的API访问权限：

| 功能类别 | 客户端模式 | 授权码模式 | 密码模式 |
|----------|------------|------------|----------|
| 基础查询API | ✅ | ✅ | ✅ |
| 订单创建 | ❌ | ✅ | ✅ |
| 订单修改 | ❌ | ✅ | ✅ |
| 地点修改 | ❌ | ✅ | ✅ |
| 司机信息查询 | ✅ | ✅ | ✅ |

## 注意事项

1. ⚠️ **订单创建权限**: 只有用户授权或企业账号的token才能创建订单
2. 🔄 **Token管理**: 系统会自动管理token生命周期和刷新
3. 🧪 **测试环境**: 当前配置使用沙盒环境，不会产生实际费用
4. 📱 **手机号要求**: 创建订单需要提供有效的手机号
5. 📍 **地理坐标**: 所有位置参数使用WGS84坐标系

## 版本信息

- MCP Python SDK: >=1.12.0
- 传输协议: streamable-http (生产推荐)
- Python要求: >=3.10
- 包管理器: uv (推荐)

## 许可证

MIT License