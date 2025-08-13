from argparse import Namespace

from talisman_tools.configure.configure import read_config
from tp_interfaces.abstract import AbstractDocumentProcessor
from tp_interfaces.readers.abstract import AbstractReader

try:
    from tqdm.asyncio import tqdm
except ImportError:
    tqdm = lambda x: x


async def async_action(processor: AbstractDocumentProcessor, serializer, reader: AbstractReader, args: Namespace):
    async with processor:
        processor_config_type = processor.config_type
        config = processor_config_type.model_validate(read_config(args.config)) if args.config else processor_config_type()
        await serializer(tqdm(processor.process_stream(reader.aread(), config, args.batch, args.concurrency, args.results_queue_size)))
