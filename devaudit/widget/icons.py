"""
Icon generation for DevAudit widgets.

Generates shield icons programmatically in different colors for system tray.
"""

from PIL import Image, ImageDraw
from typing import Tuple


def generate_shield_icon(color: str, size: int = 64) -> Image.Image:
    """
    Generate a shield icon in the specified color.

    Args:
        color: Color name ("green", "yellow", "red", "gray")
        size: Icon size in pixels (default: 64x64)

    Returns:
        PIL Image object
    """
    # Color mapping
    colors = {
        "green": (16, 185, 129),   # Emerald green (#10b981)
        "yellow": (251, 191, 36),  # Amber (#fbbf24)
        "red": (239, 68, 68),      # Red (#ef4444)
        "gray": (156, 163, 175),   # Gray (#9ca3af)
    }

    fill_color = colors.get(color, colors["gray"])

    # Create transparent image
    img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    # Shield path (simplified shield shape)
    # Calculate points for shield
    center_x = size // 2
    top_y = size // 8
    bottom_y = size - size // 8
    width = size * 3 // 4

    # Shield outline points
    shield_points = [
        (center_x - width // 2, top_y),                    # Top left
        (center_x + width // 2, top_y),                    # Top right
        (center_x + width // 2, bottom_y - width // 4),    # Right side
        (center_x, bottom_y),                              # Bottom point
        (center_x - width // 2, bottom_y - width // 4),    # Left side
    ]

    # Draw shield with fill
    draw.polygon(shield_points, fill=fill_color, outline=(0, 0, 0, 0))

    # Add a darker border for better visibility
    border_color = tuple(max(0, c - 40) for c in fill_color)
    draw.polygon(shield_points, outline=border_color + (255,), width=2)

    # Add a small checkmark or exclamation mark in the center
    if color == "green":
        # Draw checkmark
        check_points = [
            (center_x - width // 6, center_x),
            (center_x - width // 12, center_x + width // 8),
            (center_x + width // 4, center_x - width // 8),
        ]
        draw.line(check_points, fill=(255, 255, 255, 200), width=4, joint="curve")
    elif color in ["yellow", "red"]:
        # Draw exclamation mark
        # Vertical line
        draw.line(
            [(center_x, center_x - width // 6), (center_x, center_x + width // 12)],
            fill=(255, 255, 255, 200),
            width=4
        )
        # Dot
        draw.ellipse(
            [
                center_x - 2,
                center_x + width // 8,
                center_x + 2,
                center_x + width // 8 + 4
            ],
            fill=(255, 255, 255, 200)
        )

    return img


def get_icon_for_status(status: str) -> Image.Image:
    """
    Get icon for a given status.

    Args:
        status: Status string ("ok", "warning", "critical", "attention", "unknown", etc.)

    Returns:
        PIL Image object
    """
    status_to_color = {
        "ok": "green",
        "warning": "yellow",
        "critical": "red",
        "attention": "yellow",
        "error": "gray",
        "unknown": "gray",
        "no_scan": "gray",
    }

    color = status_to_color.get(status, "gray")
    return generate_shield_icon(color)


def save_all_icons(output_dir: str = "."):
    """
    Generate and save all icon variations to files.

    Args:
        output_dir: Directory to save icons to
    """
    from pathlib import Path

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)

    colors = ["green", "yellow", "red", "gray"]

    for color in colors:
        icon = generate_shield_icon(color, size=128)  # Higher res for better quality

        # Save as PNG
        icon.save(output_path / f"shield_{color}.png")

        # Also save smaller version for system tray (some platforms need smaller icons)
        icon_small = generate_shield_icon(color, size=32)
        icon_small.save(output_path / f"shield_{color}_small.png")

    print(f"Icons saved to {output_path}")


if __name__ == "__main__":
    # Generate icons if run directly
    save_all_icons("icons")
