import logging
import anywidget
import array
import pathlib
import struct
import traitlets
import json
import glob
import requests
from typing import Any, Optional, TYPE_CHECKING
from luminarycloud.vis.display import DisplayAttributes, ColorMap
from luminarycloud.enum.vis_enums import (
    CameraDirection,
    visquantity_text,
    SceneMode,
    Representation,
    VisQuantity,
)
from luminarycloud._proto.api.v0.luminarycloud.vis import vis_pb2

from luminarycloud_jupyter.interactive_lcvis_widget import InteractiveLCVisWidget, LCVisPlaneWidget
from luminarycloud_jupyter.vis_enums import (
    field_component_to_lcvis,
    representation_to_lcvis,
)

if TYPE_CHECKING:
    # We need to be careful w/ this import for typing otherwise
    # we'll introduce a circular import issue
    from luminarycloud.vis import Scene

base_path = pathlib.Path(__file__).parent / "static"


class LCVisWidget(anywidget.AnyWidget):
    _esm: pathlib.Path = base_path / "lcvis.js"

    # If the frontend widget is up and ready to receive a workspace state
    frontend_ready_for_workspace: bool = False

    # If the workspace execution is complete and the widget is ready
    # to receive other commands.
    workspace_execution_done: bool = False

    # If workspace state was set before the frontend was ready
    # we buffer the command til we get ready_for_workspace from the Wasm
    # Now we support two workspaces: one for isComparator=False, one for isComparator=True
    # TODO: If we plan to support more than 2 scenes to compare, use an index (idx) as the key here.
    buffered_workspaces: dict[bool, dict] = {}

    # Commands we need to buffer up because calls were made
    # before the widget was ready. The normal Jupyter comm stuff
    # doesn't buffer messages before the widget is up, they just get
    # discarded
    buffered_commands: list[dict] = []

    scene_mode: traitlets.Unicode = traitlets.Unicode().tag(sync=True)

    last_screenshot: Optional[bytes] = None

    # The camera look at configuration
    camera_position: traitlets.List = traitlets.List().tag(sync=True)
    camera_look_at: traitlets.List = traitlets.List().tag(sync=True)
    camera_up: traitlets.List = traitlets.List().tag(sync=True)
    camera_pan: traitlets.List = traitlets.List().tag(sync=True)

    # Map of field names to ranges (one-way sync: TypeScript -> Python)
    field_data_map: traitlets.Dict = traitlets.Dict(default_value={}).tag(sync=True)

    # The next free widget ID
    next_widget_id: int = 1

    # Released widget IDs that are available for re-use
    free_widget_ids: list[int] = []

    # Active interactive widgets in the LCVis widget
    lcvis_widgets: dict[int, InteractiveLCVisWidget] = {}

    def __init__(self, scene_mode: SceneMode, **kwargs: Any) -> None:
        super().__init__(**kwargs)
        self.scene_mode = scene_mode
        self.on_msg(self.receive_widget_message)

    # TODO (will): make widget messages that come back be JSON too
    def receive_widget_message(self, widget: Any, content: str, buffers: list[memoryview]) -> None:
        if content == "screenshot_taken":
            self.last_screenshot = buffers[0]
        elif content == "set_scene_mode":
            new_scene_mode = buffers[0].tobytes().decode("utf-8")
            self.scene_mode = new_scene_mode
        elif content == "ready_for_workspace":
            self.frontend_ready_for_workspace = True
            # Send all buffered workspaces if we have them
            if self.buffered_workspaces:
                for is_comparator, workspace in self.buffered_workspaces.items():
                    self.send(
                        {
                            "cmd": workspace["cmd"],
                            "workspaceState": workspace["workspaceState"],
                            "isComparator": is_comparator,
                        },
                        workspace["buffers"],
                    )
        elif content == "workspace_execution_done":
            self.workspace_execution_done = True
            self._send_buffered_commands()
        elif content == "load_wasm":
            # We don't know the name of the wasm file until build
            # since it comes from the npm package
            wasm_file = glob.glob("*.wasm", root_dir=base_path)
            # TODO will: We need some way to report errors back out, these just
            # get lost since its in some message handler.
            if len(wasm_file) == 0:
                raise Exception("Failed to find expected packaged Wasm file")
            wasm = (base_path / wasm_file[0]).read_bytes()
            # Note: When we merge with the buffering PR, this send
            # should not be buffered, b/c the widget is up at this point
            # and sent us this message and we need the wasm there before
            # it can complete loading LCVis and tell us its ready for buffered cmds
            self.send({"cmd": "load_wasm"}, [wasm])
        elif content == "update_widget":
            widget_id: int = struct.unpack("I", buffers[0])[0]
            if widget_id in self.lcvis_widgets:
                self.lcvis_widgets[widget_id]._from_frontend_state(content, buffers[1:])

    def set_workspace_state(
        self,
        render_data_urls: vis_pb2.GetRenderDataUrlsResponse,
        isComparator: bool,
    ) -> None:
        self.workspace_execution_done = False
        workspace_state = json.loads(render_data_urls.workspace_state)

        filter_urls = {}
        filter_data = []
        for i in range(len(render_data_urls.urls.filter_ids)):
            filter_id = render_data_urls.urls.filter_ids[i]
            url = render_data_urls.urls.data_files[i].signed_url
            # TODO: We should send back to the Python side if we're in the
            # frodo env or not, then we could skip fetching data in Python
            # and just fetch it in the FE instead to be more efficient.
            filter_urls[filter_id] = {
                "url": url,
                # What buffer index this filter's data is in
                "bufferId": i,
            }
            # For portability to standalone widget environments we download
            # the render data in Python and send it to the frontend. This
            # avoids the HTTP requests for the render data being blocked due to
            # CORS restrictions when made on the frontend
            # Track which buffer goes to which filter
            data = requests.get(url).content
            filter_data.append(data)

        workspace_state["filters_to_url"] = filter_urls

        if self.frontend_ready_for_workspace:
            self.send(
                {
                    "cmd": "set_workspace_state",
                    "workspaceState": json.dumps(workspace_state),
                    "isComparator": isComparator,
                },
                filter_data,
            )

        # when widget is re-mounted we need to send the workspace state
        self.buffered_workspaces[isComparator] = {
            "cmd": "set_workspace_state",
            "workspaceState": json.dumps(workspace_state),
            "buffers": filter_data,
            "isComparator": isComparator,
        }

    def set_flat_shading(self, flat_shading: bool) -> None:
        """
        Set flat shading for the scene.
        """
        self._send_or_buffer_cmd(
            {
                "cmd": "set_flat_shading",
                "flatShading": flat_shading,
            }
        )

    def take_screenshot(self) -> None:
        self.last_screenshot = None
        self._send_or_buffer_cmd({"cmd": "screenshot"})

    def set_surface_visibility(self, surface_id: str, visible: bool) -> None:
        self._send_or_buffer_cmd(
            {
                # TODO: put these in some shared JSON defs/constants file for cmds?
                "cmd": "set_surface_visibility",
                "surfaceId": surface_id,
                "visible": visible,
            }
        )

    def set_surface_color(self, surface_id: str, color: list[float]) -> None:
        if len(color) != 3:
            raise ValueError("Surface color must be list of 3 RGB floats, in [0, 1]")
        if any(c < 0 or c > 1 for c in color):
            raise ValueError("Surface color must be list of 3 RGB floats, in [0, 1]")
        self._send_or_buffer_cmd(
            {
                # TODO: put these in some shared JSON defs/constants file for cmds
                "cmd": "set_surface_color",
                "surfaceId": surface_id,
            },
            buffers=[array.array("f", color).tobytes()],
        )

    def set_display_attributes(self, object_id: str, attrs: DisplayAttributes) -> None:
        cmd = {
            "cmd": "set_display_attributes",
            "objectId": object_id,
            "visible": attrs.visible,
            "representation": representation_to_lcvis(attrs.representation),
        }
        if attrs.field:
            cmd["field"] = {
                "name": visquantity_text(attrs.field.quantity),
                "component": field_component_to_lcvis(attrs.field.component),
            }
        self._send_or_buffer_cmd(cmd)

    def get_field_range(self, quantity: VisQuantity) -> list[float]:
        """
        Get the field range for a given quantity.
        """
        field_name = visquantity_text(quantity)
        if field_name not in self.field_data_map:
            raise ValueError(f"Field {field_name} not found in field data map")
        return self.field_data_map[field_name]

    def set_display_field(self, object_id: str, field_name: str, comp: int) -> None:
        """
        Directly set the display field for an object via a string name and component.
        Useful for interference scenes that have fields that don't conform to the
        standard names. For example, 'Pressure' versus 'Pressure (Pa)'.
        """
        cmd = {
            "cmd": "set_display_attributes",
            "objectId": object_id,
            "visible": True,
            "representation": representation_to_lcvis(Representation.SURFACE),
        }
        cmd["field"] = {
            "name": field_name,
            "component": comp,
        }
        self._send_or_buffer_cmd(cmd)

    def set_color_map(self, color_map: ColorMap) -> None:
        cmd = {
            "cmd": "set_color_map",
            "field": {
                "name": visquantity_text(color_map.field.quantity),
                "component": field_component_to_lcvis(color_map.field.component),
            },
            "min": color_map.data_range.min_value,
            "max": color_map.data_range.max_value,
        }
        self._send_or_buffer_cmd(cmd)

    def reset_camera(self) -> None:
        self._send_or_buffer_cmd({"cmd": "reset_camera"})

    def set_triad_visible(self, visible: bool) -> None:
        self._send_or_buffer_cmd(
            {
                "cmd": "set_triad_visible",
                "visible": visible,
                "rerender": True,
            }
        )

    def set_camera_orientation(self, cam_dir: CameraDirection) -> None:
        orientation = -1
        if cam_dir == CameraDirection.X_POSITIVE:
            orientation = 0
        elif cam_dir == CameraDirection.X_NEGATIVE:
            orientation = 1
        elif cam_dir == CameraDirection.Y_POSITIVE:
            orientation = 2
        elif cam_dir == CameraDirection.Y_NEGATIVE:
            orientation = 3
        elif cam_dir == CameraDirection.Z_POSITIVE:
            orientation = 4
        elif cam_dir == CameraDirection.Z_NEGATIVE:
            orientation = 5

        if orientation != -1:
            self._send_or_buffer_cmd({"cmd": "set_camera_orientation", "orientation": orientation})

    def add_plane_widget(self) -> LCVisPlaneWidget:
        widget_id = self._next_widget_id()
        self._send_or_buffer_cmd(
            {
                "cmd": "create_widget",
                "type": "plane",
                "id": widget_id,
                "rerender": True,
            }
        )
        # Force rerender as well
        w = LCVisPlaneWidget(self, widget_id)
        self.lcvis_widgets[widget_id] = w
        return w

    def delete_widget(self, widget: InteractiveLCVisWidget) -> None:
        if widget.id in self.lcvis_widgets:
            self._send_or_buffer_cmd(
                {
                    "cmd": "delete_widget",
                    "id": widget.id,
                    "rerender": True,
                }
            )
            del self.lcvis_widgets[widget.id]
            # Recycle the ID
            self.free_widget_ids.append(widget.id)
            # Detach the widget from the Python side scene
            widget.owner = None
            widget.id = -1

    def set_show_widget_controls(self, widget: InteractiveLCVisWidget, show_controls: bool) -> None:
        self._send_or_buffer_cmd(
            {
                "cmd": "set_show_widget_controls",
                "show_controls": show_controls,
                "rerender": True,
                "id": widget.id,
            }
        )

    def update_interactive_widget(self, interactive_widget: InteractiveLCVisWidget) -> None:
        cmd, buffers = interactive_widget._to_frontend_state()
        # Force rerender when updating widget state
        cmd["rerender"] = True
        self._send_or_buffer_cmd(cmd, buffers)

    def _send_or_buffer_cmd(self, cmd: dict, buffers: list[bytes] | None = None) -> None:
        """
        If command-based calls are made before the widget is ready we need
        to buffer them and wait til the widget is ready to receive them. Otherwise,
        the default Jupyter comm support doesn't buffer them and the commands are
        simply discarded.
        """
        if self.workspace_execution_done:
            # If we're sending the command immediately, trigger a re-render
            cmd["rerender"] = True
            self.send(cmd, buffers)
        else:
            # If we're buffering the commands we don't want to render the partially
            # applied state, so force all to be false, we'll send a rerender command
            # at the end of the buffer
            cmd["rerender"] = False
            self.buffered_commands.append({"cmd": cmd, "buffers": buffers})

    def _send_buffered_commands(self) -> None:
        if not self.workspace_execution_done:
            logging.error("Cannot send buffered commands before frontend is ready")
            return

        for cmd in self.buffered_commands:
            self.send(cmd["cmd"], cmd["buffers"])
        # We don't re-render when running buffered commands to not show
        # the intermediate states, now that we've flushed the buffer send an
        # explicit re-render command.
        self.send({"cmd": "render_frame"})
        self.buffered_commands = []

    def _next_widget_id(self) -> int:
        widget_id = -1
        if len(self.free_widget_ids) == 0:
            widget_id = self.next_widget_id
            self.next_widget_id += 1
        else:
            widget_id = self.free_widget_ids[0]
            self.free_widget_ids = self.free_widget_ids[1:]
        return widget_id
