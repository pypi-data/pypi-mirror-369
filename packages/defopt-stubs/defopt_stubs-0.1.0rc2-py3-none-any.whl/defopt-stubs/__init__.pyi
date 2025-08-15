import types
import inspect
from typing import Callable, Mapping, Sequence, List, Optional, Union, Literal, Tuple

type Funcs[T] = Callable[..., T] | Sequence[Callable[..., T]] | Mapping[str, Funcs[T]]


__version__: str

def run[T](
    funcs: Funcs[T],
    *,
    parsers: Mapping[type, Callable[[str], object]] = ...,
    short: Optional[Mapping[str, str]] = ...,
    cli_options: Literal["kwonly", "all", "has_default"] = ..., 
    show_defaults: bool = ..., 
    show_types: bool = ..., 
    no_negated_flags: bool = ..., 
    version: Union[str, None, bool] = ..., 
    argparse_kwargs: Mapping[str, object] = ...,
    intermixed: bool = ..., 
    argv: Optional[Sequence[str]] = ...,
) -> T: ...

def bind[T](
    funcs: Funcs[T],
    *,
    parsers: Mapping[type, Callable[[str], object]] = ...,
    short: Optional[Mapping[str, str]] = ...,
    cli_options: Literal["kwonly", "all", "has_default"] = ..., 
    show_defaults: bool = ..., 
    show_types: bool = ..., 
    no_negated_flags: bool = ..., 
    version: Union[str, None, bool] = ..., 
    argparse_kwargs: Mapping[str, object] = ...,
    intermixed: bool = ..., 
    argv: Optional[Sequence[str]] = ...,
) -> Callable[[], T]: ...

def bind_known[T](
    funcs: Funcs[T],
    *,
    parsers: Mapping[type, Callable[[str], object]] = ...,
    short: Optional[Mapping[str, str]] = ...,
    cli_options: Literal["kwonly", "all", "has_default"] = ..., 
    show_defaults: bool = ..., 
    show_types: bool = ..., 
    no_negated_flags: bool = ..., 
    version: Union[str, None, bool] = ..., 
    argparse_kwargs: Mapping[str, object] = ...,
    intermixed: bool = ..., 
    argv: Optional[Sequence[str]] = ...,
) -> Tuple[Callable[[], T], List[str]]: ...
class Parameter(inspect.Parameter):
    doc: Optional[str]
    def replace(
        self,
        *,
        doc: Optional[str] = ...,
        **kwargs: object,
    ) -> "Parameter": ...

class Signature(inspect.Signature):
    doc: Optional[str]
    raises: Tuple[type[BaseException], ...]

    @property
    def parameters(self) -> types.MappingProxyType[str, Parameter]: ...

    def replace(
        self,
        *,
        doc: Optional[str] = ...,
        raises: Tuple[type[BaseException], ...] = ...,
        **kwargs: object,
    ) -> "Signature": ...


def signature(func: Callable[..., object] | str) -> Signature: ...
