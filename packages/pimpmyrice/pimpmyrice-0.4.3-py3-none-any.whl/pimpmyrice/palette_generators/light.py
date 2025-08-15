from pathlib import Path

from pimpmyrice.color_extract import extract_colors
from pimpmyrice.colors import Color, Palette


async def gen_palette(image_path: Path) -> Palette:
    colors_with_count = extract_colors(image_path)
    # TODO use count

    by_vibrancy = sorted(
        [color for color, count in colors_with_count],
        key=lambda c: c.hsv_tuple()[1] + (c.hsv_tuple()[2]),
        reverse=True,
    )

    normal = colors_with_count[0][0].adjusted(max_sat=10, min_val=95)

    # TODO contrast with normal
    primary = by_vibrancy[0].adjusted(min_sat=50, max_val=40)
    secondary = by_vibrancy[1].adjusted(min_sat=50, max_val=40)

    term: dict[str, Color] = {}

    term["color0"] = normal

    # TODO contrast based on hue
    for i in range(1, 8):
        term[f"color{i}"] = (
            primary.adjusted(hue=f"+{50 * (i - 1)}")
            .contrasting(normal)
            .adjusted(sat=100, val=40)
        )

    # term["color8"] = normal.adjusted(val="+80")

    for i in range(8, 15):
        term[f"color{i}"] = term[f"color{i - 8}"].adjusted(sat="-50", val="+10")

    term["color15"] = normal.contrasting().adjusted(max_sat=20)

    palette = {
        "term": term,
        "normal": {"bg": normal, "fg": normal.contrasting().adjusted(max_sat=20)},
        "primary": {"bg": primary, "fg": primary.contrasting()},
        "secondary": {"bg": secondary, "fg": secondary.contrasting()},
    }

    p = Palette(**palette)  # type: ignore
    return p
