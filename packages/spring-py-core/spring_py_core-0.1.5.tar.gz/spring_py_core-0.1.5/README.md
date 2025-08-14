# Spring-Py

一个类似Spring Framework的Python依赖注入框架，提供了现代化的IoC容器和组件管理功能。

## 特性

- 🚀 **类Spring注解** - 支持 `@Component`, `@Configuration`, `@Bean`, `@Autowired` 等注解
- 🔧 **依赖注入** - 自动化的组件依赖管理和注入
- 📦 **组件扫描** - 自动发现并注册标记的组件
- 🌐 **全局上下文** - 单例应用上下文，无需手动传递
- 🛠️ **Bean工厂** - 支持通过 `@Bean` 方法创建复杂对象
- 📝 **类型安全** - 完整的类型注解支持
- 🏗️ **项目脚手架** - 内置CLI工具快速生成项目模板

## 安装

```bash
pip install spring-py-core
```

## 项目地址
https://github.com/mahoushoujyo-eee/spring-py

## 快速开始

### 1. 基本组件定义

```python
from spring_py import Component, Autowired

@Component
class UserService:
    def get_user(self, user_id: int):
        return {"id": user_id, "name": "Alice"}

@Component
class OrderService:
    user_service: UserService = Autowired()
    
    def create_order(self, user_id: int):
        user = self.user_service.get_user(user_id)
        return {"order_id": 123, "user": user}
```

### 2. 应用启动

```python
from spring_py import SpringBootApplication, get_bean

@SpringBootApplication()
class Application:
    pass

def main():
    # 启动应用上下文
    app = Application()
    context = app.run()
    
    # 获取并使用服务
    order_service = get_bean(OrderService)
    order = order_service.create_order(1)
    print(order)

if __name__ == "__main__":
    main()
```

### 3. 运行结果

```
🚀 Starting Spring-Py application...
📦 Scanning packages: ['/path/to/your/app']
--- 扫描组件 ---
Scanned 2 components:
  - UserService (main)
  - OrderService (main)
✓ GlobalContext initialized with 2 components
✅ Application started successfully!

{'order_id': 123, 'user': {'id': 1, 'name': 'Alice'}}
```

## 核心概念

### 组件注解

#### @Component
标记一个类为Spring组件，会被自动扫描和注册：

```python
@Component
class MyService:
    def do_something(self):
        return "Hello from MyService"
```

#### @Service
`@Component` 的语义化别名，用于服务层：

```python
from spring_py import Service

@Service
class BusinessService:
    def process_business_logic(self):
        return "Processing..."
```

#### @Configuration
标记配置类，通常包含 `@Bean` 方法：

```python
from spring_py import Configuration, Bean

@Configuration
class AppConfig:
    @Bean
    def database_connection(self):
        return DatabaseConnection("localhost:5432")
```

### 依赖注入

#### @Autowired
自动注入依赖的组件：

```python
@Component
class UserController:
    user_service: UserService = Autowired()
    email_service: EmailService = Autowired()
    
    def register_user(self, username: str):
        user = self.user_service.create_user(username)
        self.email_service.send_welcome_email(user)
        return user
```

#### 按类型注入

```python
# 直接按类型获取
user_service = get_bean(UserService)
```

#### 按名称注入

```python
# 按组件名称获取（类名小写）
user_service = get_bean("userservice")
```

### Bean工厂方法

使用 `@Bean` 注解创建复杂对象：

```python
@Configuration
class DatabaseConfig:
    
    @Bean
    def database_connection(self):
        return DatabaseConnection(
            host="localhost",
            port=5432,
            database="myapp"
        )
    
    @Bean
    def redis_client(self):
        return Redis(host="localhost", port=6379)

# 使用Bean
@Component
class DataService:
    db: DatabaseConnection = Autowired()
    cache: Redis = Autowired()
```

### 全局上下文

无需手动传递ApplicationContext，在任何地方都可以获取Bean：

```python
from spring_py import get_bean

def some_utility_function():
    # 在任何地方都可以获取Bean
    user_service = get_bean(UserService)
    return user_service.get_user_count()
```

## Web应用集成

Spring-Py与FastAPI完美集成：

```python
from spring_py import Component, Autowired, SpringBootApplication, get_bean
from fastapi import FastAPI, APIRouter
import uvicorn

@Component
class UserService:
    def get_all_users(self):
        return [{"id": 1, "name": "Alice"}, {"id": 2, "name": "Bob"}]

@Component
class UserController:
    user_service: UserService = Autowired()
    
    def setup_routes(self) -> APIRouter:
        router = APIRouter(prefix="/api/users")
        
        @router.get("/")
        async def get_users():
            return self.user_service.get_all_users()
        
        return router

@SpringBootApplication()
class WebApplication:
    def create_app(self) -> FastAPI:
        app = FastAPI(title="Spring-Py Web App")
        
        # 注册路由
        controller = get_bean(UserController)
        app.include_router(controller.setup_routes())
        
        return app

def main():
    app = WebApplication()
    context = app.run()
    
    fastapi_app = app.create_app()
    uvicorn.run(fastapi_app, host="0.0.0.0", port=8000)

if __name__ == "__main__":
    main()
```

