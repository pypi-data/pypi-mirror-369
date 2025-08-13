from argparse import ArgumentParser, Namespace
from pathlib import Path
from typing import AsyncIterable, Awaitable, Callable, Iterable, overload

from tdm import TalismanDocument
from typing_extensions import Literal

from talisman_tools.plugin import SerializerPlugins


@overload
def get_serializer_factory(
        parser: ArgumentParser, sync: Literal[True] = True
) -> Callable[[Namespace], Callable[[Iterable[TalismanDocument]], None]]:
    ...


@overload
def get_serializer_factory(
        parser: ArgumentParser, sync: Literal[False] = True
) -> Callable[[Namespace], Callable[[AsyncIterable[TalismanDocument]], Awaitable[None]]]:
    ...


def get_serializer_factory(parser: ArgumentParser, sync: bool = True):
    serializers = SerializerPlugins.flattened
    argument_group = parser.add_argument_group(title="Output documents arguments")
    argument_group.add_argument('output', type=Path, metavar='<output path>')
    argument_group.add_argument('-serializer', type=str, metavar='<serializer type>', choices=set(serializers.keys()), default='default')

    if sync:
        def get_serializer(args: Namespace) -> Callable[[Iterable[TalismanDocument]], None]:
            from functools import partial
            return partial(serializers[args.serializer]().serialize, path=args.output)
    else:
        def get_serializer(args: Namespace) -> Callable[[AsyncIterable[TalismanDocument]], Awaitable[None]]:
            from functools import partial
            return partial(serializers[args.serializer]().aserialize, path=args.output)

    return get_serializer
