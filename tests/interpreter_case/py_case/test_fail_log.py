import allure

@allure.story('fail')
def test_fail():
    assert 1 == 2, '1不等于2'
