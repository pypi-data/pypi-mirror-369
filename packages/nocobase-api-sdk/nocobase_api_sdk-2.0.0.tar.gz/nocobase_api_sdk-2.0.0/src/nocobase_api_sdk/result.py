from dataclasses import dataclass, field


@dataclass
class ErrorResult:
    message: str = None
    errors: list[dict] = field(default_factory=list)

    def __post_init__(self):
        if isinstance(self.errors, list) and len(self.errors) > 0:
            self.message = self.errors[0].get('message')


@dataclass
class SuccessResult:
    data: dict | list[dict] | int = None


@dataclass
class SelectResult(SuccessResult):
    meta: dict = None
    count: int = None
    page: int = None
    pageSize: int = None
    totalPage: int = None

    def __post_init__(self):
        if isinstance(self.meta, dict):
            for k, v in self.meta.items():
                setattr(self, k, v)


@dataclass
class GetResult(SuccessResult):
    pass


@dataclass
class UpdateResult(SuccessResult):
    pass


@dataclass
class DestroyResult(SuccessResult):
    pass


@dataclass
class CreateResult(SuccessResult):
    pass
