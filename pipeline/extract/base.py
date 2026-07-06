# Abstract base class for all source readers. Why an ABC and not a Protocol or
# a simple function?
#
# 1. ABC enforces the contract at instantiation time, not just at call time.
#    If you subclass SourceReader without implementing read(), you get an error
#    when you try to instantiate — not when you call a missing method at runtime.
# 2. The `source_type` property lets the pipeline identify what kind of source
#    produced each record without isinstance checks — which is an anti-pattern
#    that violates Open/Closed principle.
# 3. The Iterator[dict] return type is deliberate: it means sources can be lazy
#    (streaming from a file, paginating an API) without the pipeline needing to
#    know. The pipeline calls read() and iterates. Memory efficiency is the
#    source's responsibility.
#
# The key design decision: we use dict, not a Pydantic model, as the interchange
# format between extract and transform. This is because at extraction time we
# may not know the schema. Validation happens in the transform phase, where
# we have schema definitions. Separating extraction (schema-agnostic) from
# validation (schema-aware) is deliberate.
from abc import ABC, abstractmethod
from collections.abc import Iterator


class SourceReader(ABC):
    @abstractmethod
    def read(self, source: str) -> Iterator[dict]:
        ...

    @property
    @abstractmethod
    def source_type(self) -> str:
        ...
