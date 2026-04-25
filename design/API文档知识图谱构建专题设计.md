# API文档知识图谱构建专题设计

> GraphIt 项目子文档 | 研究日期: 2026-04-24

## 一、API文档平台分类与提取策略

### 1.1 平台类型谱系

API文档平台按机器可读性分为三个层级：

**结构化平台**（直接解析，零LLM成本）：Swagger UI通过`/swagger.json`、`/openapi.json`等端点暴露规范；Redoc在HTML内嵌`<script type="application/json">`标签存储Spec；Stoplight Elements基于OpenAPI规范运行；Postman Collection可导出JSON格式。发现隐藏Spec的方法包括：检查`/v2/api-docs`、`/v3/api-docs`、`/swagger-resources`等常见路径。

**半结构化平台**（平台API获取）：ReadMe支持通过`/docs`端点获取规范；GitBook提供导出能力；Apiary/Dredd集成OpenAPI验证。

**非结构化平台**（需HTML解析或LLM）：Slate/Sourcegraph生成纯Markdown/HTML渲染；Docusaurus文档需获取源码而非仅HTML输出；自定义HTML文档站点缺乏统一规范。

### 1.2 提取策略选择

当存在OpenAPI规范时，解析器应按优先级尝试：JSON端点获取原始规范；YAML端点获取规范；规范内嵌位置检测（Redoc的`<redoc spec-url>`属性或内嵌脚本标签）；规范URL发现（基于HTML元标签或已知平台特征）。

对于HTML文档页面，推荐降级策略链：Trafilatura正文提取→readability-lxml清理→Playwright无头浏览器渲染JS页面→LLM辅助解析缺失内容。

## 二、OpenAPI 3.x规范结构到知识图谱的映射

### 2.1 核心实体类型

| 实体类型 | 对应OpenAPI对象 | 说明 |
|---------|---------------|------|
| API服务 | OpenAPI根对象 | 整体API服务入口，包含元数据 |
| 服务器 | ServerObject | 基础URL环境（生产/测试/开发） |
| 路径模板 | Pathtemplat | URL路径模板如`/users/{id}` |
| 操作方法 | Operation | HTTP方法（GET/POST/PUT/DELETE/PATCH等） |
| 参数 | Parameter | 路径/查询/头部/Cookie参数 |
| 请求体 | RequestBody | 操作输入结构 |
| 响应 | APIResponse | HTTP状态码到响应体的映射 |
| 媒体类型 | MediaType | Content-Type到Schema的映射 |
| Schema定义 | Schema | 数据模型（类型系统） |
| 字段 | SchemaProperty | 对象属性及验证规则 |
| 安全方案 | SecurityScheme | API密钥/OAuth2/JWT等认证方式 |
| 标签分组 | Tag | 操作分类标记 |
| 文档链接 | ExternalDocs | 外部文档URL引用 |
| Webhook定义 | PathItem（webhooks字段） | 异步事件入口 |

### 2.2 核心关系类型

```
API服务
├── HAS_SERVER → 服务器
├── HAS_PATH → 路径模板
├── HAS_TAG → 标签
├── DEFINES_SECURITY → 安全方案
└── OWNS_OPERATION → 操作方法（通过路径关联）
    │
    ├── 操作 → HAS_PARAMETER → 参数
    ├── 操作 → REQUIRES_AUTH → 安全方案
    ├── 操作 → ACCEPTS → 请求体
    ├── 操作 → RETURNS → 响应
    ├── 操作 → TAGGED_WITH → 标签
    ├── 操作 → LINKS_TO → 操作（Link对象跨操作关联）
    └── 操作 → DEFINES_CALLBACK → 回调定义

路径模板 → MATCHES_OPERATION → 操作（通过路径模板+方法定位）

服务器 → HOLDS_VARIABLE → 服务器变量

参数 → REFERENCES → Schema（通过schema属性）
请求体 → CONTAINS_MEDIA → 媒体类型
媒体类型 → DEFINES_SCHEMA → Schema

响应 → STATUS_CODE → HTTP状态码（响应字典的键）
响应 → PROVIDES → 媒体类型

Schema → CONTAINS_PROPERTY → 字段
Schema → IMPLEMENTS协议/扩展协议
Schema → EXTENDS → Schema（allOf引用链）
Schema → ALTERNATIVE → Schema（oneOf/anyOf分支）
Schema → HAS_ENUM → 枚举值
Schema → DISCRIMINATES_BY → 鉴别器字段

字段 → TYPED_AS → 数据类型（string/integer/object等）
字段 → CONSTRained_BY → 约束（minimum/maxLength/pattern等）
```

