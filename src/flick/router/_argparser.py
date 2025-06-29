from typing import List

from flask_restful import reqparse


class ReqArg:
    def __init__(self, *args, **kwargs) -> None:
        self.args = args
        self.kwargs = kwargs


def query_parser(args: List[ReqArg]):
    parser = reqparse.RequestParser()
    for arg in args:
        arg.kwargs.pop('location', None)
        parser.add_argument(*arg.args, location='args', **arg.kwargs)
    return parser
