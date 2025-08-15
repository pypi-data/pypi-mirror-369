import traceback
import sys

class TayloristException(Exception):
    def __init__(self, *args: object, status_code: int, message: str) -> None:
        super().__init__(*args)
        self.status_code = status_code
        self.message = message

        print(f"[TayloristException] {self.message} (status_code={self.status_code})")
        traceback.print_stack()

class TayloristAPIException(Exception):
    def __init__(self, *args: object, status_code: int, message: str) -> None:
        super().__init__(*args)
        self.status_code = status_code
        self.message = message

        print(f"[TayloristAPIException] {self.message} (status_code={self.status_code})")
        traceback.print_stack()
