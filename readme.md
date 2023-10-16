### 设计文档


[加入知识库](https://www.yuque.com/g/furnace/to7lba/collaborator/join?token=z491mBSt4Iyk4fhP#),进入后见[原型和功能](https://www.yuque.com/furnace/to7lba/cmgoyr)设计文档

### 初始化环境

类 unix 用户

```bash
mkdir log
mkdir report
mkdir suite
python3 -m venv venv
source venv/bin/activate
pip3 install -r requirements.txt
```

win 用户

```bat
mkdir log
mkdir report
mkdir suite
python -m venv venv
venv\Scripts\activate.bat
pip install -r requirements.txt
```

### 使用

```
# 初始化全局变量和邮箱配置，方便我们将用例放在该目录下
python3 init_project_conf.py ipc test

# 使用自动生成模板脚本

python3 cli.py gt hello_world

# 编写自动化脚本

...

# 运行

python3 runner test_case/hello_world -e demo

```

使用例子在 demo_case ,可以直接运行了解运行

### 开发

```

# 尝试使用 coverage 测试自己开发的内容，保证测试的覆盖率

coverage run runner.py tests/interpreter_case -e demo

# 输出报告, -d 指定生成文件夹名

coverage html -d report/demo_html

# 回归测试

# interpreter_case 为解释配置文件的用例

# module 为框架能力的测试用例

python3 runner.py tests -e demo -debug

```
### 贡献者

感谢协作开发者：关瑷健、邹业成、黄剑莲