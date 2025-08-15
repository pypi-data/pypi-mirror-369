import sys
import ctypes
import logging
from ctypes import wintypes, pointer
import re
import tkinter as tk
import tkinter.font as tkfont
# Import the common Windows check function
try:
    from . import is_windows
except ImportError:
    # Fallback for when called directly
    def is_windows():
        return sys.platform == "win32"

class DPIManager:
    """DPI management class for Windows applications."""
    def __init__(self):
        self._dpi_awareness_set = False
        self.logger = logging.getLogger(__name__)
    def _get_hwnd_dpi(self, window_handle):
        """Get DPI information for a window handle."""
        if not is_windows():
            return 96, 96, 1.0
        try:
            # Set process DPI awareness
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(
                    1
                )  # PROCESS_SYSTEM_DPI_AWARE
            except Exception as e:
                self.logger.debug(f"Failed to set process DPI awareness: {e}")
            dpi_100pc = 96  # DPI 96 is 100% scaling
            dpi_type = 0  # MDT_EFFECTIVE_DPI = 0
            win_h = wintypes.HWND(window_handle)
            monitor_handle = ctypes.windll.user32.MonitorFromWindow(
                win_h, wintypes.DWORD(2)  # MONITOR_DEFAULTTONEAREST = 2
            )
            x_dpi = wintypes.UINT()
            y_dpi = wintypes.UINT()
            try:
                ctypes.windll.shcore.GetDpiForMonitor(
                    monitor_handle,
                    dpi_type,
                    pointer(x_dpi),
                    pointer(y_dpi),
                )
                # Get Windows scale factor for additional verification
                try:
                    scale_factor = (
                        ctypes.windll.shcore.GetScaleFactorForDevice(0)
                    )
                    # Convert percentage to decimal (e.g., 200 -> 2.0, 250 ->
                    # 2.5)
                    windows_scale = scale_factor / 100.0
                except Exception as e:
                    self.logger.debug(
                        f"Failed to get Windows scale factor: {e}"
                    )
                    windows_scale = None
                # Calculate scaling factor: current DPI / 96 DPI (100%
                # scaling)
                dpi_scaling = (x_dpi.value + y_dpi.value) / (2 * dpi_100pc)
                # Use the higher of DPI-based scaling or Windows scale factor
                # This helps with displays that report incorrect DPI values
                if windows_scale and windows_scale > dpi_scaling:
                    scaling_factor = windows_scale
                    self.logger.info(
                        f"DPI: Using Windows scale factor {windows_scale} "
                        f"instead of DPI-based {dpi_scaling}"
                    )
                else:
                    scaling_factor = dpi_scaling
                return x_dpi.value, y_dpi.value, scaling_factor
            except Exception as e:
                self.logger.debug(f"Failed to get DPI for monitor: {e}")
                return 96, 96, 1.0  # Assume standard Windows DPI & scaling
        except Exception as e:
            self.logger.debug(f"Failed to get DPI information: {e}")
            return 96, 96, 1.0
    def _scale_geometry_string(self, geometry_string, scale_func):
        """Scale geometry string based on DPI scaling."""
        if not geometry_string:
            return geometry_string
        try:
            # Match pattern "WxH+X+Y"
            pattern = r"(?P<W>\d+)x(?P<H>\d+)\+(?P<X>\d+)\+(?P<Y>\d+)"
            match = re.search(pattern, geometry_string)
            if match:
                w = scale_func(int(match.group("W")))
                h = scale_func(int(match.group("H")))
                x = scale_func(int(match.group("X")))
                y = scale_func(int(match.group("Y")))
                return f"{w}x{h}+{x}+{y}"
            # Match pattern "WxH" only
            pattern = r"(?P<W>\d+)x(?P<H>\d+)"
            match = re.search(pattern, geometry_string)
            if match:
                w = scale_func(int(match.group("W")))
                h = scale_func(int(match.group("H")))
                return f"{w}x{h}"
        except Exception as e:
            self.logger.debug(f"Failed to scale geometry string: {e}")
        return geometry_string
    def _fix_scaling(self, root):
        """Scale fonts on high DPI displays."""
        if not root:
            return
        try:
            scaling = float(root.tk.call("tk", "scaling"))
            # Apply font scaling for all scaling factors, not just > 1.4
            if scaling != 1.0:  # Only when scaling is not 1.0
                for name in tkfont.names(root):
                    font = tkfont.Font(root=root, name=name, exists=True)
                    size = int(font["size"])
                    if size < 0:  # Pixel size - scale proportionally
                        font["size"] = round(size * scaling)
        except Exception as e:
            self.logger.debug(f"Failed to fix scaling: {e}")
    def _patch_widget_methods(self, root):
        """Patch widget methods to handle pad/padding scaling."""
        if not root or not hasattr(root, "DPI_scaling"):
            return
        # Use tk_scaling for widget method patches, not DPI_scaling
        # This ensures proper scaling even when DPI_scaling is 1.0
        try:
            tk_scaling = float(root.tk.call("tk", "scaling"))
            scaling_factor = tk_scaling
        except Exception as e:
            self.logger.debug(f"Failed to get tk scaling: {e}")
            scaling_factor = root.DPI_scaling
        # Patch pack method to scale padx/pady
        original_pack = tk.Widget.pack
        def scaled_pack(self, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "padx" in scaled_kwargs:
                padx = scaled_kwargs["padx"]
                if isinstance(padx, (int, float)):
                    # Only scale if the value is reasonable
                    # (not already scaled)
                    if 0 <= abs(padx) <= 50:  # Normal padding range
                        scaled_kwargs["padx"] = int(padx * scaling_factor)
                    # Otherwise use as-is to avoid double scaling
                elif isinstance(padx, (list, tuple)) and len(padx) == 2:
                    # Only scale if values are reasonable
                    # (not already scaled)
                    if all(0 <= abs(val) <= 50 for val in padx):
                        scaled_kwargs["padx"] = (
                            int(padx[0] * scaling_factor),
                            int(padx[1] * scaling_factor),
                        )
                    # Otherwise use as-is to avoid double scaling
            if "pady" in scaled_kwargs:
                pady = scaled_kwargs["pady"]
                if isinstance(pady, (int, float)):
                    # Only scale if the value is reasonable
                    # (not already scaled)
                    if 0 <= abs(pady) <= 50:  # Normal padding range
                        scaled_kwargs["pady"] = int(pady * scaling_factor)
                    # Otherwise use as-is to avoid double scaling
                elif isinstance(pady, (list, tuple)) and len(pady) == 2:
                    # Only scale if values are reasonable
                    # (not already scaled)
                    if all(0 <= abs(val) <= 50 for val in pady):
                        scaled_kwargs["pady"] = (
                            int(pady[0] * scaling_factor),
                            int(pady[1] * scaling_factor),
                        )
                    # Otherwise use as-is to avoid double scaling
            return original_pack(self, **scaled_kwargs)
        # Patch grid method to scale padx/pady
        original_grid = tk.Widget.grid
        def scaled_grid(self, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "padx" in scaled_kwargs:
                padx = scaled_kwargs["padx"]
                if isinstance(padx, (int, float)):
                    scaled_kwargs["padx"] = int(padx * scaling_factor)
                elif isinstance(padx, (list, tuple)) and len(padx) == 2:
                    scaled_kwargs["padx"] = (
                        int(padx[0] * scaling_factor),
                        int(padx[1] * scaling_factor),
                    )
            if "pady" in scaled_kwargs:
                pady = scaled_kwargs["pady"]
                if isinstance(pady, (int, float)):
                    scaled_kwargs["pady"] = int(pady * scaling_factor)
                elif isinstance(pady, (list, tuple)) and len(pady) == 2:
                    scaled_kwargs["pady"] = (
                        int(pady[0] * scaling_factor),
                        int(pady[1] * scaling_factor),
                    )
            return original_grid(self, **scaled_kwargs)
        # Patch place method to scale x/y coordinates (place doesn't use
        # padx/pady)
        original_place = tk.Widget.place
        def scaled_place(self, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Scale x and y coordinates for place method
            if "x" in scaled_kwargs:
                scaled_kwargs["x"] = int(scaled_kwargs["x"] * scaling_factor)
            if "y" in scaled_kwargs:
                scaled_kwargs["y"] = int(scaled_kwargs["y"] * scaling_factor)
            return original_place(self, **scaled_kwargs)
        # Patch LabelFrame constructor to scale padx/pady
        original_label_frame = tk.LabelFrame.__init__
        def scaled_label_frame_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "padx" in scaled_kwargs:
                padx = scaled_kwargs["padx"]
                if isinstance(padx, (int, float)):
                    scaled_kwargs["padx"] = int(padx * scaling_factor)
                elif isinstance(padx, (list, tuple)) and len(padx) == 2:
                    scaled_kwargs["padx"] = (
                        int(padx[0] * scaling_factor),
                        int(padx[1] * scaling_factor),
                    )
            if "pady" in scaled_kwargs:
                pady = scaled_kwargs["pady"]
                if isinstance(pady, (int, float)):
                    scaled_kwargs["pady"] = int(pady * scaling_factor)
                elif isinstance(pady, (list, tuple)) and len(pady) == 2:
                    scaled_kwargs["pady"] = (
                        int(pady[0] * scaling_factor),
                        int(pady[1] * scaling_factor),
                    )
            return original_label_frame(self, parent, **scaled_kwargs)
        # Patch Frame constructor to scale padx/pady
        original_frame = tk.Frame.__init__
        def scaled_frame_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            if "padx" in scaled_kwargs:
                padx = scaled_kwargs["padx"]
                if isinstance(padx, (int, float)):
                    scaled_kwargs["padx"] = int(padx * scaling_factor)
                elif isinstance(padx, (list, tuple)) and len(padx) == 2:
                    scaled_kwargs["padx"] = (
                        int(padx[0] * scaling_factor),
                        int(padx[1] * scaling_factor),
                    )
            if "pady" in scaled_kwargs:
                pady = scaled_kwargs["pady"]
                if isinstance(pady, (int, float)):
                    scaled_kwargs["pady"] = int(pady * scaling_factor)
                elif isinstance(pady, (list, tuple)) and len(pady) == 2:
                    scaled_kwargs["pady"] = (
                        int(pady[0] * scaling_factor),
                        int(pady[1] * scaling_factor),
                    )
            return original_frame(self, parent, **scaled_kwargs)
        # Patch Button constructor to scale bd only (width/height are character
        # units)
        original_button = tk.Button.__init__
        def scaled_button_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_button(self, parent, **scaled_kwargs)
        # Patch Entry constructor to scale bd only
        # (width is character units and should not be scaled)
        original_entry = tk.Entry.__init__
        def scaled_entry_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width is character units, not pixels - do not scale
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_entry(self, parent, **scaled_kwargs)
        # Patch Label constructor to scale bd/wraplength (width/height are
        # character units)
        original_label = tk.Label.__init__
        def scaled_label_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width and wraplength
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            if "wraplength" in scaled_kwargs:
                scaled_kwargs["wraplength"] = int(
                    scaled_kwargs["wraplength"] * scaling_factor
                )
            # For calendar widgets, don't scale width/height as they are
            # character units
            # and should remain consistent across DPI settings
            return original_label(self, parent, **scaled_kwargs)
        # Patch Text constructor to scale bd only (width/height are character
        # units)
        original_text = tk.Text.__init__
        def scaled_text_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width (Text widget doesn't support wraplength)
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_text(self, parent, **scaled_kwargs)
        # Patch Checkbutton constructor to scale bd (width/height are character
        # units)
        original_checkbutton = tk.Checkbutton.__init__
        def scaled_checkbutton_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_checkbutton(self, parent, **scaled_kwargs)
        # Patch Radiobutton constructor to scale bd (width/height are character
        # units)
        original_radiobutton = tk.Radiobutton.__init__
        def scaled_radiobutton_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_radiobutton(self, parent, **scaled_kwargs)
        # Patch Listbox constructor to scale bd (width/height are character
        # units)
        original_listbox = tk.Listbox.__init__
        def scaled_listbox_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_listbox(self, parent, **scaled_kwargs)
        # Patch Spinbox constructor to scale bd (width is character units)
        original_spinbox = tk.Spinbox.__init__
        def scaled_spinbox_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width is character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_spinbox(self, parent, **scaled_kwargs)
        # Patch Scale constructor to scale bd (width/height are character
        # units)
        original_scale = tk.Scale.__init__
        def scaled_scale_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_scale(self, parent, **scaled_kwargs)
        # Patch Scrollbar constructor to scale bd (width/height are character
        # units)
        original_scrollbar = tk.Scrollbar.__init__
        def scaled_scrollbar_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_scrollbar(self, parent, **scaled_kwargs)
        # Patch Canvas constructor to scale bd (width/height are pixels)
        original_canvas = tk.Canvas.__init__
        def scaled_canvas_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Canvas width and height are pixels, so scale them
            if "width" in scaled_kwargs:
                scaled_kwargs["width"] = int(
                    scaled_kwargs["width"] * scaling_factor
                )
            if "height" in scaled_kwargs:
                scaled_kwargs["height"] = int(
                    scaled_kwargs["height"] * scaling_factor
                )
            # Scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_canvas(self, parent, **scaled_kwargs)
        # Patch Menu constructor to scale bd
        original_menu = tk.Menu.__init__
        def scaled_menu_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_menu(self, parent, **scaled_kwargs)
        # Patch Menubutton constructor to scale bd (width/height are character
        # units)
        original_menubutton = tk.Menubutton.__init__
        def scaled_menubutton_init(self, parent=None, **kwargs):
            scaled_kwargs = kwargs.copy()
            # Note: width and height are character units, not pixels
            # Only scale border width
            if "bd" in scaled_kwargs:
                scaled_kwargs["bd"] = int(scaled_kwargs["bd"] * scaling_factor)
            return original_menubutton(self, parent, **scaled_kwargs)
        # Note: ttk widgets generally handle DPI scaling automatically
        # so we don't patch them to avoid conflicts
        # Apply patches
        tk.Widget.pack = scaled_pack
        tk.Widget.grid = scaled_grid
        tk.Widget.place = scaled_place
        tk.LabelFrame.__init__ = scaled_label_frame_init
        tk.Frame.__init__ = scaled_frame_init
        tk.Button.__init__ = scaled_button_init
        tk.Entry.__init__ = scaled_entry_init
        tk.Label.__init__ = scaled_label_init
        tk.Text.__init__ = scaled_text_init
        tk.Checkbutton.__init__ = scaled_checkbutton_init
        tk.Radiobutton.__init__ = scaled_radiobutton_init
        tk.Listbox.__init__ = scaled_listbox_init
        tk.Spinbox.__init__ = scaled_spinbox_init
        tk.Scale.__init__ = scaled_scale_init
        tk.Scrollbar.__init__ = scaled_scrollbar_init
        tk.Canvas.__init__ = scaled_canvas_init
        tk.Menu.__init__ = scaled_menu_init
        tk.Menubutton.__init__ = scaled_menubutton_init
    def fix_dpi(self, root):
        """Adjust scaling for high DPI displays on Windows."""
        if not is_windows():
            # Non-Windows systems
            root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                root.winfo_id()
            )
            return
        try:
            # For Windows 8.1 and later
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(
                    2
                )  # PROCESS_PER_MONITOR_DPI_AWARE
                scale_factor = ctypes.windll.shcore.GetScaleFactorForDevice(0)
                shcore = True
            except Exception as e:
                self.logger.debug(
                    f"Failed to set process DPI awareness (shcore): {e}"
                )
                # For Windows older than 8.1
                try:
                    ctypes.windll.user32.SetProcessDPIAware()
                    shcore = False
                except Exception as e2:
                    self.logger.debug(
                        f"Failed to set process DPI awareness (user32): {e2}"
                    )
                    return
            if shcore:
                # Set Tk scaling based on Windows DPI settings
                # scale_factor is percentage (e.g., 150 for 150%)
                # Tkinter uses 72 DPI as base, Windows uses 96 DPI
                # Convert: (scale_factor / 100) * (96/72)
                tk_scaling = (scale_factor / 100) * (96 / 72)
                root.tk.call("tk", "scaling", tk_scaling)
                # Also get Windows scale factor for verification
                try:
                    windows_scale_factor = (
                        ctypes.windll.shcore.GetScaleFactorForDevice(0)
                    )
                    windows_scale = windows_scale_factor / 100.0
                    # Use the higher scale factor if Windows reports a higher
                    # value
                    if windows_scale > (scale_factor / 100):
                        tk_scaling = windows_scale * (96 / 72)
                        root.tk.call("tk", "scaling", tk_scaling)
                        self.logger.info(
                            f"DPI: Adjusted Tk scaling to {tk_scaling} "
                            f"based on Windows scale {windows_scale}"
                        )
                except Exception as e:
                    self.logger.debug(
                        f"Failed to get Windows scale factor for "
                        f"verification: {e}"
                    )
                # Get DPI for the monitor
                win_handle = wintypes.HWND(root.winfo_id())
                monitor_handle = ctypes.windll.user32.MonitorFromWindow(
                    win_handle, 2  # MONITOR_DEFAULTTONEAREST = 2
                )
                x_dpi = wintypes.UINT()
                y_dpi = wintypes.UINT()
                ctypes.windll.shcore.GetDpiForMonitor(
                    monitor_handle, 0, pointer(x_dpi), pointer(y_dpi)
                )  # MDT_EFFECTIVE_DPI = 0
                # Store DPI information in the root window
                root.DPI_X = x_dpi.value
                root.DPI_Y = y_dpi.value
                # Calculate scaling factor: current DPI / 96 DPI (100%
                # scaling)
                dpi_scaling = (x_dpi.value + y_dpi.value) / (2 * 96)
                # Get Windows scale factor for verification
                try:
                    windows_scale_factor = (
                        ctypes.windll.shcore.GetScaleFactorForDevice(0)
                    )
                    windows_scale = windows_scale_factor / 100.0
                    # Use the higher of DPI-based scaling or Windows scale
                    # factor
                    if windows_scale > dpi_scaling:
                        root.DPI_scaling = windows_scale
                        self.logger.info(
                            f"DPI: Using Windows scale {windows_scale} "
                            f"instead of DPI-based {dpi_scaling}"
                        )
                    else:
                        root.DPI_scaling = dpi_scaling
                except Exception as e:
                    self.logger.debug(
                        f"Failed to get Windows scale factor for DPI "
                        f"scaling: {e}"
                    )
                    root.DPI_scaling = dpi_scaling
            else:
                root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                    root.winfo_id()
                )
        except Exception as e:
            self.logger.warning(f"Failed to fix DPI: {e}, using fallback")
            # Fallback
            root.DPI_X, root.DPI_Y, root.DPI_scaling = self._get_hwnd_dpi(
                root.winfo_id()
            )
        self._fix_scaling(root)
    def apply_dpi(self, root, *, enable=True):
        """
        Enable DPI awareness and apply scaling to a Tkinter root window.
        This function patches the root window to be DPI-aware by:
        1. Setting process-level DPI awareness
        2. Getting effective DPI for the window's monitor
        3. Setting appropriate Tk scaling
        4. Fixing font scaling issues
        5. Adding DPI scaling utilities to the root
        6. Patching widget methods for pad/padding scaling
        Args:
            root: Tkinter root window
            enable: Whether to enable DPI awareness (default: True)
        Returns:
            dict: DPI information and scaling results
        """
        result = {
            "enabled": enable,
            "platform": "windows" if is_windows() else "non-windows",
            "dpi_awareness_set": False,
            "effective_dpi": 96,
            "scaling_factor": 1.0,
            "tk_scaling": 1.0,
            "hwnd": None,
            "applied_to_windows": [],
        }
        if not enable:
            return result
        if not is_windows():
            return result
        if root is None:
            return result
        try:
            # Apply DPI fix
            self.fix_dpi(root)
            # Get result information
            result["dpi_awareness_set"] = True
            result["effective_dpi"] = (root.DPI_X + root.DPI_Y) / 2
            result["scaling_factor"] = root.DPI_scaling
            result["hwnd"] = root.winfo_id()
            result["tk_scaling"] = float(root.tk.call("tk", "scaling"))
            # Add scaling function
            root.TkScale = lambda v: int(float(v) * root.DPI_scaling)
            # Override geometry method to apply scaling
            original_geometry = root.wm_geometry
            def scaled_geometry(geometry_string=None):
                if geometry_string is None:
                    return original_geometry()
                scaled = self._scale_geometry_string(
                    geometry_string, root.TkScale
                )
                return original_geometry(scaled)
            root.geometry = scaled_geometry
            # Patch widget methods for pad/padding scaling
            self._patch_widget_methods(root)
            # Force update to ensure window is properly initialized
            root.update_idletasks()
            # Record that we applied scaling to this window
            result["applied_to_windows"].append(result["hwnd"])
        except Exception as e:
            result["error"] = str(e)
        return result
    def enable_dpi_awareness(self):
        """
        Enable DPI awareness for the current process.
        This should be called BEFORE creating any Tkinter windows.
        Returns True if DPI awareness was successfully enabled.
        """
        if not is_windows():
            return False
        try:
            # Try SetProcessDpiAwareness for Windows 8.1+
            try:
                ctypes.windll.shcore.SetProcessDpiAwareness(
                    2
                )  # PROCESS_PER_MONITOR_DPI_AWARE
                return True
            except (AttributeError, OSError):
                pass
            # Fallback to SetProcessDPIAware for older Windows
            try:
                ctypes.windll.user32.SetProcessDPIAware()
                return True
            except (AttributeError, OSError):
                pass
        except Exception as e:
            self.logger.debug(f"Failed to enable DPI awareness: {e}")
        return False
    def get_scaling_factor(self, root):
        """Get DPI scaling factor for a root window."""
        if not is_windows() or root is None:
            return 1.0
        try:
            if hasattr(root, "DPI_scaling"):
                return root.DPI_scaling
            else:
                _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
                return scaling_factor
        except Exception as e:
            self.logger.debug(f"Failed to get scaling factor: {e}")
            return 1.0
    def get_effective_dpi(self, root):
        """Get effective DPI for a root window."""
        if not is_windows() or root is None:
            return 96
        try:
            if hasattr(root, "DPI_X") and hasattr(root, "DPI_Y"):
                return (root.DPI_X + root.DPI_Y) / 2
            else:
                dpi_x, dpi_y, _ = self._get_hwnd_dpi(root.winfo_id())
                return (dpi_x + dpi_y) / 2
        except Exception as e:
            self.logger.debug(f"Failed to get effective DPI: {e}")
            return 96
    def logical_to_physical(self, value, *, root=None, scaling_factor=None):
        """Convert logical pixel value to physical pixels."""
        if not is_windows() or not isinstance(value, (int, float)):
            return value
        try:
            if scaling_factor is None:
                if root is None:
                    return value
                if hasattr(root, "DPI_scaling"):
                    scaling_factor = root.DPI_scaling
                else:
                    _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            return type(value)(round(float(value) * float(scaling_factor)))
        except Exception as e:
            self.logger.debug(
                f"Failed to convert logical to physical pixels: {e}"
            )
            return value
    def physical_to_logical(self, value, *, root=None, scaling_factor=None):
        """Convert physical pixel value to logical pixels."""
        if not is_windows() or not isinstance(value, (int, float)):
            return value
        try:
            if scaling_factor is None:
                if root is None:
                    return value
                if hasattr(root, "DPI_scaling"):
                    scaling_factor = root.DPI_scaling
                else:
                    _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            if scaling_factor == 0:
                return value
            return type(value)(round(float(value) / float(scaling_factor)))
        except Exception as e:
            self.logger.debug(
                f"Failed to convert physical to logical pixels: {e}"
            )
            return value
    def scale_font_size(
        self, original_size, root=None, *, scaling_factor=None
    ):
        """Scale a font size based on DPI scaling factor."""
        if not is_windows():
            return original_size
        try:
            if scaling_factor is None:
                if root is None:
                    return original_size
                # Use tk_scaling instead of DPI_scaling for font scaling
                try:
                    scaling_factor = float(root.tk.call("tk", "scaling"))
                except Exception as e:
                    self.logger.debug(
                        f"Failed to get tk scaling for font: {e}"
                    )
                    if hasattr(root, "DPI_scaling"):
                        scaling_factor = root.DPI_scaling
                    else:
                        _, _, scaling_factor = self._get_hwnd_dpi(
                            root.winfo_id()
                        )
            # Handle negative sizes (pixels) vs positive sizes (points)
            if original_size < 0:
                # Negative size = pixel size - scale proportionally
                return round(original_size * scaling_factor)
            else:
                # Positive size = point size - scale proportionally
                return round(original_size * scaling_factor)
        except Exception as e:
            self.logger.debug(f"Failed to scale font size: {e}")
            return original_size
    def get_actual_window_size(self, root):
        """
        Get actual window size information.
        Returns:
            dict: Window size information
        """
        if not is_windows() or root is None:
            return {
                "platform": ("non-windows" if not is_windows() else "no-root"),
                "logical_size": None,
                "physical_size": None,
            }
        try:
            # Get logical size from Tkinter
            geometry = root.geometry()
            match = re.match(r"(\d+)x(\d+)", geometry)
            logical_width = int(match.group(1)) if match else None
            logical_height = int(match.group(2)) if match else None
            # Get scaling factor
            if hasattr(root, "DPI_scaling"):
                scaling_factor = root.DPI_scaling
            else:
                _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            # Calculate physical size
            physical_width = (
                int(logical_width * scaling_factor) if logical_width else None
            )
            physical_height = (
                int(logical_height * scaling_factor)
                if logical_height
                else None
            )
            return {
                "hwnd": root.winfo_id(),
                "logical_size": {
                    "width": logical_width,
                    "height": logical_height,
                    "geometry": geometry,
                },
                "physical_size": {
                    "width": physical_width,
                    "height": physical_height,
                },
                "scaling_factor": scaling_factor,
            }
        except Exception as e:
            return {
                "error": f"Failed to get window size: {str(e)}",
                "logical_size": None,
                "physical_size": None,
            }
    def calculate_dpi_sizes(self, base_sizes, root=None, max_scale=None):
        """Calculate DPI-aware sizes for various UI elements."""
        if not is_windows() or not isinstance(base_sizes, dict):
            return base_sizes
        try:
            if root and hasattr(root, "DPI_scaling"):
                scaling_factor = root.DPI_scaling
            elif root:
                _, _, scaling_factor = self._get_hwnd_dpi(root.winfo_id())
            else:
                scaling_factor = 1.0
            if max_scale and scaling_factor > max_scale:
                scaling_factor = max_scale
            return {
                key: int(value * scaling_factor)
                for key, value in base_sizes.items()
            }
        except Exception as e:
            logger = logging.getLogger(__name__)
            logger.debug(f"Failed to calculate DPI sizes: {e}")
            return base_sizes
# Global instance for backward compatibility
_dpi_manager = DPIManager()
# Backward compatibility functions

def dpi(root, *, enable=True):
    """Backward compatibility function for dpi()."""
    return _dpi_manager.apply_dpi(root, enable=enable)

def enable_dpi_awareness():
    """Backward compatibility function for enable_dpi_awareness()."""
    return _dpi_manager.enable_dpi_awareness()

def enable_dpi_geometry(root):
    """Enable DPI-aware geometry for backward compatibility."""
    return dpi(root)

def get_scaling_factor(root):
    """Backward compatibility function for get_scaling_factor()."""
    return _dpi_manager.get_scaling_factor(root)

def get_effective_dpi(root):
    """Backward compatibility function for get_effective_dpi()."""
    return _dpi_manager.get_effective_dpi(root)

def logical_to_physical(value, *, root=None, scaling_factor=None):
    """Backward compatibility function for logical_to_physical()."""
    return _dpi_manager.logical_to_physical(
        value, root=root, scaling_factor=scaling_factor
    )

def physical_to_logical(value, *, root=None, scaling_factor=None):
    """Backward compatibility function for physical_to_logical()."""
    return _dpi_manager.physical_to_logical(
        value, root=root, scaling_factor=scaling_factor
    )

def scale_font_size(original_size, root=None, *, scaling_factor=None):
    """Backward compatibility function for scale_font_size()."""
    return _dpi_manager.scale_font_size(
        original_size, root=root, scaling_factor=scaling_factor
    )

def get_actual_window_size(root):
    """Backward compatibility function for get_actual_window_size()."""
    return _dpi_manager.get_actual_window_size(root)

def calculate_dpi_sizes(base_sizes, root=None, max_scale=None):
    """Backward compatibility function for calculate_dpi_sizes()."""
    return _dpi_manager.calculate_dpi_sizes(
        base_sizes, root=root, max_scale=max_scale
    )

def scale_icon(icon_name, parent, base_size=24, max_scale=3.0):
    """
    Create a scaled version of a Tkinter icon for DPI-aware sizing.
    Args:
        icon_name (str): Icon identifier (e.g., "error", "info")
        parent: Parent widget
        base_size (int): Base icon size
        max_scale (float): Maximum scaling factor
    Returns:
        str: Scaled icon name or original icon name if scaling fails
    """
    if not is_windows():
        return icon_name
    try:
        scaling = get_scaling_factor(parent)
        if scaling > 1.0:
            # Map icon names to actual Tkinter icon names
            icon_mapping = {
                "error": "::tk::icons::error",
                "info": "::tk::icons::information",
                "warning": "::tk::icons::warning",
                "question": "::tk::icons::question",
            }
            # Get the actual Tkinter icon name
            original_icon = icon_mapping.get(
                icon_name, f"::tk::icons::{icon_name}"
            )
            scaled_icon = f"scaled_{icon_name}_large"
            # Get original icon dimensions (currently not used directly)
            # original_width = parent.tk.call("image", "width", original_icon)
            # original_height = parent.tk.call(
            #     "image", "height", original_icon
            # )
            # Calculate new dimensions
            # Only scale if DPI scaling is significantly higher than 1.0
            if scaling >= 1.25:  # Only scale for 125% DPI or higher
                scale_factor = min(scaling, max_scale)  # Cap at max_scale
            else:
                scale_factor = 1.0  # No scaling for 100% DPI
            # Calculate scaled dimensions (currently not used)
            # new_width = int(original_width * scale_factor)
            # new_height = int(original_height * scale_factor)
            # Create scaled image using Tcl's image scaling
            parent.tk.call("image", "create", "photo", scaled_icon)
            parent.tk.call(
                scaled_icon,
                "copy",
                original_icon,
                "-zoom",
                int(scale_factor),
                int(scale_factor),
            )
            return scaled_icon
    except Exception as e:
        logger = logging.getLogger(__name__)
        logger.debug(f"Failed to scale icon {icon_name}: {e}")
    return icon_name
# Auto DPI scaling placeholders (simplified)

def enable_auto_dpi_scaling(root, *, interval_ms=500, adjust_fonts=True):
    """
    Placeholder for auto DPI scaling (not implemented in simplified
    version).
    """
    return False

def disable_auto_dpi_scaling(root):
    """Placeholder for disabling auto DPI scaling."""
    return False

def is_auto_dpi_scaling_enabled(root):
    """Placeholder for checking auto DPI scaling status."""
    return False
# Widget scaling placeholders (removed complex functionality)

def scale_widget_dimensions(
    widget, root=None, *, scaling_factor=None, exclude_properties=None
):
    """
    Placeholder for widget dimension scaling (not implemented in
    simplified version).
    """
    return {
        "scaled_properties": [],
        "errors": ["Not implemented in simplified version"],
    }

def scale_widget_tree(
    root_widget,
    *,
    scaling_factor=None,
    exclude_properties=None,
    widget_filter=None,
):
    """
    Placeholder for widget tree scaling (not implemented in
    simplified version).
    """
    return {
        "total_widgets": 0,
        "scaled_widgets": 0,
        "widget_results": [],
        "errors": ["Not implemented in simplified version"],
    }

def get_scalable_properties():
    """Placeholder for getting scalable properties."""
    return set()

def add_scalable_property(property_name):
    """Placeholder for adding scalable property."""
    pass

def remove_scalable_property(property_name):
    """Placeholder for removing scalable property."""
    pass
