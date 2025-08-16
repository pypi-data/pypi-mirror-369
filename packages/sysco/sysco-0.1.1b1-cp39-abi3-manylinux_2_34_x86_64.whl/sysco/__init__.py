# import cvxpy as cvx
from loguru import logger

from sysco._core import hello_from_bin
# from sysco.controller.controller import Controller as Controller

from .controller import BaseController as BaseController

logger.debug(f"Importing {__name__}")


def hello_from_rust() -> str:
    return hello_from_bin()
