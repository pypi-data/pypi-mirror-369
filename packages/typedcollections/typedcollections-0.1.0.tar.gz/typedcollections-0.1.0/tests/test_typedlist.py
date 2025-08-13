import pytest
from typedcollections.typedlist import TypedList
from typedcollections.exceptions import TypedListTypeError

def test_valid_strict_list():
    lst = TypedList(int, [1, 2, 3], strict=True)
    assert lst == [1, 2, 3]

def test_invalid_strict_list():
    with pytest.raises(TypedListTypeError):
        TypedList(int, [1, "two", 3], strict=True)

def test_empty_list():
    lst = TypedList(int, [], strict=True)
    assert lst == []

def test_single_element():
    lst = TypedList(str, ["hello"], strict=True)
    assert lst == ["hello"]

def test_large_list():
    data = list(range(1000))
    lst = TypedList(int, data, strict=True)
    assert lst == data

def test_mixed_types_non_strict():
    lst = TypedList(int, [1, "2", 3], strict=False)
    assert lst == [1, 2, 3]

def test_none_values():
    with pytest.raises(TypedListTypeError):
        TypedList(int, [1, None, 3], strict=True)

def test_nested_typedlist():
    inner = TypedList(int, [1, 2], strict=True)
    outer = TypedList(TypedList, [inner], strict=True)
    assert len(outer) == 1
    assert isinstance(outer[0], TypedList)
