def add(a: float, b: float) -> float:
    """Return the sum of *a* and *b*."""
    return a + b


def mean(values):
    """Return the arithmetic mean of an iterable of numbers.

    Raises:
        ValueError: if *values* is empty.
    """
    vals = list(values)
    if not vals:
        raise ValueError("values must not be empty")
    return sum(vals) / len(vals)


def _square_cli():
    """Console script entrypoint: prints n*n for an integer argument."""
    import sys
    if len(sys.argv) != 2:
        print("Usage: thangdemo-cli <int>")
        sys.exit(1)
    try:
        n = int(sys.argv[1])
    except ValueError:
        print("Argument must be an integer")
        sys.exit(2)
    print(n * n)
