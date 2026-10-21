import logging


def quiet_nemo_logging():
    """NeMo logs every config detail on model load; keep only warnings and errors."""

    from nemo.utils import logging as nemo_logging
    nemo_logging.setLevel(logging.WARNING)
