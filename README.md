## 定制统一 restful 响应体
* 遵循 RFC 标准 status code 规范
* 响应体：成功则直接返回 JSON 数据，异常返回`code` `message`

[响应基类](app/libs/response.py)  

**成功的响应**

Response -> flask_restful.Api.output(self, resource)
-> flask_restful.Resource.dispatch_request
-> if isinstance(resp, ResponseBase): 
-> return resp

**失败的响应**

APIException(HTTPException) -> app/libs/flask_restful.Api.handle_error
-> flask_restful.Api.handle_error
-> if isinstance(e, HTTPException): 
-> return resp

同时 handle_error 还处理其他抛出的异常如 equestParser Marshmallow
参数校验异常等，未知异常统一返回 ServiceInternalError

## 登录
采用 HTTPTokenAuth，在 header 中保存 token 的机制

    Authorization: Bearer <token>

获取 token: /v1/auth
[校验 token](./app/libs/token_auth.py)

除获取 token 以外的所有接口每次访问都需要校验 token，其方法是在 flask_restful.Api 中添加
了方法装饰器:

    method_decorators = [auth.login_required]

token 校验通过后，将 token 中的用户信息保存到 g 变量: `g.user = User(uid, role)`
方便在视图中快速访问信息

因为 token 的维护是无状态的，为了实现用户修改密码和注销操作的正确性，需要采用 redis 记录 token，
并在 token 验证过程中加入 redis 键验证

1. 用户 token 校验通过，存储 token 到 redis (token:uid:xxx), 同步设置过期时间
2. 修改密码，让其他登录的 token 都失效 （删除 token:uid:*）
3. 注销登录，让本次登录的 token 失效  (删除当前 token)

为了方便在开发环境调试，配置中做了一个开关：`API_LOGIN_REQUIRED`
等于 False 时，则不对访问的 Api 校验登录有效性

## 权限校验
目前设定了 3 中角色:

* SUPER_ADMIN
* ADMIN
* MEMBER

[verify_auth_token](./app/libs/token_auth.py)
->
[is_allowed](./app/libs/permission_scope.py)

在 token 校验通过后即对当前访问的 api 进行权限校验，通过判断
path 或 blueprint 是否在禁止名单中，来确定是否放行。

* 当需要禁止访问 api 时，可以添加 path 或 blueprint 名单到 `forbidden_set`
* 当需要限定 api 且是指定的 method 时，可以添加 path 名单到 `forbidden_dict`

eg. 

    path: /v1/users/1
    buleprint: v1.users

添加无权限的 path 和 blueprint

    forbidden_set = {'/v1/token/get_token', 'v1.users'}

添加无权限的 path 及指定 method (普通管理员只有查看用户列表权限)

    forbidden_dict = {
            '/v1/users': {'POST', 'PUT', 'DELETE'}
        }


## ORM 模型、序列化与反序列化
这里用到了：

* flask-sqlalchemy          flask 和 sqlalchemy 的接口
* flask-marshmallow         flask 和 marshmallow/marshmallow-sqlalchemy 的接口
* marshmallow-sqlalchemy    marshmallow 和 sqlalchemy 的接口

[base 基类](./app/models/base.py)

* ModelBase(db.Model): 定义了 ORM 模型基类，继承了该基类的模型都有 `create_time` `update_time` 字段
* BaseOpts(SQLAlchemyAutoSchemaOpts): SQLAlchemySchema Meta 类中的选项可以在此设置默认选项
* SQLAlchemyAutoSchema(flask_ma.SQLAlchemyAutoSchema): 继承此类的 Schema 可以自动生成模型需要序列化的字段

## docker 部署
为了各个服务能网络互通，需要先创建一个网络，如网络名：test-fly-network
```bash
docker network create test-fly-network
```
### 部署公共组件（TestFlyDocker 项目中）:

1\. jenkins

* 挂载出容器 jenkins_home 目录到宿主机，方便查看 jenkins 工作空间和保存 jenkins 配置，避免下次 build 时又得重来
* 将宿主机当前目录映射到容器 /docker 目录，方便在 jenkins 管理公共组件
* 将宿主机的 docker 命令、 docker-compose 命令映射到容器，方便在容器中使用
* 将容器中的 8080 端口映射到宿主机 9999，如访问 http://172.22.23.112:9999/ 既可访问 web 管理页面

```yaml
    volumes:
      - ./jenkins/jenkins_home:/var/jenkins_home
      - .:/docker
      - /var/run/docker.sock:/var/run/docker.sock
      - /usr/bin/docker:/usr/bin/docker
      - /usr/local/bin/docker-compose:/usr/local/bin/docker-compose
    ports:
      - "9999:8080"
      - "50000:50000"

```
2\. mysql

* 设置数据库 root 用户密码为 testflyadmin
* 设置默认数据库名称为 test_fly
* 设置普通用户 admin  密码 admin
* 将数据库数据文件目录映射到宿主机，方便增量使用、备份
```yaml
    environment:
      MYSQL_ROOT_PASSWORD: testflyadmin
      MYSQL_DATABASE: test_fly
      MYSQL_USER: admin
      MYSQL_PASSWORD: admin
    volumes:
      - ./mysql/db_data:/var/lib/mysql

```
2\. nginx

* 将 nginx 的配置文件映射出来，方便修改和同步配置

```yaml
    volumes:
      - ./nginx/nginx.conf:/etc/nginx/nginx.conf
      - ./nginx/conf.d:/etc/nginx/conf.d
```

统一使用同一个桥接网络，方便用各个服务的名称作为 host 名称，如可以 ping mysql
```yaml
networks:
  default:
    external:
      name: test-fly-network

```

### 部署后端服务
因为服务部署都是依靠 jenkins 容器的，所以 build 镜像时不能在容器中挂载目录到宿主机，同时也没必要这样做，
所以是将新的代码都放在镜像中

为了统一使用 docker-compose 管理，这里也使用了 docker-compose.yml

```dockerfile
FROM python:3.7
LABEL maintainer="mailmzb@163.com"
ENV TZ="Asia/Shanghai"
ENV FLASK_ENV="production"
WORKDIR /usr/src
RUN pip install uwsgi -i https://pypi.tuna.tsinghua.edu.cn/simple
# 以下两句在 COPY . . 之前主要是为了利用 build 缓存，避免每次都重装 python 依赖
COPY ./requirements.txt ./requirements.txt
RUN pip install -r requirements.txt --timeout 600

COPY . .

CMD uwsgi --ini uwsgi_config.ini --cache-blocksize 0
```




