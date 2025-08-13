from __future__ import annotations

import argparse
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional, Dict, Tuple
import tomllib


@dataclass
class Settings:
    fps: int = 20
    density: float = 1.0
    color: str = "auto"
    seed: Optional[int] = None
    speed: float = 0.75
    # Spawn/scaling configuration
    specials_weights: Dict[str, float] = field(default_factory=lambda: {
        "shark": 1.0,
        "fishhook": 1.0,
        "whale": 1.0,
        "ship": 1.0,
        "ducks": 1.0,
        "dolphins": 1.0,
        "swan": 1.0,
        "monster": 1.0,
        "big_fish": 1.0,
    })
    spawn_start_delay_min: float = 3.0
    spawn_start_delay_max: float = 8.0
    spawn_interval_min: float = 8.0
    spawn_interval_max: float = 20.0
    fish_scale: float = 1.0
    seaweed_scale: float = 1.0
    waterline_top: int = 5
    castle_enabled: bool = True
    chest_enabled: bool = True
    chest_burst_seconds: float = 60.0
    fish_direction_bias: float = 0.5
    fish_speed_min: float = 0.6
    fish_speed_max: float = 2.5
    fish_bubble_min: float = 2.0
    fish_bubble_max: float = 5.0
    fish_turn_enabled: bool = True
    fish_turn_chance_per_second: float = 0.01
    fish_turn_min_interval: float = 6.0
    fish_turn_shrink_seconds: float = 0.35
    fish_turn_expand_seconds: float = 0.35
    fish_count_base: Optional[int] = None
    fish_count_per_80_cols: Optional[float] = None
    fish_y_band: Optional[Tuple[float, float]] = None
    seaweed_count_base: Optional[int] = None
    seaweed_count_per_80_cols: Optional[float] = None
    seaweed_sway_min: float = 0.18
    seaweed_sway_max: float = 0.5
    seaweed_lifetime_min: float = 25.0
    seaweed_lifetime_max: float = 60.0
    seaweed_regrow_delay_min: float = 4.0
    seaweed_regrow_delay_max: float = 12.0
    seaweed_growth_rate_min: float = 6.0
    seaweed_growth_rate_max: float = 12.0
    seaweed_shrink_rate_min: float = 8.0
    seaweed_shrink_rate_max: float = 16.0
    spawn_max_concurrent: int = 1
    spawn_cooldown_global: float = 0.0
    specials_cooldowns: Dict[str, float] = field(default_factory=dict)
    fishhook_dwell_seconds: float = 20.0
    ui_backend: str = "terminal"
    ui_fullscreen: bool = False
    ui_cols: int = 120
    ui_rows: int = 40
    ui_font_family: str = "Menlo"
    ui_font_size: int = 14
    web_open: bool = False
    web_port: int = 8000


def _find_config_paths(override: Optional[Path] = None) -> List[Path]:
    if override is not None:
        if override.exists():
            return [override]
        return [override]
    paths: List[Path] = []
    cwd = Path.cwd()
    paths.append(cwd / ".asciiquarium.toml")
    xdg = os.environ.get("XDG_CONFIG_HOME")
    if xdg:
        paths.append(Path(xdg) / "asciiquarium-redux" / "config.toml")
    home = Path.home()
    paths.append(home / ".config" / "asciiquarium-redux" / "config.toml")
    return [p for p in paths if p.exists()]


def _load_toml(path: Path) -> dict:
    try:
        with path.open("rb") as f:
            return tomllib.load(f)
    except Exception:
        return {}


