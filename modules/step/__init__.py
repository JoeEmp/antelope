from enum import unique, Enum
from modules.step.set_by_json import SetByJsonStep
from modules.step.step import Step
from modules.step.sql_exec import SqlExecStep
from modules.step.assert_step import AssertEqualStep, AssertListEqualStep, AssertNotEqualStep, AssertInStep, AssertJsonInStep, \
    AssertLenEqualStep, AssertLenNotEqualStep, AssertJsonStep, AssertNotInStep, AssertValueType
from modules.step.case import CaseStep, CaseStepV2
from modules.step.my_function import MyFunctionStep
from modules.step.set import SetStep
from modules.step.request import RequestStep
from modules.step.if_else import IfStep, ElifStep, ElseStep, JudgeStep, BranchStep
from modules.step.echo import EchoStep
from modules.step.sleep_step import SleepStep
from modules.step.templdate_block import TemplateBlockStep

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
    assertListEqual = AssertListEqualStep
    assertJson = AssertJsonStep
    assertNotIn = AssertNotInStep
    assertValueType = AssertValueType
    template = TemplateBlockStep
    case_v2 = CaseStepV2
    set_by_json = SetByJsonStep