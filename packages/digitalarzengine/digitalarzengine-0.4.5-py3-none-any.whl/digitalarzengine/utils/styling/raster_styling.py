from typing import Any, Mapping, Sequence, Union, Literal, Optional, Dict, List, Tuple
from pydantic import BaseModel
from rio_tiler.colormap import cmap

RGBA = Tuple[int, int, int, int]

# Forward declarations so type hints work
# (adjust imports if these classes live elsewhere)
# from .raster_styling import ContinuousStyle, DiscreteStyle
RasterStyleTypes = Union["ContinuousStyle", "DiscreteStyle"]
StyleLike = Union[Mapping[str, Any], Any]  # dict-like or model instance


class ColorMapBase(BaseModel):
    @staticmethod
    def create_color_map(palette) -> Dict[int, RGBA]:
        if isinstance(palette, dict):
            pairs = list(palette.items())
            iterable = [(int(k), v) for k, v in pairs]
            iterable.sort(key=lambda kv: kv[0])
        elif isinstance(palette, (list, tuple)):
            iterable = list(enumerate(palette))
        elif isinstance(palette, set):
            iterable = list(enumerate(sorted(palette)))
        else:
            raise TypeError("palette must be a dict, list, tuple, or set")

        color_map = {idx: ColorMapBase.hex_to_rgba(hex_color) for idx, hex_color in iterable}
        return color_map

    @staticmethod
    def hex_to_rgba(hex_color: str) -> RGBA:
        h = hex_color.lstrip('#')
        if len(h) == 6:
            h += "FF"
        if len(h) != 8:
            raise ValueError(f"Invalid hex color: {hex_color}")
        return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4, 6))

    # ---------- Type inference helpers ----------
    @staticmethod
    def _has(obj: StyleLike, key: str) -> bool:
        return (isinstance(obj, Mapping) and key in obj) or hasattr(obj, key)

    @staticmethod
    def _get(obj: StyleLike, key: str, default=None):
        if isinstance(obj, Mapping):
            return obj.get(key, default)
        return getattr(obj, key, default)

    @staticmethod
    def infer_style_type(style: StyleLike) -> Literal["discrete", "continuous"]:
        # 1) explicit
        t = ColorMapBase._get(style, "type", None)
        if t in ("discrete", "continuous"):
            return t

        # 2) values => discrete
        vals = ColorMapBase._get(style, "values", None)
        if isinstance(vals, Sequence) and not isinstance(vals, (str, bytes)) and len(vals) >= 2:
            return "discrete"

        # 3) min/max => continuous
        if ColorMapBase._has(style, "min") and ColorMapBase._has(style, "max"):
            return "continuous"

        # 4) palette-based
        pal = ColorMapBase._get(style, "palette", None)
        if isinstance(pal, dict):
            # Dict palettes map codes/breakpoints -> colors ⇒ discrete
            return "discrete"

        if isinstance(pal, (list, tuple, set)):
            # Bare ramps tend to be continuous
            if ColorMapBase._has(style, "min") and ColorMapBase._has(style, "max"):
                return "continuous"
            if isinstance(vals, Sequence) and len(vals) >= 2:
                return "discrete"

        return None


class ContinuousStyle(ColorMapBase):
    """
     🎨 Example 1: Continuous Style
    {
        "type": "continuous",
        "min": 0,
        "max": 100,
        "palette": ["#0000FF", "#00FF00", "#FF0000"]
    }
    """

    type: Optional[Literal["continuous"]] = "continuous"
    min: float
    max: float
    palette: List[str]

    def to_cog_color_map(self) -> cmap:
        """
        :return: cmap as List[Tuple[Tuple[float, float], RGBA]]
        """
        result = []
        color_map = self.create_color_map(self.palette)
        # vmin = float(self.get_first('min', 'min_val'))
        # vmax = float(self.get_first('max', 'max_val'))
        vmin = float(self.min)
        vmax = float(self.max)
        if vmax <= vmin:
            raise ValueError("max must be greater than min for continuous style.")

        n = len(color_map)
        if n == 1:
            # Single color: one full-range bin + overflow with same color
            only = color_map[min(color_map.keys())]
            result.append(((vmin, vmax), only))
            result.append(((vmax, float('inf')), only))
            return result

        # Equal-width bins for the first (n-1) colors
        step = (vmax - vmin) / (n - 1)
        sorted_idxs = sorted(color_map.keys())
        for i in range(n - 1):
            start = vmin + i * step
            end = vmin + (i + 1) * step
            result.append(((start, end), color_map[sorted_idxs[i]]))

        # Overflow bin gets the last color
        result.append(((vmax, float('inf')), color_map[sorted_idxs[-1]]))
        return result


class DiscreteStyle(ColorMapBase):
    type: Optional[Literal["discrete"]] = "discrete"
    values: Optional[List[float]] = None
    labels: Optional[List[str]] = None
    palette: Union[Dict[int, str], List[str]]
    min_val: Optional[float] = None
    max_val: Optional[float] = None

    @staticmethod
    def get_values(palette):
        if isinstance(palette, dict):
            values = sorted(int(k) for k in palette.keys())
        else:
            values = list(range(len(palette)))
        return values

    def get_labels(self) -> List[str]:
        """Return existing labels or generate range labels from values."""
        if self.labels:
            return self.labels

        # Get the breakpoints
        values = self.get_values(self.palette) if self.values is None else self.values
        if len(values) < 2:
            raise ValueError("Cannot generate labels without at least two values.")

        # Generate range labels for each bin + overflow
        labels = []
        for i in range(len(values) - 1):
            labels.append(f"{values[i]} - {values[i + 1]}")
        labels.append(f"{values[-1]}+")  # Overflow bin
        return labels

    def to_cog_color_map(self) -> cmap:
        """
        :return: cmap as List[Tuple[Tuple[float, float], RGBA]]
        """
        result = []
        values = self.get_values(self.palette) if self.values is None else self.values
        color_map = self.create_color_map(self.palette)

        if not values or len(values) < 2:
            raise ValueError("Discrete style requires 'values' with at least two entries.")

        # Adjacent bins between given breakpoints
        for i in range(len(values) - 1):
            start = float(values[i])
            end = float(values[i + 1])
            color = color_map.get(i)
            if color is None:
                color = color_map[max(color_map.keys())]
            result.append(((start, end), color))

        # Overflow bin
        last_idx = len(values) - 1
        overflow_color = color_map.get(last_idx, color_map[max(color_map.keys())])
        result.append(((float(values[-1]), float('inf')), overflow_color))
        return result
