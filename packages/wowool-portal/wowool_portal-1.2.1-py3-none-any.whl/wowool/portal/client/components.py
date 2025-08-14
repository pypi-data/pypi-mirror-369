from dataclasses import dataclass
from typing import Iterator

from wowool.portal.client.portal import Portal


@dataclass
class Component:
    """Represents a component available in the Portal.

    Attributes:
        name (str): The name of the component.
        type (str): The type of the component.
        short_description (str): A brief description of the component.
    """

    name: str
    type: str
    description: str


class Components:
    """A class that provides information about available components in the Portal."""

    def __init__(self, type: str = "", language: str = "", portal: Portal | None = None):
        """Initialize a Components instance.

        Args:
            type (str): The type of components to filter by.
            language (str): The language of components to filter by.
            portal (Portal|None): Connection to the Portal server.
        """
        self._portal = portal or Portal()
        self.type = type
        self.language = language
        self._components = self.get(type=type, language=language)

    def get(self, type: str = "", language: str = "", **kwargs) -> list[Component]:
        """Get components from the Portal.

        Args:
            type (str): The type of components to filter by.
            language (str): The language of components to filter by.
            **kwargs: Additional keyword arguments for the request.

        Returns:
            list[Component]: A list of Component instances.

        Raises:
            ClientError: If the Portal returns an invalid response or timeout occurs.
        """
        components_raw: list[dict[str, str]] = self._portal._service.get(
            url="components/",
            json={
                "type": type,
                "language": language,
            },
            **kwargs,
        ).json()
        return [Component(**c) for c in components_raw]

    def __iter__(self) -> Iterator[Component]:
        """Return an iterator over the components.

        Returns:
            Iterator[Component]: An iterator over the components.
        """
        return iter(self._components)

    def __len__(self):
        """Return the number of components.

        Returns:
            int: The number of components.
        """
        return len(self._components)
