from enum import unique, Enum
from modules.step.step import Step
from modules.step.sql_exec import SqlExecStep
from modules.step.assert_step import AssertEqualStep, AssertListEqualStep, AssertNotEqualStep, AssertInStep, AssertJsonInStep, \
    AssertLenEqualStep, AssertLenNotEqualStep, AssertJsonStep, AssertNotInStep, AssertValueType
from modules.step.case import CaseStep
from modules.step.my_function import MyFunctionStep
from modules.step.set import SetStep
from modules.step.request import RequestStep
from modules.step.if_else import IfStep, ElifStep, ElseStep, JudgeStep, BranchStep
from modules.step.echo import EchoStep
from modules.step.sleep_step import SleepStep
from modules.step.oss_step import OssStep

@unique
class STEP_TYPE(Enum):
    # 支持的步骤 断言为驼峰命名，其他步骤名字为下划线
    sql_exec = SqlExecStep
    assertEqual = AssertEqualStep
    set_step = SetStep
    assertNotEqual = AssertNotEqualStep
    case = CaseStep
    func = MyFunctionStep
    request = RequestStep
    assertIn = AssertInStep
    assertJsonSchema = AssertJsonInStep
    judge = JudgeStep
    if_step = IfStep
    else_step = ElseStep
    elif_step = ElifStep
    assertLenEqual = AssertLenEqualStep
    assertLenNotEqual = AssertLenNotEqualStep
    echo = EchoStep
    sleep = SleepStep
    oss_upload = OssStep
    assertListEqual = AssertListEqualStep
    assertJson = AssertJsonStep
    assertNotIn = AssertNotInStep
    assertValueType = AssertValueType