## CLI工具

Spring-Py提供了项目脚手架工具：

### 创建新项目

```bash
# 创建Web应用项目
spring-py create my-web-app

# 查看可用模板
spring-py templates

# 查看版本
spring-py version
```

### 生成的项目结构

```
my-web-app/
├── src/
│   ├── main/
│   │   ├── application.py      # 应用主入口
│   │   ├── controller/         # 控制器层
│   │   ├── service/           # 服务层
│   │   ├── model/             # 数据模型
│   │   └── param/             # 参数定义
│   └── test/                  # 测试代码
├── pyproject.toml            # 项目配置
├── README.md                 # 项目文档
├── .gitignore               # Git忽略文件
└── .env.example             # 环境变量示例
```

### 运行生成的项目

```bash
cd my-web-app
pip install -e .
python src/main/application.py
```

项目会启动一个FastAPI服务器，包含：
- **API文档**: http://localhost:8000/docs
- **健康检查**: http://localhost:8000/health
- **用户API**: http://localhost:8000/api/users/

## 高级用法

### 条件Bean注册

```python
@Configuration
class ConditionalConfig:
    
    @Bean
    def development_service(self):
        if os.getenv("ENV") == "dev":
            return DevelopmentService()
        return ProductionService()
```

### Bean作用域

```python
@Component
class SingletonService:
    """默认单例作用域"""
    pass

# 获取的总是同一个实例
service1 = get_bean(SingletonService)
service2 = get_bean(SingletonService)
assert service1 is service2  # True
```

### 多环境配置

```python
@Configuration
class DatabaseConfig:
    
    @Bean
    def database_url(self):
        env = os.getenv("ENV", "dev")
        if env == "prod":
            return "postgresql://prod-server:5432/myapp"
        else:
            return "sqlite:///./dev.db"
```

## 最佳实践

### 1. 项目结构

```
your-app/
├── src/main/
│   ├── controller/     # Web控制器
│   ├── service/       # 业务逻辑服务
│   ├── repository/    # 数据访问层
│   ├── model/         # 数据模型
│   ├── config/        # 配置类
│   └── application.py # 应用入口
```

### 2. 分层架构

```python
# 控制器层
@Component
class UserController:
    user_service: UserService = Autowired()

# 服务层
@Service
class UserService:
    user_repository: UserRepository = Autowired()

# 数据访问层
@Component
class UserRepository:
    database: Database = Autowired()
```

### 3. 配置管理

```python
@Configuration
class AppConfiguration:
    
    @Bean
    def app_settings(self):
        return AppSettings(
            database_url=os.getenv("DATABASE_URL"),
            redis_url=os.getenv("REDIS_URL"),
            secret_key=os.getenv("SECRET_KEY")
        )
```

## API参考

### 装饰器

- `@Component` - 标记组件类
- `@Service` - 标记服务类（@Component别名）
- `@Configuration` - 标记配置类
- `@Bean` - 标记Bean工厂方法
- `@Autowired()` - 标记自动注入字段
- `@SpringBootApplication()` - 标记应用主类

### 函数

- `get_bean(cls_or_name)` - 获取Bean实例
- `get_context()` - 获取应用上下文
- `initialize_context(packages)` - 初始化上下文
- `is_context_initialized()` - 检查上下文是否已初始化

### 类

- `ApplicationContext` - 应用上下文
- `Container` - IoC容器
- `ComponentScanner` - 组件扫描器

## 示例项目

查看 [examples](examples/) 目录中的完整示例：

- [基础Web应用](examples/web-app/) - FastAPI + Spring-Py
- [微服务示例](examples/microservice/) - 多服务架构
- [数据库集成](examples/database/) - SQLAlchemy集成

## 开发

### 环境设置

```bash
git clone https://github.com/spring-py/spring-py.git
cd spring-py
uv sync
```

### 运行测试

```bash
uv run pytest tests/
```

### 构建

```bash
uv build
```

## 贡献

欢迎贡献代码！请查看 [CONTRIBUTING.md](CONTRIBUTING.md) 了解详细信息。

## 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情。

## 更新日志

### v0.1.0

- ✅ 基本的IoC容器功能
- ✅ 组件扫描和注册
- ✅ 依赖注入支持
- ✅ @Bean工厂方法
- ✅ 全局上下文管理
- ✅ CLI项目生成工具
- ✅ FastAPI集成支持

### v0.1.3
- ✅ 修复部分因名称导致的问题

### v0.1.4
- ✅ 完善启动模板，增强与fastapi的整合

## 社区

- **GitHub**: https://github.com/spring-py/spring-py
- **文档**: https://spring-py.readthedocs.io
- **讨论**: https://github.com/spring-py/spring-py/discussions
- **问题反馈**: https://github.com/spring-py/spring-py/issues

---

**Spring-Py** - 让Python开发像Spring一样简单! 🚀
