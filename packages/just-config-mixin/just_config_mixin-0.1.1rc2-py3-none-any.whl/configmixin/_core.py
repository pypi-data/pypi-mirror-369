import functools
import inspect
import pathlib
import re
from copy import deepcopy
from os import PathLike
from types import MappingProxyType
from typing import Any, Callable, TypeVar

import orjson

from ._json import default, option

_Self = TypeVar("_Self", bound="ConfigMixin")

_IGNORE_REGEX = re.compile(r"^_")


class ConfigMixin:
    r"""Mixin class for automated configuration registration and IO.

    Attributes
    ----------
    config_name : str, default=None
        Class attribute that specifies the filename under which the config should be stored when calling
        `save_config`. Should be overridden by the subclass.
    ignore_for_config : list[str], default=[]
        Class attribute that specifies a list of attributes that should not be saved in the config. Should
        be overridden by the subclass.

    Examples
    --------
    In this example, we have a model with 3 arguments:

    - ``hidden_size``: The hidden size of the model.
    - ``_num_layers``: The number of layers in the model.
    - ``dropout``: The dropout rate of the model.

    Among the three arguments, the number of layers is implicitly ignored by the decorator because of the leading
    underscore; the ``dropout`` argument is explicitly based on the specification in ``ignore_for_config`` class
    variable. The ``hidden_size`` argument is registered to the config.

    >>> class MyModel(ConfigMixin):
    ...     config_name = "my_model_config.json"
    ...     ignore_for_config = ["dropout"]
    ...
    ...     @register_to_config
    ...     def __init__(self, hidden_size: int = 768, _num_layers: int = 12, dropout: float = 0.1):
    ...         self.hidden_size = hidden_size
    ...         self.num_layers = _num_layers
    ...         self.dropout = dropout  # This will be ignored because of the specification in `ignore_for_config`
    ...
    >>> model = MyModel(hidden_size=1024, _num_layers=20, dropout=0.2)
    >>> model.config
    mappingproxy({'__notes__': {'class_name': 'MyModel', 'using_default_values': [], 'args': (), 'kwargs': {}}, 'hidden_size': 1024})
    >>> model.num_layers
    20
    >>> model.dropout
    0.2
    """

    _private_names = ["__notes__"]

    config_name = None
    ignore_for_config = []

    def __repr__(self) -> str:
        return f"{self.__class__.__name__} {self.config_dumps()}"

    def _register_to_config(self, **kwargs) -> None:
        self._internal_dict = kwargs

    @property
    def config(self) -> MappingProxyType:
        r"""Returns the config of the class as a ``MappingProxyType``.

        ``MappingProxyType`` is used to mitigate unintended modifications to the config dictionary.
        Note that this method does not completely rule out the possibility of modifying the config.
        For instance, if the user access a nested dictionary or list in the config, they can still
        modify the contents after dereferencing the nested object.

        Returns
        -------
        MappingProxyType
            The config of the class wrapped in ``MappingProxyType``.
        """
        return MappingProxyType(self._internal_dict)

    def save_config(
        self,
        save_directory: str | PathLike,
        *,
        overwrite: bool = False,
        default: Callable = default,
        option: int = option,
    ) -> int:
        r"""Save a configuration object to the directory specified in ``save_directory``.

        The configuration is saved as a JSON file named as ``self.config_name`` in the directory
        specified in ``save_directory``.

        It is recommended to save the configuration in the same directory as the main
        objects, e.g., a model checkpoint, or other metadata files.

        Parameters
        ----------
        save_directory : str or PathLike
            Directory where the configuration JSON file, named as ``self.config_name``, is saved.
        overwrite : bool, default=False
            Whether to overwrite the configuration file if it already exists.
        default : Callable, default=configmixin.default
            Same as the ``default`` argument in ``orjson.dumps``, which can be used to explicitly handle custom
            objects or override default serialization behaviors. Serialization can lose information such that it
            may not be possible to fully restore the original object without additional post-processing after
            deserialization.
        option : int, default=configmixin.option
            A bitwise OR of the ``orjson`` options. Please refer to the ``orjson`` documentation for more details.

        Returns
        -------
        int
            The number of bytes written to the file.
        """
        if self.config_name is None:
            msg = f"Make sure that {self.__class__.__name__} has defined a class attribute `config_name`."
            raise NotImplementedError(msg)

        dest = pathlib.Path(save_directory)
        if dest.is_file():
            msg = f"Provided path ({save_directory}) should be a directory, not a file"
            raise AssertionError(msg)

        dest.mkdir(parents=True, exist_ok=True)
        file = dest / self.config_name
        if file.is_file() and not overwrite:
            msg = (
                f"Provided path ({save_directory}) already contains a file named {self.config_name}. "
                "Please set `overwrite=True` to overwrite the existing file."
            )
            raise FileExistsError(msg)

        with open(file, "wb") as writer:
            return writer.write(self.config_dumps(default=default, option=option))

    @classmethod
    def from_config(
        cls: type[_Self],
        config: dict[str, Any] = None,
        *,
        save_directory: str | PathLike = None,
        runtime_kwargs: dict[str, Any] = None,
    ) -> _Self:
        r"""Instantiate the current class from a config dictionary.

        Parameters
        ----------
        config : dict[str, Any], default=None
            A dictionary of the config parameters. If provided, the config will be loaded from the dictionary
            instead of the JSON file. If not provided, the config will be loaded from the JSON file.
        save_directory : str or PathLike, default=None
            Directory where the configuration JSON file, named as ``self.config_name``, is saved. Note that the
            ``config`` argument takes precedence over the ``save_directory`` argument.
        runtime_kwargs : dict[str, Any], default=None
            A dictionary of the runtime kwargs. These are usually non-serializable parameters that need to be
            determined/initialized at runtime, such as the model object of a trainer class.

        Returns
        -------
        An instance of the class.
        """
        if config is None:
            if save_directory is None:
                msg = "Either `save_directory` or `config` must be provided"
                raise ValueError(msg)

            dest = pathlib.Path(save_directory)
            if dest.is_file():
                msg = f"Provided path ({save_directory}) should be a directory, not a file"
                raise AssertionError(msg)

            file = dest / cls.config_name
            if not file.is_file():
                msg = f"Provided path ({save_directory}) does not contain a file named {cls.config_name}"
                raise FileNotFoundError(msg)

            with open(file, "rb") as reader:
                config = orjson.loads(reader.read())

        notes = config.get("__notes__", {})
        if notes.get("class_name") != cls.__name__:
            msg = f"Config {cls.config_name} is not a config for {cls.__name__}."
            raise ValueError(msg)

        pooled_kwargs = cls.apply_param_hooks(deepcopy(config)) | (runtime_kwargs or {})
        for name in cls._private_names:
            pooled_kwargs.pop(name, None)

        signature = inspect.signature(cls)

        args = []
        for name, param in signature.parameters.items():
            if param.kind not in {
                inspect.Parameter.POSITIONAL_ONLY,
                inspect.Parameter.POSITIONAL_OR_KEYWORD,
            }:
                continue
            if name not in pooled_kwargs:
                msg = f"Config is missing required parameter: {name}."
                raise KeyError(msg)
            args.append(pooled_kwargs.pop(name))

        args.extend(notes.get("args", []))
        pooled_kwargs = pooled_kwargs | notes.get("kwargs", {})

        return cls(*args, **pooled_kwargs)

    @classmethod
    def apply_param_hooks(cls, jdict: dict[str, Any]) -> dict[str, Any]:
        r"""Apply post-processing hooks to the JSON dictionary.

        ``orjson.loads`` only decode configs to primitive types, which may not be directly
        consumable by the class initializer. For instance, a ``dataclass`` object will be
        loaded as a dictionary. Therefore, this method is intended to be overridden by the
        subclass to perform additional post-processing on the loaded config dictionary.

        Note that, it is highly discouraged to abuse this method to deserialize complex objects
        and one should consider using ``runtime_kwargs`` argument of ``from_config`` instead,
        to explicitly pass the complex objects to the class initializer.

        By default, this method returns the input dictionary unchanged.

        Parameters
        ----------
        jdict : dict[str, Any]
            The config dictionary after deserialization.

        Returns
        -------
        dict[str, Any]
            The config dictionary after post-processing.
        """
        return jdict

    def config_dumps(self, default=default, option=option) -> str:
        r"""Serializes the configurations to a JSON string.

        In addition to the config parameters, the JSON string also includes metadata in the '__notes__' field such
        as the class name, which argument values were registered from default values, and any variable arguments.

        Parameters
        ----------
        default : Callable, default=configmixin.default
            Same as the ``default`` argument in ``orjson.dumps``, which can be used to explicitly handle custom
            objects or override default serialization behaviors. Serialization can lose information such that it
            may not be possible to fully restore the original object without additional post-processing after
            deserialization.
        option : int, default=configmixin.option
            A bitwise OR of the ``orjson`` options. Please refer to the ``orjson`` documentation for more details.

        Returns
        -------
        str
            String containing all the attributes that make up the configuration instance in JSON format.
            Note that ignored config parameters (specified via ``ignore_for_config``) are not included in
            the JSON string.
        """
        return orjson.dumps(self._internal_dict, default=default, option=option)


