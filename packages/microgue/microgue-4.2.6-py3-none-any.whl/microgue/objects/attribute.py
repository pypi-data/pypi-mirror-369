from datetime import datetime


class Attribute:
    def __init__(
            self,
            hidden=False,
            required=False,
            unique=False,
            default=False,
            default_value=None,
            type=None,
            serialize=None,
            deserialize=None
    ):
        self.hidden = hidden
        self.required = required
        self.unique = unique
        self.default = default
        self.default_value = default_value
        self.type = type
        self.serialize = serialize
        self.deserialize = deserialize

        # set default serialize and deserialize functions for datetime type
        if type is datetime:
            if serialize is None:
                self.serialize = lambda x: None if x is None else x.isoformat()
            if deserialize is None:
                self.deserialize = lambda x: None if x is None else datetime.fromisoformat(x)
