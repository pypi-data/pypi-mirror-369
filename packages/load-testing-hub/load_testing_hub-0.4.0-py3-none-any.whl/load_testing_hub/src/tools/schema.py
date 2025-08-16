import csv
from typing import Self

import yaml
from pydantic import BaseModel, RootModel, FilePath


class YAMLSchema(BaseModel):
    @classmethod
    def from_yaml(cls, file: FilePath) -> Self:
        data = yaml.safe_load(file.open())
        return cls.model_validate(data)


class JSONSchema(BaseModel):
    @classmethod
    def from_json(cls, file: FilePath) -> Self:
        try:
            content = file.read_text(encoding="utf-8-sig")
        except UnicodeDecodeError:
            content = file.read_text(encoding="utf-16")

        return cls.model_validate_json(content)


class CSVRootSchema(RootModel):
    @classmethod
    def from_csv(cls, file: FilePath) -> Self:
        reader = csv.DictReader(file.open())
        return cls.model_validate(reader)
