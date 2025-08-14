from oslo_config.cfg import DefaultValueError, Opt
from oslo_config import types

from certx.provider import crypto


class EncryptedStr(types.ConfigType):
    def __call__(self, value):
        try:
            if isinstance(value, str) and value.startswith("encrypted:"):
                encrypted_part = value[len("encrypted:"):]
                return crypto.decrypt(encrypted_part)
        except Exception as e:
            raise ValueError(f"Failed to decrypt configuration value: {str(e)}")
        return value

    def __repr__(self):
        return 'EncryptedStr'

    def _formatter(self, value):
        return self.quote_trailing_and_leading_space(value)


class EncryptedStrOpt(Opt):
    def __init__(self, name, **kwargs):
        super().__init__(name, type=EncryptedStr(), **kwargs)

    def _check_default(self):
        if self.default is not None and not self._default_is_ref():
            if not isinstance(self.default, str):
                raise DefaultValueError("Error processing default value %(default)s for Opt type of %(opt)s."
                                        % {'default': self.default, 'opt': self.type})
