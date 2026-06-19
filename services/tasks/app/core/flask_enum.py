from enum import Enum


class FlaskEnum(Enum):
    @property
    def label(self) -> str:
        return self.value[1]

    @property
    def db_value(self) -> str:
        return self.value[0]
