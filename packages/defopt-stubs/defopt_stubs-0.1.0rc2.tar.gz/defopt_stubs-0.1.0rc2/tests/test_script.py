from defopt import run, bind, bind_known, signature


def main(value: int, *, times: int = 1) -> int:
    """Print a value multiple times and return it.

    :param value: Value to display
    :param times: Number of repetitions
    :returns: The input ``value``
    """
    for _ in range(times):
        print(value)
    return value


def demo_bind() -> None:
    call = bind(main, argv=["1", "--times", "2"])
    ret1: int = call()
    call2, rest = bind_known(main, argv=["2", "--times", "3"])
    ret2: int = call2()


def demo_signature() -> None:
    sig = signature(main)
    doc: str | None = sig.doc
    param_doc: str | None = sig.parameters["value"].doc


def demo_run_dict() -> None:
    """Demonstrate running a mapping of callables.

    This ensures that ``run`` infers and returns the expected type when
    dispatching to a subcommand.
    """

    def double(value: int) -> int:
        return value * 2

    funcs = {"double": double}
    result: int = run(funcs, argv=["double", "3"])


if __name__ == "__main__":
    demo_bind()
    demo_signature()
    demo_run_dict()
    res: int = run(main)
