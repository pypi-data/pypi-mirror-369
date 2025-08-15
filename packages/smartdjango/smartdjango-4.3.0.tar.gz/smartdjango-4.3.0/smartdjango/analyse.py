from functools import wraps

from django.http import HttpRequest
from django.utils.translation import gettext as _
from oba import Obj

from smartdjango.code import Code
from smartdjango.error import Error
from smartdjango.utils import io, inspect
from smartdjango.validation.dict_validator import DictValidator
from smartdjango.validation.validator import Validator


class Request(HttpRequest):
    json: Obj
    query: Obj
    argument: Obj
    data: Obj


@Error.register
class AnalyseErrors:
    REQUEST_NOT_FOUND = Error(_("Cannot find request"), code=Code.InternalServerError)


def get_request(*args):
    for i, arg in enumerate(args):
        if isinstance(arg, HttpRequest):
            return arg
    raise AnalyseErrors.REQUEST_NOT_FOUND


def update_to_data(req: Request, target):
    data = getattr(req, '_data', None)
    data = data() if data is not None else {}
    data.update(target())
    req.data = Obj(data)


def analyse(*validators: Validator | str, target_getter, target_setter, restrict_keys):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            req = get_request(*args)
            target = target_getter(req, kwargs)

            validator = DictValidator().fields(*validators)
            if restrict_keys:
                validator.restrict_keys()
            target = validator.clean(target)
            target_setter(req, Obj(target))

            return func(*args, **kwargs)
        return wrapper
    return decorator


def json(*validators: Validator | str, restrict_keys=True):
    def getter(req, kwargs):
        return io.json_loads(req.body.decode())

    def setter(req, target):
        req.json = target
        update_to_data(req, target)

    return analyse(
        *validators,
        target_getter=getter,
        target_setter=setter,
        restrict_keys=restrict_keys
    )


def query(*validators: Validator | str, restrict_keys=False):
    def getter(req, kwargs):
        return req.GET.dict()

    def setter(req, target):
        req.query = target
        update_to_data(req, target)

    return analyse(
        *validators,
        target_getter=getter,
        target_setter=setter,
        restrict_keys=restrict_keys
    )


def argument(*validators: Validator | str, restrict_keys=True):
    def getter(req, kwargs):
        return kwargs

    def setter(req, target):
        req.argument = target
        update_to_data(req, target)

    return analyse(
        *validators,
        target_getter=getter,
        target_setter=setter,
        restrict_keys=restrict_keys
    )


def request(bool_func, message=None):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            req = get_request(*args)
            Validator().bool(bool_func, message=message).clean(req)
            return func(*args, **kwargs)

        return wrapper
    return decorator


def function(*validators: Validator | str, restrict_keys=True):
    validator = DictValidator().fields(*validators)
    if restrict_keys:
        validator.restrict_keys()

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            args, kwargs = inspect.get_function_arguments(func, *args, **kwargs)
            arguments = dict(**args, **kwargs)
            arguments = validator.clean(arguments)

            return func(**arguments)
        return wrapper
    return decorator
