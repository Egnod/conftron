import binascii
from pathlib import Path
from typing import Any

import ujson
from pydantic import BaseModel as PydanticModel
from pydantic import Field

from conftron.sync.enums.target import TargetContentType


class BaseSyncModelConfig:
    validate_assignment = True
    json_loads = ujson.loads
    json_dumps = ujson.dumps


class BaseSyncModel(PydanticModel):
    @classmethod
    def get_field_info(cls, alias=False) -> list[dict[str, Any]]:
        fields_info = []

        for field_name in cls.__fields__.keys():
            fields_info.append(
                {
                    "name": field_name,
                    "type": cls.__fields__[field_name].type_,
                    "default": cls.__fields__[field_name].get_default(),
                }
            )

        return fields_info

    class Config(BaseSyncModelConfig):
        pass


class BaseSyncOptionsModelConfig(BaseSyncModelConfig):
    pass


class BaseSyncOptionsModel(BaseSyncModel):
    class Config(BaseSyncOptionsModelConfig):
        pass


class BaseSyncTargetModelConfig(BaseSyncModelConfig):
    pass


class BaseSyncTargetModel(BaseSyncModel):
    content_type: TargetContentType = Field(default=TargetContentType.text)

    path: Path = Field(...)

    def get_data(self):
        return self.path.read_text()

    def check_local_availability(self):
        return self.path.is_file()

    def get_target_name(self, sep: str = "[__trgt__]"):
        return f"{binascii.hexlify(str(self.path.cwd()).encode()).decode()}{sep}{str(self.path.name)}"

    def dict(self, *args, **kwargs):
        data = super().dict(*args, **kwargs)

        data["path"] = str(self.path)
        data["name"] = self.get_target_name()

        return data

    class Config(BaseSyncTargetModelConfig):
        pass
