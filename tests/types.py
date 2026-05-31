from collections.abc import Callable

AddStock = Callable[[list[tuple[str, str, int, str | None]]], None]