def load_settings_from_sources(argv: Optional[List[str]] = None) -> Settings:
    s = Settings()
    override_path: Optional[Path] = None
    if argv:
        for i, tok in enumerate(argv):
            if tok == "--config" and i + 1 < len(argv):
                override_path = Path(str(argv[i + 1])).expanduser()
                break
            if tok.startswith("--config="):
                override_path = Path(tok.split("=", 1)[1]).expanduser()
                break

    candidates = _find_config_paths(override_path)
    if override_path is not None and candidates and not candidates[0].exists():
        raise FileNotFoundError(f"Config file not found: {override_path}")
    for p in candidates:
        data = _load_toml(p)
        render = data.get("render", {})
        scene = data.get("scene", {})
        spawn = data.get("spawn", {})
        if "fps" in render:
            s.fps = int(render.get("fps", s.fps))
        if "color" in render:
            s.color = str(render.get("color", s.color))
        if "density" in scene:
            try:
                s.density = float(scene.get("density", s.density))
            except Exception:
                pass
        if "seed" in scene:
            seed_val = scene.get("seed")
            if isinstance(seed_val, int):
                s.seed = seed_val
            elif isinstance(seed_val, str) and seed_val.lower() == "random":
                s.seed = None
        if "speed" in scene:
            try:
                s.speed = float(scene.get("speed", s.speed))
            except Exception:
                pass
        specials = spawn.get("specials")
        if isinstance(specials, dict):
            for k in list(s.specials_weights.keys()):
                v = specials.get(k)
                if isinstance(v, (int, float)):
                    try:
                        s.specials_weights[k] = float(v)
                    except Exception:
                        pass
        for key, attr in [
            ("start_delay_min", "spawn_start_delay_min"),
            ("start_delay_max", "spawn_start_delay_max"),
            ("interval_min", "spawn_interval_min"),
            ("interval_max", "spawn_interval_max"),
            ("fish_scale", "fish_scale"),
            ("seaweed_scale", "seaweed_scale"),
            ("cooldown_global", "spawn_cooldown_global"),
        ]:
            if key in spawn:
                try:
                    setattr(s, attr, float(spawn.get(key)))
                except Exception:
                    pass
        if "max_concurrent" in spawn:
            try:
                s.spawn_max_concurrent = int(spawn.get("max_concurrent"))
            except Exception:
                pass
        per_type = spawn.get("per_type")
        if isinstance(per_type, dict):
            for k, v in per_type.items():
                try:
                    s.specials_cooldowns[k] = float(v)
                except Exception:
                    pass
        if "waterline_top" in scene:
            try:
                s.waterline_top = int(scene.get("waterline_top", s.waterline_top))
            except Exception:
                pass
        if "castle_enabled" in scene:
            try:
                s.castle_enabled = bool(scene.get("castle_enabled"))
            except Exception:
                pass
        if "chest_enabled" in scene:
            try:
                s.chest_enabled = bool(scene.get("chest_enabled"))
            except Exception:
                pass
        if "chest_burst_seconds" in scene:
            try:
                s.chest_burst_seconds = float(scene.get("chest_burst_seconds"))
            except Exception:
                pass
        fish = data.get("fish", {})
        if fish:
            for key, attr in [
                ("direction_bias", "fish_direction_bias"),
                ("speed_min", "fish_speed_min"),
                ("speed_max", "fish_speed_max"),
                ("bubble_min", "fish_bubble_min"),
                ("bubble_max", "fish_bubble_max"),
                ("turn_chance_per_second", "fish_turn_chance_per_second"),
                ("turn_min_interval", "fish_turn_min_interval"),
                ("turn_shrink_seconds", "fish_turn_shrink_seconds"),
                ("turn_expand_seconds", "fish_turn_expand_seconds"),
            ]:
                if key in fish:
                    try:
                        setattr(s, attr, float(fish.get(key)))
                    except Exception:
                        pass
            if "turn_enabled" in fish:
                try:
                    s.fish_turn_enabled = bool(fish.get("turn_enabled"))
                except Exception:
                    pass
            if "y_band" in fish and isinstance(fish.get("y_band"), (list, tuple)):
                try:
                    band = tuple(float(x) for x in fish.get("y_band"))  # type: ignore[arg-type]
                    if len(band) == 2:
                        s.fish_y_band = (band[0], band[1])
                except Exception:
                    pass
            if "count_base" in fish:
                try:
                    s.fish_count_base = int(fish.get("count_base"))
                except Exception:
                    pass
            if "count_per_80_cols" in fish:
                try:
                    s.fish_count_per_80_cols = float(fish.get("count_per_80_cols"))
                except Exception:
                    pass
        seaweed = data.get("seaweed", {})
        if seaweed:
            for key, attr in [
                ("sway_min", "seaweed_sway_min"),
                ("sway_max", "seaweed_sway_max"),
                ("lifetime_min", "seaweed_lifetime_min"),
                ("lifetime_max", "seaweed_lifetime_max"),
                ("regrow_delay_min", "seaweed_regrow_delay_min"),
                ("regrow_delay_max", "seaweed_regrow_delay_max"),
                ("growth_rate_min", "seaweed_growth_rate_min"),
                ("growth_rate_max", "seaweed_growth_rate_max"),
                ("shrink_rate_min", "seaweed_shrink_rate_min"),
                ("shrink_rate_max", "seaweed_shrink_rate_max"),
            ]:
                if key in seaweed:
                    try:
                        setattr(s, attr, float(seaweed.get(key)))
                    except Exception:
                        pass
            if "count_base" in seaweed:
                try:
                    s.seaweed_count_base = int(seaweed.get("count_base"))
                except Exception:
                    pass
            if "count_per_80_cols" in seaweed:
                try:
                    s.seaweed_count_per_80_cols = float(seaweed.get("count_per_80_cols"))
                except Exception:
                    pass
        fishhook = data.get("fishhook", {})
        if isinstance(fishhook, dict):
            if "dwell_seconds" in fishhook:
                try:
                    val = fishhook.get("dwell_seconds")
                    if val is not None:
                        s.fishhook_dwell_seconds = float(val)
                except Exception:
                    pass
        ui = data.get("ui", {})
        if isinstance(ui, dict):
            b = ui.get("backend")
            if isinstance(b, str):
                s.ui_backend = b
            fs = ui.get("fullscreen")
            if isinstance(fs, bool):
                s.ui_fullscreen = fs
            v = ui.get("cols")
            if isinstance(v, int):
                s.ui_cols = max(40, min(300, v))
            v = ui.get("rows")
            if isinstance(v, int):
                s.ui_rows = max(15, min(200, v))
            f = ui.get("font_family")
            if isinstance(f, str):
                s.ui_font_family = f
            v = ui.get("font_size")
            if isinstance(v, int):
                s.ui_font_size = max(8, min(48, v))

        break
    parser = argparse.ArgumentParser(description="Asciiquarium Redux")
    parser.add_argument("--config", type=str, help="Path to a config TOML file")
    parser.add_argument("--fps", type=int)
    parser.add_argument("--density", type=float)
    parser.add_argument("--color", choices=["auto", "mono", "16", "256"])
    parser.add_argument("--seed", type=int)
    parser.add_argument("--speed", type=float)
    parser.add_argument("--backend", choices=["terminal", "tk", "web"])
    parser.add_argument("--open", dest="web_open", action="store_true")
    parser.add_argument("--port", dest="web_port", type=int)
    parser.add_argument("--fullscreen", action="store_true")
    parser.add_argument("--castle", dest="castle_enabled", action="store_true", default=None)
    parser.add_argument("--no-castle", dest="castle_enabled", action="store_false")
    args = parser.parse_args(argv)

    if args.fps is not None:
        s.fps = max(5, min(120, args.fps))
    if args.density is not None:
        s.density = max(0.1, min(5.0, args.density))
    if args.color is not None:
        s.color = args.color
    if args.seed is not None:
        s.seed = args.seed
    if args.speed is not None:
        s.speed = max(0.1, min(3.0, args.speed))
    if args.backend is not None:
        s.ui_backend = args.backend
    if args.fullscreen:
        s.ui_fullscreen = True
    if getattr(args, "castle_enabled", None) is not None:
        s.castle_enabled = bool(args.castle_enabled)
    try:
        if getattr(args, "web_open", False):
            s.web_open = True
        vp = getattr(args, "web_port", None)
        if isinstance(vp, int) and vp:
            s.web_port = vp
    except Exception:
        pass
    return s
