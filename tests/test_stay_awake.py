import uuid

from pytest import raises, fixture

from eugeroic import stay_awake

@fixture
def unique_reason():
    return uuid.uuid4().hex


def test_stay_awake_positive_entry(caplog, unique_reason):
    @stay_awake(reason=unique_reason)
    def decorated_function():
        pass

    decorated_function()
    assert f"Entering wakefulness state during: {unique_reason!r}" in caplog.text


def test_stay_awake_negative_entry(caplog, unique_reason):

    @stay_awake(reason=unique_reason)
    def decorated_function():
        pass

    assert f"Entering wakefulness state during: {unique_reason!r}" not in caplog.text
    # decorated_function() is never called so the entry message is not logged


def test_stay_awake_positive_exit(caplog, unique_reason):

    @stay_awake(reason=unique_reason)
    def decorated_function():
        pass

    decorated_function()
    assert f"Exiting wakefulness state after: {unique_reason!r}" in caplog.text


def test_stay_awake_negative_exit(caplog, unique_reason):

    @stay_awake(reason=unique_reason)
    def decorated_function():
        pass

    assert f"Exiting wakefulness state after: {unique_reason!r}" not in caplog.text
    # decorated_function() is never called so the exit message is not logged


def test_exit_logged_for_exceptional_exit(caplog, unique_reason):

    @stay_awake(reason=unique_reason)
    def decorated_function():
        raise Exception('Something went wrong')

    try:
        decorated_function()
    except Exception:
        pass
    assert f"Exiting wakefulness state after: {unique_reason!r}" in caplog.text


def test_stay_awake_extracts_first_line_of_docstring_as_reason(caplog):

    @stay_awake()
    def decorated_function():
        """This is the first line of the docstring.

        Subsequent lines are ignored.
        """
        pass

    decorated_function()
    assert "Entering wakefulness state during: 'This is the first line of the docstring.'" in caplog.text


def test_stay_awake_uses_function_name_as_reason_if_no_docstring(caplog):

    @stay_awake()
    def decorated_function():
        pass

    decorated_function()
    assert "Entering wakefulness state during: 'decorated_function'" in caplog.text


def test_stay_awake_can_be_used_without_arguments(caplog):

    @stay_awake
    def decorated_function():
        pass

    decorated_function()
    assert "Entering wakefulness state during: 'decorated_function'" in caplog.text


def test_stay_awake_can_be_used_with_positional_argument(caplog, unique_reason):

    @stay_awake(unique_reason)
    def decorated_function():
        pass

    decorated_function()
    assert f"Entering wakefulness state during: {unique_reason!r}" in caplog.text


def test_stay_away_with_both_positional_and_keyword_argument_raises_type_error():

    with raises(TypeError, match=(
        "Cannot specify 'reason' as both a positional argument and "
        "a keyword argument to stay_awake."
    )):
        @stay_awake("reason", reason="another reason")
        def decorated_function():
            pass
