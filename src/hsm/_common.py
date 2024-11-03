from enum import IntEnum
from typing import Any, Callable, Final, Type, TypeVar, _ProtocolMeta
from typing_extensions import TypeIs

TEvent = TypeVar("TEvent", bound=IntEnum)
TState = TypeVar("TState")
TNode = TypeVar("TNode")


class HSMStatus(IntEnum):
    NO_TRANSITION = -2_147_483_648
    SELF_TRANSITION = -2_147_483_647
    EVENT_UNHANDLED = -2_147_483_646


def is_hsm_status(node: Type[TNode] | HSMStatus) -> TypeIs[HSMStatus]:
    return isinstance(node, HSMStatus)


def _is_hsm_node(cls: Any) -> TypeIs[Type["NodeMeta"]]:
    return getattr(cls, "__hsm_node", False)


class _NodeMixin:
    _superstate: type | None
    _substates: tuple[type, ...]
    _event_handlers: tuple[
        tuple[
            IntEnum,
            Callable[[TEvent, TState | None], type | HSMStatus],
        ],
        ...,
    ]


class _NodeMeta(type, _NodeMixin):
    def __new__(
        cls: Type["_NodeMeta"],
        name: str,
        bases: tuple[type, ...],
        dct: dict[str, Any],
    ) -> "_NodeMeta":
        dct["__hsm_node"] = True
        node_cls = super().__new__(cls, name, bases, dct)
        node_cls._superstate = None

        substates: Final[list[type]] = []
        for attr_value in dct.values():
            if _is_hsm_node(attr_value):
                substates.append(attr_value)
                attr_value._superstate = node_cls
        node_cls._substates = tuple(substates)
        del substates

        if not hasattr(node_cls, "EventHandlers"):
            return node_cls

        event_handlers: Final[
            list[
                tuple[
                    IntEnum,
                    Callable[
                        [TEvent, TState | None],
                        type | HSMStatus,
                    ],
                ]
            ]
        ] = []
        for name, value in node_cls.EventHandlers.__annotations__.items():
            # Note: value.__args__ = (Literal[TEvent], TState, Return Type)
            event_handlers.append(
                (
                    value.__args__[0].__args__[0],
                    getattr(node_cls.EventHandlers, name),
                )
            )
        node_cls._event_handlers = tuple(event_handlers)
        del event_handlers

        return node_cls


class NodeMeta(_NodeMeta, _ProtocolMeta):
    pass


def hsm_get_path_to_root(
    node: Type[TNode],
) -> tuple[Type[TNode], ...]:
    path: Final[list[Type[TNode]]] = [node]
    while node is not None and node._superstate is not None:  # type: ignore[attr-defined]
        node = node._superstate  # type: ignore[attr-defined]
        path.append(node)

    return tuple(path)


def hsm_get_lca(
    path1: tuple[Type[TNode], ...],
    path2: tuple[Type[TNode], ...],
) -> Type[TNode]:
    for node in path1:
        if node in path2:
            return node

    raise ValueError("No common ancestor found")


def hsm_get_event_handler(
    node: Type[TNode],
    event: TEvent,
) -> Callable[[TEvent, TState | None], Type[TNode] | HSMStatus] | None:
    for e, handler in node._event_handlers:  # type: ignore[attr-defined]
        if event == e:
            return handler  # type: ignore[no-any-return]

    return None
