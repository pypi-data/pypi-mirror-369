TYPE_ATTR = 'type'
NAME_ATTR = 'name'
VALUE_ATTR = 'value'
DEFAULT_VALUE_ATTR = 'defaultValue'
ALLOWED_VALUE_ATTR = 'allowedValue'
SENSITIVE_ATTR = 'sensitive'
DESCRIPTION_ATTR = 'description'


class InteractiveParameter:

    def __init__(self, raw_parameter: dict):
        self.name = raw_parameter.get(NAME_ATTR)
        if TYPE_ATTR in raw_parameter:
            self.type = raw_parameter.get(TYPE_ATTR).upper()
        self.sensitive = bool(raw_parameter.get(SENSITIVE_ATTR))
        self.description = raw_parameter.get(DESCRIPTION_ATTR)
        self.allowed_value = raw_parameter.get(ALLOWED_VALUE_ATTR)
        self._value = None
        if VALUE_ATTR in raw_parameter:
            self.default_value = raw_parameter[VALUE_ATTR]
        else:
            self.default_value = raw_parameter.get(DEFAULT_VALUE_ATTR)
        # Auxiliary attributes
        self.value_provided_by_user = False
        self._force_prompt = False

    @property
    def value(self):
        return self._value if self.value_provided_by_user else self.default_value

    @value.setter
    def value(self, value):
        self._value = value
        self.value_provided_by_user = True

    def force_prompt(self):
        self.value = None
        self.value_provided_by_user = False
        self._force_prompt = True

    def is_prompt_forced(self):
        return self._force_prompt

    def to_raw_parameter(self):
        return {
            NAME_ATTR: self.name,
            VALUE_ATTR: self.value,
            DEFAULT_VALUE_ATTR: self.default_value,
            TYPE_ATTR: self.type,
            SENSITIVE_ATTR: self.sensitive
        }

    def __eq__(self, other):
        if not isinstance(other, InteractiveParameter):
            return NotImplemented
        return self.name == other.name

    def __hash__(self):
        return hash(self.name)
