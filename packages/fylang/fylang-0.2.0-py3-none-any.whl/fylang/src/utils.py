from typing import (
    Callable as CallableType,
    Any,
    Optional,
    Dict as DictType,
)


class Environment:
    def __init__(self, parent: Optional["Environment"] = None):
        self.values: DictType[str, Any] = {}
        self.parent = parent

    def define(self, name: str, value: Any):
        self.values[name] = value

    def assign(self, name: str, value: Any):
        if name in self.values:
            self.values[name] = value
        elif self.parent:
            self.parent.assign(name, value)
        else:
            self.define(name, value)

    def get(self, name: str) -> Any:
        if name in self.values:
            return self.values[name]
        if self.parent:
            return self.parent.get(name)
        raise RuntimeError(f"Undefined variable '{name}'")


class Callable:
    def __init__(
        self,
        env: Environment,
        fn_callable: CallableType,
        arity: int,
        get_label=lambda x: f"<fn: arity={x}>",
    ):
        self.env = env
        self.arity = arity
        self.fn_callable = fn_callable
        self.get_label = get_label

    def __call__(self, *args):
        return self.fn_callable(self.env, *args)

    def __str__(self):
        return self.get_label(self.arity)

    def __repr__(self):
        return str(self)


class NoneLiteral:
    def __str__(self):
        return "none"

    def __repr__(self):
        return str(self)


class ReturnException(Exception):
    def __init__(self, value: Any):
        self.value = value


class Reference:
    def __init__(self, getter: CallableType, setter: CallableType):
        self._getter = getter
        self._setter = setter

    def get(self):
        val = self._getter()
        while isinstance(val, Reference):
            val = val.get()
        return val

    def set(self, value: Any):
        if isinstance(value, Reference):
            value = value.get()
        return self._setter(value)

    def __str__(self):
        # return f"|{str(self.get())}|"
        return str(self.get())

    def __repr__(self):
        return str(self)


class StructInstance:
    def __init__(
        self,
        struct_value: "StructValue",
        instance_values: DictType[str, Any | NoneLiteral],
    ):
        self.struct = struct_value
        self.fields = instance_values

    def __getattr__(self, name: str):
        if name in self.fields:
            return self.fields[name]
        raise RuntimeError(f"Field '{name}' not found in struct")

    def __setattr__(self, name, value):
        if name in ("struct", "fields"):
            super().__setattr__(name, value)
        elif name in self.fields:
            self.fields[name] = value
        else:
            raise RuntimeError(f"Cannot add new field '{name}' to struct")

    def __str__(self):
        kv = lambda key, value: f"{key}={value}"
        return (
            f"{{ {', '.join(kv(key, value) for key, value in self.fields.items())} }}"
        )


class StructValue:
    def __init__(self, name: str | None, fields: DictType[str, Any]):
        self.name = name
        self.fields = fields

    def __call__(self, *args, **kwargs):
        field_names = list(self.fields.keys())
        instance_values = {}

        if len(args) > len(field_names):
            raise RuntimeError("Too many positional arguments for struct")

        for i, value in enumerate(args):
            instance_values[field_names[i]] = value

        for name, value in kwargs.items():
            if name not in self.fields:
                raise RuntimeError(f"Unknown field '{name}' for struct")
            if name in instance_values:
                raise RuntimeError(f"Field '{name}' already set by positional arg")
            instance_values[name] = value

        for key, value in self.fields.items():
            if key not in instance_values:
                instance_values[key] = value

        instance = StructInstance(self, instance_values)

        for fname, fval in self.fields.items():
            if isinstance(fval, Callable):
                bound_env = Environment(fval.env)
                bound_env.define("this", instance)
                instance.fields[fname] = Callable(
                    bound_env, fval.fn_callable, fval.arity
                )

        return instance

    def __str__(self):
        return f"<struct: {{ {', '.join(self.fields.keys())} }}>"