### 2.3 $ref引用的图表示

内部引用`#/components/schemas/User`映射为关系`REFERENCES → Schema{name:'User'}`，外部引用`./shared.yaml#/components/schemas/Address`映射为`REFERENCES → ExternalResource{url:'./shared.yaml'}`后连接到`Schema{name:'Address'}`。引用节点可选择保留或透明展开，推荐保留以维持来源可追溯性。

### 2.4 组合模式的图表示

OpenAPI 3.1的`allOf`（继承组合）、`oneOf`（排他联合）、`anyOf`（可选联合）映射为子Schema节点上的关系边。allOf继承链通过`EXTENDS`边表示，多态鉴别通过`DISCRIMINATES`关系和鉴别器属性字段追踪。

## 三、GraphQL Schema的图谱映射

### 3.1 核心实体

GraphQL Schema解析为：GraphQL服务节点连接到Query根操作类型；Query类型包含查询字段作为子实体；Mutation类型包含变更操作；Subscription类型包含实时订阅；ObjectType/InputType/Enum/Scalar/Interface/Union各有对应节点。

### 3.2 字段关系建模

字段级联建模：字段→ARGUMENTS→输入值；字段→RETURNS→类型引用；字段→IMPLEMENTS→接口；接口→IMPLEMENTED_BY→实现对象。

GraphQL内省查询`__schema`、`__type`可直接程序化获取结构。

## 四、gRPC Proto文件的图谱映射

Proto文件通过 protoc编译导出FileDescriptorSet后解析为：ProtoFile包节点连接Service包；Service节点包含RpcMethod方法节点；Message/Enum节点包含字段和值定义。

## 五、增量更新策略

文档变更通过HTTP HEAD请求比对ETag/Last-Modified或完整内容SHA256哈希检测。增量同步包括新增路径方法处理为CREATE操作；参数Schema变更为UPDATE+关系重建；废弃标记操作为SET deprecated=True而非物理删除；删除操作标记墓碑（valid_to时间戳）后软删除。

版本化策略为每次变更记录时间戳；支持按时间点查询历史状态；提供版本diff能力展示变更详情。

## 六、检索与问答能力

### 6.1 自然语言查询示例

"UserService有哪些接口？"转换为图查询MATCH (t:Tag{name:'UserService'})<-[:TAGGED_WITH]-(o:Operation) RETURN o.operationId, o.method, o.summary。

"createUser方法的完整请求体Schema是什么？"遵循MATCH (o:Operation{operationId:'createUser'})-[:ACCEPTS]->(rb:RequestBody)-[:CONTAINS_MEDIA]->(mt:MediaType)-[:DEFINES_SCHEMA]->(s:Schema) OPTIONAL MATCH (s)-[:CONTAINS_PROPERTY*]->(p:SchemaProperty) RETURN s, collect(p)。

"哪些接口需要OAuth认证？"遵循MATCH (o:Operation)-[:REQUIRES_AUTH|SECURED_BY]->(ss:SecurityScheme{type:'oauth2'}) RETURN o.operationId, o.summary, ss.scheme。

### 6.2 跨端点影响分析

变更影响分析通过Schema变更传播建模实现。变更检测Schema节点set updated_at=now()；匹配涉及变更Schema的所有边操作；聚合受影响操作列表。

## 七、参考工具链

prance处理OpenAPI 2.0/3.0解析和$ref递归解析；openapi-core提供验证和解组；openapi-schema-validator处理Schema验证；datamodel-code-generator生成Pydantic模型。

## 八、总结

API文档构建知识图谱的核心是理解API规范的结构化本质——路径模板、操作、参数、Schema形成了一个具有丰富关系的网络，天然适合用图来表示。