def register_to_config(init):
    r"""Decorator for the init of classes inheriting from `ConfigMixin` for auto argument-registration.

    Users should apply this decorator to the ``__init__(self, ...)`` method of the subclass so that all
    the arguments are automatically sent to ``self._register_to_config``. To ignore a specific argument
    accepted by the init but that shouldn't be registered in the config, use the ``ignore_for_config``
    class variable.

    Examples
    --------
    In this example, we have a model with 3 arguments:

    - ``hidden_size``: The hidden size of the model.
    - ``_num_layers``: The number of layers in the model.
    - ``dropout``: The dropout rate of the model.

    Among the three arguments, the number of layers is implicitly ignored by the decorator because of the leading
    underscore; the ``dropout`` argument is explicitly based on the specification in ``ignore_for_config`` class
    variable. The ``hidden_size`` argument is registered to the config.

    >>> class MyModel(ConfigMixin):
    ...     config_name = "my_model_config.json"
    ...     ignore_for_config = ["dropout"]
    ...
    ...     @register_to_config
    ...     def __init__(self, hidden_size: int = 768, _num_layers: int = 12, dropout: float = 0.1):
    ...         self.hidden_size = hidden_size
    ...         self.num_layers = _num_layers
    ...         self.dropout = dropout  # This will be ignored because of the specification in `ignore_for_config`
    ...
    >>> model = MyModel(_num_layers=20, dropout=0.2)
    >>> model.config
    mappingproxy({'__notes__': {'class_name': 'MyModel', 'using_default_values': ['hidden_size'], 'args': (), 'kwargs': {}}, 'hidden_size': 768})
    >>> model.num_layers
    20
    >>> model.dropout
    0.2
    """

    @functools.wraps(init)
    def inner_init(self, *args, **kwargs):
        if not isinstance(self, ConfigMixin):
            msg = (
                f"`@register_to_config` was applied to {self.__class__.__name__} init method, "
                "but this class does not inherit from `ConfigMixin`."
            )
            raise RuntimeError(msg)

        if self.config_name is None:
            msg = f"Make sure that {self.__class__.__name__} has defined a class attribute `config_name`."
            raise NotImplementedError(msg)

        signature = inspect.signature(self.__class__)

        ignore_for_config = set(getattr(self, "ignore_for_config", []))
        registered_kwargs = {
            "__notes__": {
                "class_name": self.__class__.__name__,
                "using_default_values": [],
                "args": args[_num_non_var_positional(signature) :],
                "kwargs": {
                    name: param
                    for name, param in kwargs.items()
                    if not (
                        name in signature.parameters
                        or _is_ignored_name(name, ignore_for_config)
                    )
                },
            },
        }

        # Obtain the names corresponding to positional arguments.
        #
        # Note that, if the number of provided positional argument is greater than the number
        # of non-var positional arguments, while no var positional argument is present in the
        # init signature, the extra positional arguments could be incorrectly associated with
        # the var keyword arguments. But the instantiation of the class will fail anyway.
        for name, param in zip(signature.parameters.keys(), args):
            if signature.parameters[name].kind is inspect.Parameter.VAR_POSITIONAL:
                break
            if _is_ignored_name(name, ignore_for_config):
                continue
            registered_kwargs[name] = param

        # Fill in the default values for the remaining positional arguments.
        #
        # Note that positional arguments of the init method may also be passed in as keyword
        # arguments, which will be captured by the `kwargs` argument. In this cases, default
        # values will not be used.
        for name, param in filter(
            lambda i: i[0] not in registered_kwargs, signature.parameters.items()
        ):
            if _is_ignored_name(name, ignore_for_config):
                continue
            if name in kwargs:
                registered_kwargs[name] = kwargs[name]
                continue
            if param.default is not inspect.Parameter.empty:
                registered_kwargs[name] = param.default
                registered_kwargs["__notes__"]["using_default_values"].append(name)

        self._register_to_config(**registered_kwargs)
        init(self, *args, **kwargs)

    return inner_init


def _is_ignored_name(name: str, ignore_for_config: list[str]) -> bool:
    return name in ignore_for_config or _IGNORE_REGEX.match(name) is not None


def _num_non_var_positional(signature: inspect.Signature) -> int:
    return sum(
        param.kind
        in {
            inspect.Parameter.POSITIONAL_ONLY,
            inspect.Parameter.POSITIONAL_OR_KEYWORD,
        }
        for param in signature.parameters.values()
    )
