from pydantic import BaseModel

from gitlib.common.enums import DiffLineType


class DiffLine(BaseModel):
    type: DiffLineType
    lineno: int
    content: str
    skip: bool = False

    @property
    def start_col(self):
        # TODO: This is a temporary solution. Need to find a better way to calculate the start column
        line_with_spaces = self.content.expandtabs(4)
        return (len(line_with_spaces) - len(line_with_spaces.lstrip())) + 1

    @property
    def end_col(self):
        return len(self.content.rstrip()) - 1

    def __str__(self):
        return f"{self.lineno} {self.type.value} {self.content}"
