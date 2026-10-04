import pytest
from pydantic import ValidationError

from app.modules.settings.schemas import ApplicationSettingUpdateRequest


def test_currency_code_requires_three_characters() -> None:
    with pytest.raises(ValidationError):
        ApplicationSettingUpdateRequest(currency_code="ID")


def test_partial_setting_update_is_supported() -> None:
    payload = ApplicationSettingUpdateRequest(application_name="SIMA Budget")
    assert payload.application_name == "SIMA Budget"
    assert payload.timezone is None
