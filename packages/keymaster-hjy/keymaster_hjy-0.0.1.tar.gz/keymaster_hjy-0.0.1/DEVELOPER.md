# Keymaster_hjy: 开发者文档

本文档面向 `keymaster_hjy` 的维护者、贡献者或希望深入了解其内部工作原理的开发者。

## 1. 设计哲学与指导原则

本项目严格遵循三大核心原则：

- **苹果产品原则 (高内聚、低耦合)**: `keymaster_hjy` 将所有复杂性（数据库交互、Redis缓存、配置管理）封装在内部。对外仅暴露一个极其简单的`master`对象，其API直观、易用。
- **云原生公民原则 (配置驱动、依赖注入)**: 模块不持有任何基础设施，而是通过自动读取`.env`文件来获取用户授权的数据库和Redis连接信息。所有配置均从用户自己的RDS中动态“注入”，完全服从于用户的环境。
- **双重文档使命**: `README.md` 面向使用者，本 `DEVELOPER.md` 面向维护者。

## 2. 架构与核心流程

### 2.1. 零配置自动初始化

这是`keymaster_hjy`的核心特性。当用户在代码中首次执行`from keymaster_hjy import master`时，`_master.py` 中的 `_build_master()` 函数被调用，创建了 `KeyMaster` 的单例。

当首次访问 `master` 对象的任何服务（如 `master.keys.create()`）时，会触发 `KeyMaster` 内部的 lazy-loading 机制：

1.  `_ensure_engine()`:
    - 调用 `ConfigProvider` 查找并解析 `mysql.env`。
    - 使用凭证构建 SQLAlchemy engine。
    - 调用 `init_db()`，进而调用 `schema.create_all()`，在用户数据库中幂等地创建所有 `keymaster_*` 表。
    - 调用 `ensure_default_settings()`，向 `keymaster_settings` 表写入默认配置。
2.  `_ensure_redis()`:
    - 调用 `ConfigProvider` 查找 `mysql.env` (或 `redis.env`) 中的 Redis 配置。
    - 如果找到，则创建一个 `redis.Redis` 客户端实例。
3.  **服务实例化**:
    - `_settings_service()`: 传入 engine 实例化 `SettingsService`。
    - `_keys_service()`: 传入 engine 和 `SettingsService` 实例化 `KeysService`。
    - `_auth_service()`: 传入 engine、`SettingsService` 和可选的 Redis 客户端实例化 `AuthService`。

### 2.2. 鉴权流程 `validate_key`

`AuthService.validate_key` 是安全的核心，执行以下原子化检查链：

1.  **解析与哈希**: 对传入的明文 Key 进行哈希。
2.  **数据库查找**: 在 `keymaster_keys` 表中查找匹配的 `hashed_key`。
3.  **状态检查**: 校验 `is_active` 和 `expires_at` 字段。
4.  **速率限制**:
    - 如果 `AuthService` 持有 Redis 客户端，则使用 `RedisFixedWindowLimiter` 进行分布式限流。
    - 否则，降级为 `_InMemoryFixedWindowLimiter`，仅用于开发环境。
5.  **权限范围 (Scope) 检查**: 如果调用时传入 `required_scope`，则查询 `keymaster_key_scope_map` 映射表，确认 Key 具备该权限。
6.  **日志审计**: 无论成功与否，都将请求信息异步（未来规划）写入 `keymaster_logs` 表。

## 3. 本地开发与测试

### 3.1. 环境设置

```bash
# 1. 创建虚拟环境
python3 -m venv .venv
source .venv/bin/activate

# 2. 安装依赖 (包括测试和框架依赖)
pip install -U pip wheel -i https://pypi.tuna.tsinghua.edu.cn/simple
pip install -e .[test] -i https://pypi.tuna.tsinghua.edu.cn/simple
# (需要在 pyproject.toml 中定义 [project.optional-dependencies])
```

我们推荐在 `pyproject.toml` 中加入以下内容以简化测试依赖安装：

```toml
[project.optional-dependencies]
test = [
    "pytest",
    "fakeredis",
    "fastapi",
    "uvicorn",
    "flask",
    "httpx",
]
```

### 3.2. 运行测试

```bash
pytest
```

测试使用 `fakeredis` 和 `sqlite` (内存/临时文件) 进行，不依赖外部服务，确保了测试的快速和隔离性。

## 4. 目录与文件结构

- `keymaster_hjy/`: 核心源代码
  - `__init__.py`: 暴露公共 API (`master`, `KeyMaster`)。
  - `_master.py`: `KeyMaster` 类，核心编排与 lazy-loading。
  - `auth_service.py`: 鉴权逻辑。
  - `keys_service.py`: Key 生命周期管理。
  - `tags_service.py`: 标签管理。
  - `settings_service.py`: RDS 配置中心服务。
  - `config_provider.py`: `.env` 文件解析。
  - `db_init.py`: 数据库初始化。
  - `schema.py`: SQLAlchemy 表定义。
  - `exceptions.py`: 自定义异常。
  - `integrations.py`: FastAPI/Flask 装饰器。
  - `redis_limiter.py`: Redis 限流器。
  - `utils.py`: 通用工具函数。
- `tests/`: 单元测试与集成测试。
- `tmp/`: 临时脚本，如 `e2e_demo.py`，不应提交。
- `pyproject.toml`: 项目元数据与依赖。
- `.github/workflows/ci.yml`: GitHub Actions CI 配置。
