import pytest


def test_equal_not_equal():
    assert 3 != 1
    assert 3 == 3


def test_instance():
    assert isinstance('this is a string', str)
    assert not isinstance('10', int)


def test_boolean():
    validate = True
    assert validate is True
    assert ('hello' == 'world') is False


def test_greater_less():
    assert 3 < 7


def test_type():
    assert type('Hello' is str)
    assert type(10 is not str)


def test_num():
    num_list=[1,2,3,4,5]
    any_list=[False,False]
    assert 1 in num_list
    assert 7 not in num_list
    assert all(num_list)
    assert not any(any_list)


class Student:
    def __init__(self, first_name:str, last_name:str, major:str, years:int):
        self.first_name = first_name
        self.last_name = last_name
        self.major = major
        self.years = years


@pytest.fixture
def default_employee():
    return Student('awin','pavan','btech',4)


def test_student(default_employee):
    assert default_employee.first_name == 'awin'
    assert default_employee.last_name == 'pavan'
    assert default_employee.major == 'btech'
    assert default_employee.years == 4
