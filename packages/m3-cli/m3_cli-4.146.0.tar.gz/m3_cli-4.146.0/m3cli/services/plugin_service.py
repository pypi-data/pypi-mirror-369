import os
import inspect

from m3cli.services.environment_service import get_configuration_folder_path
from m3cli.utils.logger import get_logger

_LOG = get_logger('plugin_service')

INTEGRATION_REQUEST_METHOD_NAME = 'create_custom_request'
INTEGRATION_RESPONSE_METHOD_NAME = 'create_custom_response'

INTEGRATION_REQUEST_ATTRIBUTE_NAME = 'integration_request'
INTEGRATION_RESPONSE_ATTRIBUTE_NAME = 'integration_response'
INTEGRATION_SUFFIX_ATTRIBUTE_NAME = 'integration_suffix'

DATA_PROCESSING_MAPPING = {
    INTEGRATION_REQUEST_ATTRIBUTE_NAME: INTEGRATION_REQUEST_METHOD_NAME,
    INTEGRATION_RESPONSE_ATTRIBUTE_NAME: INTEGRATION_RESPONSE_METHOD_NAME
}

REQUEST_KEY = 'request'
RESPONSE_KEY = 'response'
VIEW_TYPE_KEY = 'view_type'

METHOD_TYPE_MAPPING = {
    INTEGRATION_REQUEST_ATTRIBUTE_NAME: REQUEST_KEY,
    INTEGRATION_RESPONSE_ATTRIBUTE_NAME: RESPONSE_KEY
}


class PluginService:
    def __init__(self, m3cli_path, command_name, cmd_def):
        suffix = cmd_def.get(INTEGRATION_SUFFIX_ATTRIBUTE_NAME)
        self.command_name = f'{command_name}-{suffix}' if suffix else command_name
        self.cmd_def = cmd_def
        from sys import path
        path_env_var = get_configuration_folder_path()
        self.custom_plugins_path = path_env_var
        self.built_in_plugins_path = os.path.join(m3cli_path, 'plugins')
        _LOG.debug(f'Resolved custom path to plugins: '
                   f'{self.custom_plugins_path}')
        _LOG.debug(f'Resolved built in path to plugins: '
                   f'{self.built_in_plugins_path}')
        path.extend([self.built_in_plugins_path, self.custom_plugins_path])

    def validate_method(self, method):
        try:
            getattr(__import__(self.command_name), method)
        except ModuleNotFoundError:
            if self.custom_plugins_path and os.path.isfile(os.path.join(
                    self.custom_plugins_path, self.command_name + '.py')):
                import shutil
                shutil.copyfile(os.path.join(
                    self.custom_plugins_path, self.command_name + '.py'),
                    os.path.join(
                        self.built_in_plugins_path, self.command_name + '.py'))
            else:
                raise FileNotFoundError(
                    f'Missed required plugin file for the command '
                    f'{self.command_name}')
        except AttributeError:
            raise AttributeError(f'Missed required method "{method}()" in the '
                                 f'plugin file for the command '
                                 f'"{self.command_name}"')
        plugin_module = __import__(self.command_name)
        plugin_method = getattr(plugin_module, method)
        _LOG.debug(f'Imported custom plugin: {plugin_module.__file__}, '
                   f'method {method}')
        return plugin_method

    def apply_plugin(self, data, method_type):
        method_action_type = METHOD_TYPE_MAPPING.get(method_type)
        if not self.cmd_def.get(method_type):
            return data.get(method_action_type)

        method = DATA_PROCESSING_MAPPING.get(method_type)
        plugin_method = self.validate_method(method=method)

        # Prepare keyword arguments based on method's parameters
        sig = inspect.signature(plugin_method)
        params = sig.parameters

        kwargs = {}
        # Check and add 'request' if the method expects it
        if REQUEST_KEY in params:
            kwargs[REQUEST_KEY] = data.get(REQUEST_KEY)
        # Check and add 'response' if applicable and method expects it
        if method_action_type == RESPONSE_KEY and RESPONSE_KEY in params:
            kwargs[RESPONSE_KEY] = data.get(RESPONSE_KEY)
        # Check and add 'view_type' if the method expects it
        if VIEW_TYPE_KEY in params:
            kwargs[VIEW_TYPE_KEY] = data.get(VIEW_TYPE_KEY)

        return plugin_method(**kwargs)
