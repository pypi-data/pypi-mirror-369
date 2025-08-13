__all__ = [
    'ConfigurableReaderPlugins', 'CLIPlugins', 'DomainPlugins', 'EndpointPlugins', 'ProcessorPlugins', 'ReaderPlugins',
    'SerializerPlugins', 'TrainerPlugins', 'WrapperPlugins', 'WrapperActionsPlugins'
]


from .cli import CLIPluginManager
from .domain import DomainPluginManager
from .endpoint import EndpointPluginManager
from .processor import ProcessorPluginManager
from .reader import ConfigurableReaderPluginManager, ReaderPluginManager
from .serializer import SerializerPluginManager
from .trainer import TrainerPluginManager
from .wrapper import WrapperPluginManager
from .wrapper_actions import WrapperActionsPluginManager

CLIPlugins = CLIPluginManager()
ConfigurableReaderPlugins = ConfigurableReaderPluginManager()
DomainPlugins = DomainPluginManager()
EndpointPlugins = EndpointPluginManager()
ProcessorPlugins = ProcessorPluginManager()
ReaderPlugins = ReaderPluginManager()
SerializerPlugins = SerializerPluginManager()
TrainerPlugins = TrainerPluginManager()
WrapperPlugins = WrapperPluginManager()
WrapperActionsPlugins = WrapperActionsPluginManager()
