from enum import Enum


class DataSetTemplateFileFormat(str, Enum):
    JSONL = "jsonl"
    XLSX = "xlsx"

    def __str__(self) -> str:
        return str(self.value)
