import ast
import cv2
import numpy as np
from typing import Dict, List, Tuple, Any


class Intensity:
    def __init__(self):
        pass

    # ───────── universal parsers ──────────
    
    def _parse_shapes(self,shapes) -> List[Dict[str, Any]]:
        """
        Accepts either:
        • list/dict objects already
        • a JSON-like string (e.g. '[{"type":"line","x1":10,...}, …]')
        """
        if isinstance(shapes, str):
            shapes = ast.literal_eval(shapes)
        if not isinstance(shapes, (list, tuple)):
            raise ValueError("`shapes` must be a list/tuple or its string representation")
        return list(shapes)

    def _bresenham(self,x1, y1, x2, y2):
        # … unchanged …
        pts, dx, dy = [], abs(x2 - x1), abs(y2 - y1)
        sx, sy = (1, -1)[x1 > x2], (1, -1)[y1 > y2]
        err, x, y = dx - dy, x1, y1
        while True:
            pts.append((x, y))
            if x == x2 and y == y2:
                break
            e2 = 2 * err
            if e2 > -dy:
                err -= dy; x += sx
            if e2 < dx:
                err += dx; y += sy
        return pts

    def _line_peaks(self,gray, p0, p1, win=5, sep=50):
        # … unchanged …
        samples = [(x, y) for x, y in self._bresenham(*p0, *p1)
                   if 0 <= x < gray.shape[1] and 0 <= y < gray.shape[0]]
        if len(samples) < 3:
            return [], []
        vals = np.array([gray[y, x] for x, y in samples], np.float32)
        win = max(3, (win // 2) * 2 + 1)
        smooth = np.convolve(vals, np.ones(win) / win, mode="same")
        grad = np.zeros_like(smooth)
        grad[1:-1] = 0.5 * (smooth[2:] - smooth[:-2])
        m = win // 2 + 1
        core = range(m, len(samples) - m) if len(samples) > 2 * m else range(len(samples))
        pos = sorted(((i, grad[i]) for i in core if grad[i] > 0),
                     key=lambda t: t[1], reverse=True)
        neg = sorted(((i, grad[i]) for i in core if grad[i] < 0),
                     key=lambda t: t[1])

        def greedy(cands):
            keep = []
            for idx, _ in cands:
                if all(abs(idx - k) > sep for k in keep):
                    keep.append(idx)
            return [samples[i] for i in keep]

        return greedy(pos), greedy(neg)

    # ───────── peak-extraction API ──────────
    def d2l(self, image: np.ndarray, shapes, win=5, sep=50):
        shapes = self._parse_shapes(shapes)             # <── new
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        out = {}
        for i, sh in enumerate(shapes):
            if str(sh.get("type", "")).lower() != "line":
                continue
            p0, p1 = (int(sh["x1"]), int(sh["y1"])), (int(sh["x2"]), int(sh["y2"]))
            out[i], _ = self._line_peaks(gray, p0, p1, win, sep)
        return out

    def l2d(self, image: np.ndarray, shapes, win=5, sep=50):
        shapes = self._parse_shapes(shapes)             # <── new
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        out={}
        for i, sh in enumerate(shapes):
            if str(sh.get("type", "")).lower() != "line":
                continue
            p0, p1 = (int(sh["x1"]), int(sh["y1"])), (int(sh["x2"]), int(sh["y2"]))
            _, out[i] = self._line_peaks(gray, p0, p1, win, sep)
        return out

    def d2l2d(self, image: np.ndarray, shapes, win=5, sep=50):
        shapes = self._parse_shapes(shapes)             # <── new
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        out: Dict[int, Dict[str, List[Tuple[int, int]]]] = {}
        for i, sh in enumerate(shapes):
            if str(sh.get("type", "")).lower() != "line":
                continue
            p0, p1 = (int(sh["x1"]), int(sh["y1"])), (int(sh["x2"]), int(sh["y2"]))
            d2l, l2d = self._line_peaks(gray, p0, p1, win, sep)
            out[i] = {"d2l": d2l, "l2d": l2d}
        return out

    # ───────── selectors (unchanged) ─────────
    def select_peak_single(self,peaks_dict, line_idx: int, peak_idx: int = 0):
        pts = peaks_dict.get(line_idx)
        if pts is None:
            raise KeyError(f"Line {line_idx} not found")
        if not (0 <= peak_idx < len(pts)):
            raise IndexError("Peak index out of range")
        point = pts[peak_idx]
        return point

    def select_peak_pair(self,peaks_dict, line_idx: int, idx_d2l: int = 0, idx_l2d: int = 0):
        entry = peaks_dict.get(line_idx)
        if entry is None:
            raise KeyError(f"Line {line_idx} not found")
        d2l_pts, l2d_pts = entry["d2l"], entry["l2d"]
        if not (0 <= idx_d2l < len(d2l_pts)) or not (0 <= idx_l2d < len(l2d_pts)):
            raise IndexError("Peak indices out of range")
        points = d2l_pts[idx_d2l], l2d_pts[idx_l2d]
        return points

    # ───────── point-annotation helper ─────────
    def annotate_point(self,image: np.ndarray, pt) -> np.ndarray:
        """
        Draw a red dot (radius 5) at `pt`.  
        `pt` may be (x, y) **or** the string "(x, y)".
        """
        if isinstance(pt, str):
            pt = ast.literal_eval(pt)
        if not (isinstance(pt, (tuple, list)) and len(pt) == 2):
            raise ValueError("`pt` must be (x, y) or its string representation")
        out = image.copy()
        cv2.circle(out, (int(pt[0]), int(pt[1])), 5, (0, 0, 255), -1)
        return out
