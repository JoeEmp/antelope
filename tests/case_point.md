### file / dir

- 不存在文件/目录,提示文件未找到

python3 runner.py xx.yaml

- 文件的冒烟测试

python runner.py tests/interpreter_case/pass/echo/echo_template.yaml -e demo

- py文件的冒烟测试

python3 runner.py tests/interpreter_case/pass/b_test.py -e demo

- 目录的冒烟测试

python runner.py tests/interpreter_case/pass/echo -e demo

- 多层目录的冒烟测试

python runner.py tests/interpreter_case/pass -e demo

- 使用 suite 执行的用例

python3 runner.py -e demo -suite tests/test_suite.yaml

- 优先使用 suite 作为用例

python3 runner.py tests/interpreter_case/pass/b_test.py -e demo -suite tests/test_suite.yaml

### 用例变量

- 冒烟测试

python runner.py tests/interpreter_case/pass

-  带环境变量

python runner.py tests/interpreter_case/pass -e demo

### -g 全局变量

- 指定不存在全局变量文件

python3 runner.py test_case/min_case/min_case_test.yaml -g xx_global.yaml

### -e 环境

- 指定环境

python3 runner.py test_case/min_case/min_case_test.yaml -e test_case

- 指定不存在环境

python3 runner.py test_case/min_case/min_case_test.yaml -e no_env

- 统计

python3 runner.py test_case/min_case/min_case_test.yaml -num

### -level 优先级

- 指定优先级

python3 runner.py test_case/level/level.yaml -level 1

python3 runner.py test_case/level/level.yaml -level 2

- 异常用例优先级的值
  python3 runner.py test_case/min_case/min_case_test.yaml -level abc

- 执行 is_skip 为真的用例
  python3 runner.py test_case/with_skip_value/with_skip_value.yaml -level abc
