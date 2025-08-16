import sys

from pydantic import BaseModel, ConfigDict

ALLOW_EXTRA = "allow" if "--allow-extra" in sys.argv else "forbid"


class BaseValidation(BaseModel):
    model_config = ConfigDict(
        arbitrary_types_allowed=True,
        extra=ALLOW_EXTRA,
        use_enum_values=False,
        json_schema_mode_override="serialization",
        validate_assignment=True,
        protected_namespaces=(),
    )

    def __format__(self, format_spec: str) -> str:
        return f"{self!s:{format_spec}}"
