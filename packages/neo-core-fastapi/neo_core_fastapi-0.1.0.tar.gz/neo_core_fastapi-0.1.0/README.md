# Neo Core FastAPI

A comprehensive FastAPI-based core library providing essential services for modern web applications.

## 🚀 特性

### 核心模型
- **用户管理**: 用户模型、认证、权限控制
- **角色权限**: RBAC权限模型，支持细粒度权限控制
- **应用管理**: 多应用支持，应用配置管理
- **审计日志**: 完整的操作审计和日志记录

### 数据库管理
- **SQLAlchemy 2.0**: 现代化的ORM支持
- **Alembic迁移**: 数据库版本管理
- **连接池**: 高性能数据库连接管理
- **多数据库**: 支持PostgreSQL、MySQL、SQLite

### 服务层
- **基础服务**: 通用CRUD操作封装
- **认证服务**: JWT令牌管理、密码加密
- **权限服务**: 权限检查、角色管理
- **缓存服务**: Redis缓存集成

### 中间件
- **认证中间件**: 自动用户认证
- **权限中间件**: 路由级权限控制
- **日志中间件**: 请求响应日志记录
- **CORS中间件**: 跨域请求处理

### 工具库
- **密码工具**: 密码加密、验证
- **JWT工具**: 令牌生成、验证、刷新
- **验证工具**: 数据验证、格式化
- **时间工具**: 时区处理、格式转换

## 📦 安装

```bash
# 基础安装
pip install neo-core-fastapi

# 开发环境安装
pip install neo-core-fastapi[dev]

# 测试环境安装
pip install neo-core-fastapi[testing]

# 文档环境安装
pip install neo-core-fastapi[docs]
```

## 🔧 快速开始

### 1. 基础配置

```python
from neo_core.config import CoreSettings
from neo_core.database import DatabaseManager
from neo_core.auth import AuthManager

# 配置设置
settings = CoreSettings(
    database_url="postgresql://user:pass@localhost/dbname",
    redis_url="redis://localhost:6379",
    secret_key="your-secret-key"
)

# 初始化数据库
db_manager = DatabaseManager(settings)
await db_manager.initialize()

# 初始化认证
auth_manager = AuthManager(settings)
```

### 2. 使用核心模型

```python
from neo_core.models import User, Role, Permission
from neo_core.services import UserService, RoleService

# 创建用户服务
user_service = UserService(db_session)

# 创建用户
user = await user_service.create_user(
    username="admin",
    email="admin@example.com",
    password="secure_password"
)

# 分配角色
role = await RoleService(db_session).get_role_by_name("admin")
await user_service.assign_role(user.id, role.id)
```

### 3. 使用认证中间件

```python
from fastapi import FastAPI, Depends
from neo_core.middleware import AuthMiddleware
from neo_core.dependencies import get_current_user
from neo_core.models import User

app = FastAPI()

# 添加认证中间件
app.add_middleware(AuthMiddleware)

@app.get("/protected")
async def protected_route(current_user: User = Depends(get_current_user)):
    return {"message": f"Hello, {current_user.username}!"}
```

### 4. 使用权限控制

```python
from neo_core.dependencies import require_permission
from neo_core.models import User

@app.get("/admin-only")
async def admin_only(
    current_user: User = Depends(require_permission("admin.read"))
):
    return {"message": "Admin access granted"}
```

## 📚 核心组件

### 模型层 (Models)

```python
# 用户模型
from neo_core.models import User, Role, Permission, Application

# 用户管理
user = User(
    username="john_doe",
    email="john@example.com",
    is_active=True
)

# 角色权限
role = Role(name="editor", description="Content Editor")
permission = Permission(name="content.edit", description="Edit Content")
```

### 服务层 (Services)

```python
# 基础服务
from neo_core.services import BaseService, UserService, RoleService

# 自定义服务
class CustomService(BaseService[CustomModel]):
    async def custom_method(self, param: str) -> CustomModel:
        # 自定义业务逻辑
        return await self.create({"field": param})
```

### 工具库 (Utils)

```python
# 密码工具
from neo_core.utils.password import hash_password, verify_password

hashed = hash_password("my_password")
is_valid = verify_password("my_password", hashed)

# JWT工具
from neo_core.utils.jwt import create_access_token, decode_token

token = create_access_token(data={"sub": "user_id"})
payload = decode_token(token)

# 验证工具
from neo_core.utils.validators import validate_email, validate_phone

is_valid_email = validate_email("test@example.com")
is_valid_phone = validate_phone("+1234567890")
```

## 🗄️ 数据库管理

### 迁移管理

```bash
# 创建迁移
alembic revision --autogenerate -m "Add new table"

# 应用迁移
alembic upgrade head

# 回滚迁移
alembic downgrade -1
```

### 数据库初始化

```python
from neo_core.database import init_database, create_default_data

# 初始化数据库结构
await init_database()

# 创建默认数据
await create_default_data()
```

## 🔐 安全特性

### 密码安全
- bcrypt加密算法
- 密码强度验证
- 密码历史记录

### JWT认证
- 访问令牌和刷新令牌
- 令牌黑名单机制
- 自动令牌刷新

### 权限控制
- 基于角色的访问控制(RBAC)
- 细粒度权限管理
- 动态权限检查

## 📊 监控和日志

### 结构化日志

```python
from neo_core.logging import get_logger

logger = get_logger(__name__)
logger.info("User logged in", user_id=123, ip="192.168.1.1")
```

### 性能监控

```python
from neo_core.monitoring import track_performance

@track_performance
async def slow_operation():
    # 自动记录执行时间
    pass
```

## 🧪 测试

```bash
# 运行所有测试
pytest

# 运行特定测试
pytest tests/test_auth.py

# 生成覆盖率报告
pytest --cov=neo_core --cov-report=html
```

## 📖 文档

- [API文档](https://neo-core-fastapi.readthedocs.io/)
- [用户指南](docs/user-guide.md)
- [开发指南](docs/development.md)
- [迁移指南](docs/migration.md)

## 🤝 贡献

我们欢迎所有形式的贡献！请查看 [贡献指南](CONTRIBUTING.md) 了解如何参与项目开发。

### 开发环境设置

```bash
# 克隆项目
git clone https://github.com/neo-core/neo-core-fastapi.git
cd neo-core-fastapi

# 安装开发依赖
pip install -e ".[dev]"

# 安装pre-commit钩子
pre-commit install

# 运行测试
pytest
```

## 📄 许可证

MIT License - 详见 [LICENSE](LICENSE) 文件

## 🔗 相关项目

- [FastAPI Dynamic Loader](https://github.com/your-org/fastapi-dynamic-loader) - 使用本库的动态模块加载系统
- [Neo Core CLI](https://github.com/neo-core/neo-core-cli) - 命令行工具

## 📞 支持

如果您遇到问题或有疑问：

1. 查看 [文档](https://neo-core-fastapi.readthedocs.io/)
2. 搜索 [已知问题](https://github.com/neo-core/neo-core-fastapi/issues)
3. 创建新的 [Issue](https://github.com/neo-core/neo-core-fastapi/issues/new)
4. 加入 [讨论](https://github.com/neo-core/neo-core-fastapi/discussions)

---

⭐ 如果这个项目对您有帮助，请给我们一个星标！