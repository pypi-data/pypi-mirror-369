from enum import auto

from llm_cgr import OptionsEnum


def test_options_enum():
    """
    Test the OptionsEnum class.
    """

    # define class to test the OptionsEnum functionality
    class TestEnum(OptionsEnum):
        ONE = auto()
        TWO = auto()
        THREE = auto()

    # check basic properties
    assert TestEnum.ONE == "one"
    assert str(TestEnum.ONE) == "one"
    assert TestEnum.options() == "one, two, three"
    assert TestEnum.list() == ["one", "two", "three"]

    # check case-insensitive (in)equality
    assert TestEnum.ONE == "One"
    assert TestEnum.ONE == "ONE"
    assert (TestEnum.ONE != "One") is False
    assert (TestEnum.ONE != "ONE") is False

    # check that the enum can be hashed
    test_dict = {TestEnum.TWO: "value"}
    assert test_dict[TestEnum.TWO] == "value"
    assert test_dict["two"] == "value"
    assert {TestEnum.THREE} == {"three"}
