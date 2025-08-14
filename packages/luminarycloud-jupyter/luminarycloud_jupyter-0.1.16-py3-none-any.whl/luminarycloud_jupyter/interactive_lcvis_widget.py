from abc import ABC, abstractmethod
from typing import TYPE_CHECKING
import struct

if TYPE_CHECKING:
    # We need to be careful w/ this import for typing otherwise
    # we'll introduce a circular import issue
    from luminarycloud_jupyter.lcvis_widget import LCVisWidget
    from luminarycloud.vis import Plane
    from luminarycloud.types import Vector3Like


class InteractiveLCVisWidget(ABC):
    """
    Base class for all Python side representations of the
    interactive LCVis widgets
    """

    owner: "LCVisWidget | None" = None
    id = -1

    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        self.owner = owner
        self.id = id

    def set_show_controls(self, show_controls: bool) -> None:
        if self.owner:
            self.owner.set_show_widget_controls(self, show_controls)

    def remove(self) -> None:
        if self.owner:
            self.owner.delete_widget(self)
            self.owner = None
            self.id = -1

    @abstractmethod
    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        pass

    @abstractmethod
    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        pass


class LCVisPlaneWidget(InteractiveLCVisWidget):
    def __init__(self, owner: "LCVisWidget", id: int) -> None:
        from luminarycloud.vis import Plane

        super().__init__(owner, id)
        self._plane = Plane()

    @property
    def plane(self) -> "Plane":
        return self._plane

    @plane.setter
    def plane(self, new_plane: "Plane") -> None:
        self._plane = new_plane
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def origin(self) -> "Vector3Like":
        return self._plane.origin

    @origin.setter
    def origin(self, origin: "Vector3Like") -> None:
        self._plane.origin = origin
        if self.owner:
            self.owner.update_interactive_widget(self)

    @property
    def normal(self) -> "Vector3Like":
        return self._plane.normal

    @normal.setter
    def normal(self, normal: "Vector3Like") -> None:
        self._plane.normal = normal
        if self.owner:
            self.owner.update_interactive_widget(self)

    def _from_frontend_state(self, msg: str, buffers: list[memoryview]) -> None:
        """
        Update the widget's state based on the parameters from the frontend
        """
        from luminarycloud.types import Vector3

        x, y, z = struct.unpack("fff", buffers[0].tobytes())
        self._plane.origin = Vector3(x, y, z)

        x, y, z = struct.unpack("fff", buffers[1].tobytes())
        self._plane.normal = Vector3(x, y, z)

    def _to_frontend_state(self) -> tuple[dict, list[bytes] | None]:
        """
        Return the message dict and optional data buffers to send to the
        frontend to make the frontend widget match this one
        """
        origin_buf = struct.pack(
            "fff", self._plane.origin[0], self._plane.origin[1], self._plane.origin[2]
        )
        normal_buf = struct.pack(
            "fff", self._plane.normal[0], self._plane.normal[1], self._plane.normal[2]
        )
        return {"cmd": "update_widget", "id": self.id}, [origin_buf, normal_buf]
