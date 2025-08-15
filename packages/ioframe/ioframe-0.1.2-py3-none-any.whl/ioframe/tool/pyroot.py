"""Define tools for the ``pyroot`` engine."""


def setup_multithreading(n_workers: int | None = None) -> None:
    """Set up multithreading for PyROOT.

    This method enables multithreading in PyROOT if the number of workers
    is greater than 1, or disables it if the number of workers is 1.
    """
    from ROOT import (  # noqa: PLC0415
        DisableImplicitMT,
        EnableImplicitMT,
        IsImplicitMTEnabled,
    )

    if n_workers is None:
        EnableImplicitMT()
    elif n_workers > 1:
        EnableImplicitMT(n_workers)
    elif n_workers == 1:
        if IsImplicitMTEnabled():
            DisableImplicitMT()
    else:
        msg = (
            f"Invalid number of workers: {n_workers}. "
            "It must be None or a strictly positive integer."
        )
        raise ValueError(msg)
