import pytest, os, sys, yaml

BASE_DIR = os.path.dirname(os.path.dirname(__file__))
TESTS_DIR = os.path.join(BASE_DIR, 'tests')
sys.path.append(BASE_DIR)

from tests.test import assert_result_config
from yaml_oop.parser import oopify
from yaml_oop.custom_errors import KeySealedError, ConflictingDeclarationError, NoOverrideError, InvalidDeclarationError


def test_variable():
    input_path = os.path.join(TESTS_DIR, 'test_variables/variable', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables/variable', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_multiple_variable():
    input_path = os.path.join(TESTS_DIR, 'test_variables/multiple_variables', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables/multiple_variables', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables/instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables/instantiation', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_multiple_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables/multiple_instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables/multiple_instantiation', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_abstract_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables/abstract_variables', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables/abstract_variables', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)


def test_failed_abstract_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables/failed_abstract_variables', 'sub_config.yaml')
    with pytest.raises(NotImplementedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is NotImplementedError


def test_failed_sealed_variables():
    input_path = os.path.join(TESTS_DIR, 'test_variables/failed_sealed_variables', 'sub_config.yaml')
    with pytest.raises(KeySealedError) as executeInfo:
        oopify(file_path=input_path, directory=TESTS_DIR, Loader=yaml.FullLoader)
    assert executeInfo.type is KeySealedError


def test_nested_instantiation():
    input_path = os.path.join(TESTS_DIR, 'test_variables/nested_instantiation', 'sub_config.yaml')
    expected_path = os.path.join(TESTS_DIR, 'test_variables/nested_instantiation', 'result_config.yaml')
    assert_result_config(input_path, expected_path, TESTS_DIR)
