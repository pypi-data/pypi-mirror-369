

class Status(str):

    valid = ["pending", "submitted", "running", "completed", "failed"]

    def __init__(self, value: str) -> None:
        if value not in self.valid:
            raise ValueError(f"Invalid status: {value}")
        self.value = value

    @classmethod
    def pending(cls) -> "Status":
        return cls("pending")

    @classmethod
    def submitted(cls) -> "Status":
        return cls("submitted")

    @classmethod
    def running(cls) -> "Status":
        return cls("running")
    
    @classmethod
    def completed(cls) -> "Status":
        return cls("completed")

    @classmethod
    def failed(cls) -> "Status":
        return cls("failed")
    
    def __eq__(self, other: "Status") -> bool:
        if isinstance(other, str):
            return self.value == other
        return self.value == other.value

class Pending(Status):
    def __init__(self) -> None:
        super().__init__("pending")

class Submitted(Status):
    def __init__(self) -> None:
        super().__init__("submitted")

class Running(Status):
    def __init__(self) -> None:
        super().__init__("running")

class Completed(Status):
    def __init__(self) -> None:
        super().__init__("completed")

class Failed(Status):
    def __init__(self) -> None:
        super().__init__("failed")

if __name__ == '__main__':

    status = Status.failed()

    bools = "pending" in [Pending()]
    print(bools)


