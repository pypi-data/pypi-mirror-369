# 1. 文档说明

本文档主要用于接口自动化测试框架说明以及使用。
0.0.1 版本为通用版本。
0.0.1a1版本为特殊版本，勿用。a1版本主要解决上传文件接口中有的key定义为files的情况。

## 1.1 环境准备

* IDE：Pycharm 等;
* Python 3.7以上;
* 引用类库，dg-itest; 命令：`pip install dg-itest`
* allure 本地环境配置  

    **step 1** pip install allure-pytest  
    **step 2** 下载Allure版本：[Download](https://github.com/allure-framework/allure2/releases) 并配置到PATH路径下
        对应家目录下，`.bash_profile` 配置如下：  
    
        # Setting PATH for Python 3.9
        # The original version is saved in .bash_profile.pysave
        PATH="/Library/Frameworks/Python.framework/Versions/3.9/bin:${PATH}"
        export PATH
        
        # Setting ALLURE PATH for ALLURE
        export ALLURE=/Users/yaitzayoung/Downloads/Lib/allure-2.7.0/bin
        export PATH=$PATH:$ALLURE
    **step 3** allure(依赖jdk环境1.8+) [Download](https://www.oracle.com/java/technologies/javase-jdk16-downloads.html)

# 2. 目录结构

    ├── dg-itest
    │   ├── test_res     #测试用资源文件夹，需要上传文件时，对应文件归档至该目录
    │   ├── test_report  #测试报告生成目录，系统自动生成
    │   └── test_src     #测试用例归档目录，测试用例文件归档目录


## 2.1 test_res: 测试用资源文件夹  

    说明：测试资源文件归档至该目录下；例如：相关上传文件等。

## 2.5 test_src: 测试用例归档目录 

    说明：测试用例归档目录，针对不同的测试方案归档至相应目录，测试场景建议新建对应的测试类对应或者文件夹。目前支持.yml,.xls,.xlsx,.py文件类型的测试用例。

## 2.6 test_report: 测试报告生成目录

    说明：测试报告生成目录。

# 3. 测试执行

测试执行入口为main.py；运行main.py文件即可。对应测试用例选取执行根据用例标记来进行区分。

# 4. 用例设计
## 4.1 用例以py文件设计
* 一个测试套原则上为一个`python`类(对应一个py文件)，一个测试套包含多个测试用例.
* 测试用例再设计的时候，加上对应的中文描述，如下：
```python
@allure.suite('任务增删改查')          # 注释对应的测试类的中文描述
class TestTask01:
    @allure.testcase('任务创建及删除')     # 注释对应的测试方法的中文描述
    @allure.feature('任务操作')           # 注释其对应的特性，可有可无
    @pytest.mark.smoke                   # 标记对用测试用例的优先级别。 默认级别：Blocker(该用例执行失败，会造成中断缺陷), Critical(该用例执行失败，会造成临界缺陷，即功能点缺失), Normal(该用例执行失败，会造成普通缺陷), Minor(该用例执行失败，会造成次要缺陷), Trivial(该用例执行失败，会造成轻微缺陷)
    def test_create_and_delete(self, api, task_create_and_delete):
        """
        验证任务创建
        """
        with allure.step('任务创建'):         # 代码内为with，在方法则为@allure.step('任务创建')
          task_id, task_name = task_create_and_delete
          assert int(task_id), '任务创建验证'
        
        with allure.step('任务删除'):
          result_delete = api.task_delete(task_id=task_id)
          assert result_delete.status_code == 200
```

## 4.2 用例以yaml文件设计  
* 一个yml文件，文件命名规则(testXXXX.yml 或 testXXXX.yaml)，可以包含一个或多个测试用例验证.
* 测试用例设计模板如下：
```yaml
- test:
    name: 登录接口                            # 接口用例名称
    request:
      url: api/login                         # 接口请求url
      method: post                           # 接口请求类型        
      params: { "json": {"username":"auto_test","password":"auto_test"}}   #接口请求入参
    validate:
      - eq: $.status                         # 接口验证结果
      - eq: $.code                           # 接口验证结果
      - sa: { "token": "$.data.accessToken"} # 将会把本次请求的值存在$token$中，后续需要直接在params中传人$token$,会自动替换
      - co: $.data.accessToken               # 将会通过获取对应的值，判断是否包含或被包含于expect.json.contains中的值
      - wa: 5                                # 接口请求后，等待时间，单位秒(s)
      - js: {"$schema":"http://json-schema.org/draft-07/schema#","type":"object","properties":{"status":{"type":"string"},"message":{"type":"string"},"data":{"type":"object","properties":{"accessToken":{"type":"string"},"refreshToken":{"type":"string"},"isInUse":{"type":"boolean"}},"additionalProperties":false,"required":["accessToken","refreshToken","isInUse"]},"total":{"type":"integer"}},"additionalProperties":false,"required":["status","message","data","total"]}  #接口请求后，校验接口返回json数据结构
    expect:
      json: { "code": 2000000, "status": 200, "contains": "Bearer" }
- test:
    name: 查询接口
    request:
      url: api/list
      method: post
      params: { "json": {"start": 0,"number": 10}, 
                "headers": { "Content-Type": "application/json", "Authorization": "Bearer $token$"}}
    validate:
      - eq: $.status                         # 接口验证结果
      - eq: $.code                           # 接口验证结果
    expect:
      json: { "code": 2000000, "status": 200 }
- test:
    name: 上传接口
    request:
      url: api/upload
      method: get
      params: { "data": {"start": 0,"number": 10}, 
                "headers": { "Content-Type": "application/json"}, 
                "files": ["test1.pdf", "test2.xlsx"]}   
      # 系统会自动根据files下的文件名到resource目录下查找对应文件封装后上传，文件不要重名
    validate:
      - eq: $.status                         # 接口验证结果
      - eq: $.code                           # 接口验证结果
      - sa: $.data.id                        # 存储上传文件的返回ID
    expect:
      json: { "code": 2000000, "status": 200 }
```
* 支持断言关键字：
  - eq：将根据请求按照路径获取的值与expect进行判等。
  - sa：将把请求得到的值按照路径获取并以对应$key$存储以供后续使用； convert字段，将保存的值按照提供的方法进行转化。
  - co: 将根据请求按照路径获取的值与expect进行包含判断。
  - wa: 将接口调用后需要等待的时间，单位秒。
  - inn: 将根据请求按照路径获取的值进行非空判断。
  - js: 输入对应response的json schema数据结构，对返回进行数据结构校验。

## 4.3 用例以xls，xlsx文件进行设计
* 一个xls, xlsx文件，文件命名规则(testXXXX.xls 或 testXXXX.xlsx)，可以包含一个或多个测试用例验证.
* 测试用例设计模板如下：

 
| no  | nam  | url       | method | params                                                     | validate           | validate         | validate                                | expect                                                              | status |
|-----|------|-----------|--------|------------------------------------------------------------|--------------------|------------------|-----------------------------------------|---------------------------------------------------------------------|--------|
| 1   | 登录接口 | api/login | post   | { "json": {"username":"auto_test","password":"auto_test"}} | {"eq": "$.status"} | {"eq": "$.code"} | {"sa": {"token": "$.data.accessToken"}} | { "json": { "code": 2000000, "status": 200 } }                      | 1      |
| 2   | 文件列表 | api/list  | post   | { "json": {"start":0,"limit":10}, "headers": { "Authorization": "Bearer $accessToken$" }}| {"eq": "$.status"} | {"co": {"$.data"}}       | {"sa": {"items": "$.data.items"}, "convert": "json.dumps"} | { "json": { "code": 2000000, "status": 200 }, "contains": "total" } | 1      |

* 支持断言关键字：
  - eq：将根据请求按照路径获取的值与expect进行判等
  - sa：将把请求得到的值按照路径获取并以对应$key$存储以供后续使用。


# 5. py打包详情

## 5.1 安装打包工具
```bash
pip3 install whell  -y
pip3 install twine -y
```

## 5.2 打包
```bash 
python3 setup.py bdist_wheel
```
## 5.3 项目结构
```bash
.
├── README.md
├── dg_itest
│   ├── __init__.py
│   ├── servers
│   │   ├── __init__.py
│   │   ├── dg_servers    # 封装基于requests的http请求
│   │   ├── file_handler  # 封装各类文件用例的解析
│   │   └── test_handler  # 具体用例执行的操作
│   └── utils  # 公用方法归档
│       ├── __init__.py
│       ├── cache.py
│       ├── conftest.py
│       ├── diff_helper.py
│       ├── env_generater.py
│       ├── logger.py
│       ├── replace.py
│       └── string_helper.py
├── publish.sh
├── requirements.txt
└── setup.py
```

## 5.4 上传pypi
```bash
twine upload dist/*
```


# 6. 参考文档
- [1] [pytest](https://www.osgeo.cn/pytest/contents.html) - https://www.osgeo.cn/pytest/contents.html
- [2] [allure en](https://docs.qameta.io/allure/) - https://docs.qameta.io/allure/
