import allure

@allure.story('fail')
@allure.title('测试pytest')
def test_fail():
    assert 1 == 2, '1不等于2'
