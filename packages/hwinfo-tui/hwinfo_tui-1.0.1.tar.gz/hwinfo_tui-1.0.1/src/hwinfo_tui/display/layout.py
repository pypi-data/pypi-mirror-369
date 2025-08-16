"""Layout management for the HWInfo TUI display."""

from __future__ import annotations

import os
from typing import Any

from rich.console import Console, Group
from rich.layout import Layout
from rich.text import Text

from ..data.sensors import Sensor, SensorGroup
from ..utils.stats import SensorStats
from .chart import SensorChart
from .table import CompactTable, StatsTable


class HWInfoLayout:
    """Main layout manager for the HWInfo TUI."""

    def __init__(self, console: Console) -> None:
        """Initialize the layout manager."""
        self.console = console
        self.stats_table = StatsTable(console)
        self.compact_table = CompactTable(console)
        self.chart = SensorChart()

        # Layout components (header-less)
        self.root_layout = Layout()
        self.body_layout = Layout()

        # Setup layout structure (no header, no footer)
        self.root_layout = self.body_layout

        # State
        self.paused = False
        self.compact_mode = False
        self.current_theme = "default"

        # Color management - improved colors for better terminal visibility
        self.rgb_colors = [
            (255, 100, 100),   # Bright red
            (100, 255, 100),   # Bright green
            (100, 150, 255),   # Bright blue
            (255, 255, 100),   # Bright yellow
            (255, 100, 255),   # Bright magenta
            (100, 255, 255),   # Bright cyan
            (255, 180, 100),   # Orange
            (180, 100, 255),   # Purple
        ]
        self.sensor_colors: dict[str, tuple[int, int, int]] = {}  # Current sensor to RGB color mapping

    def get_terminal_size(self) -> tuple[int, int]:
        """Get current terminal size."""
        try:
            size = os.get_terminal_size()
            return size.columns, size.lines
        except OSError:
            return 80, 24  # Default fallback

    def should_use_compact_mode(self) -> bool:
        """Determine if compact mode should be used."""
        width, height = self.get_terminal_size()
        return width < 100 or height < 20

    def _assign_sensor_colors(self, sensors: dict[str, Sensor]) -> None:
        """Assign RGB colors to sensors deterministically based on sensor names."""
        # Get all sensor names and sort them for consistent ordering
        sensor_names = sorted(sensors.keys())

        # Clear previous mappings
        self.sensor_colors = {}

        # Assign RGB colors based on position in sorted list
        for i, sensor_name in enumerate(sensor_names):
            rgb_color = self.rgb_colors[i % len(self.rgb_colors)]
            self.sensor_colors[sensor_name] = rgb_color

            # Also assign the color to the sensor info for easy access
            if isinstance(sensors[sensor_name], Sensor):
                sensors[sensor_name].info.color = f"rgb({rgb_color[0]},{rgb_color[1]},{rgb_color[2]})"

        # Log color assignments for debugging
        import logging
        logger = logging.getLogger(__name__)
        logger.info(f"Color assignments: {self.sensor_colors}")

    def update_layout(
        self,
        sensors: dict[str, Sensor],
        sensor_groups: list[SensorGroup],
        stats: dict[str, SensorStats],
        time_window: int,
        refresh_rate: float,
        csv_path: str
    ) -> Layout:
        """Update the complete layout with current data."""
        # Determine display mode
        self.compact_mode = self.should_use_compact_mode()
        width, height = self.get_terminal_size()

        # Assign colors to sensors
        self._assign_sensor_colors(sensors)

        # Update body based on mode (no header)
        if self.compact_mode:
            self._update_compact_body(sensors, stats, time_window)
        else:
            self._update_full_body(sensors, sensor_groups, stats, time_window, width, height)

        return self.root_layout

    def _update_header(self, csv_path: str, sensor_count: int, time_window: int, refresh_rate: float) -> None:
        """Update the header layout."""
        status_items = []

        # File info
        filename = csv_path.split('/')[-1] if '/' in csv_path else csv_path.split('\\')[-1]
        status_items.append(f"[blue]File:[/blue] {filename}")

        # Sensor count
        status_items.append(f"[blue]Sensors:[/blue] {sensor_count}")

        # Time window
        time_str = self._format_time_duration(time_window)
        status_items.append(f"[blue]Window:[/blue] {time_str}")

        # Refresh rate
        status_items.append(f"[blue]Rate:[/blue] {refresh_rate}s")

        # Pause status
        if self.paused:
            status_items.append("[yellow]PAUSED[/yellow]")

        # Compact mode indicator
        if self.compact_mode:
            status_items.append("[dim]Compact[/dim]")

        " • ".join(status_items)
        # Note: header_layout not implemented in header-less design
        # self.header_layout.update(Text(header_text, style="bold"))

    def _update_full_body(
        self,
        sensors: dict[str, Sensor],
        sensor_groups: list[SensorGroup],
        stats: dict[str, SensorStats],
        time_window: int,
        width: int,
        height: int
    ) -> None:
        """Update body layout for full display mode."""
        # Calculate available space for body (no header)
        available_height = height - 1  # Account for minimal padding

        # Split body into table and chart sections - minimize table, maximize chart
        table_height = min(len(stats) + 3, max(6, available_height // 6))  # Compact table, at least 6 lines, max 1/6 of space
        chart_height = available_height - table_height

        table_layout = Layout(size=table_height)
        chart_layout = Layout(size=chart_height)

        self.body_layout.split_column(table_layout, chart_layout)

        # Create chart mixin with color information
        chart_mixin = self.chart.create_chart(
            sensors, sensor_groups, time_window, sensor_colors=self.sensor_colors
        )

        # Update table with color information
        table = self.stats_table.create_table(stats, sensor_groups, time_window, self.sensor_colors)
        table_layout.update(table)

        chart_layout.update(chart_mixin)

    def _update_compact_body(
        self,
        sensors: dict[str, Sensor],
        stats: dict[str, SensorStats],
        time_window: int
    ) -> None:
        """Update body layout for compact display mode."""
        # In compact mode, show table only or simple chart
        width, height = self.get_terminal_size()

        if height < 15:
            # Very small terminal - table only
            table = self.compact_table.create_table(stats, self.sensor_colors)
            self.body_layout.update(table)
        else:
            # Small terminal - compact table + mini chart
            table_height = min(len(stats) + 3, height // 2)

            table_layout = Layout(size=table_height)
            chart_layout = Layout()

            self.body_layout.split_column(table_layout, chart_layout)

            # Compact table
            table = self.compact_table.create_table(stats, self.sensor_colors)
            table_layout.update(table)

            # Mini chart (no panel border)
            sensor_groups = self._create_sensor_groups(sensors)
            chart_mixin = self.chart.create_chart(
                sensors, sensor_groups, time_window, sensor_colors=self.sensor_colors
            )

            chart_layout.update(chart_mixin)

    def _update_footer(self, stats: dict[str, SensorStats], sensor_groups: list[SensorGroup]) -> None:
        """Update the footer layout."""
        footer_content = []

        # Status indicators
        status_text = self.stats_table.create_status_indicators(stats)
        footer_content.append(status_text)

        # Control hints
        controls = [
            "[green]Q[/green]:Quit",
            "[green]Space[/green]:Pause",
            "[green]R[/green]:Reset"
        ]

        if not self.compact_mode:
            controls.extend([
                "[green]C[/green]:Theme",
                "[green]+/-[/green]:Zoom"
            ])

        controls_text = Text(" • ".join(controls), style="dim")
        footer_content.append(Text(""))  # Spacer
        footer_content.append(controls_text)

        Group(*footer_content)
        # Note: footer_layout not implemented in header-less design
        # self.footer_layout.update(Panel(footer_group, style="dim"))

    def _create_sensor_groups(self, sensors: dict[str, Sensor]) -> list[SensorGroup]:
        """Create sensor groups from sensors dictionary."""
        from ..utils.units import UnitFilter
        unit_filter = UnitFilter()
        return unit_filter.create_sensor_groups(sensors)

    def _format_time_duration(self, seconds: int) -> str:
        """Format time duration for display."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            return f"{minutes}m"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            if minutes == 0:
                return f"{hours}h"
            else:
                return f"{hours}h{minutes}m"

    def toggle_pause(self) -> bool:
        """Toggle pause state and return new state."""
        self.paused = not self.paused
        return self.paused

    def set_theme(self, theme: str) -> None:
        """Set the display theme."""
        self.current_theme = theme
        # Theme changes would be applied to chart and table styling

    def get_layout_info(self) -> dict[str, Any]:
        """Get information about the current layout."""
        width, height = self.get_terminal_size()
        return {
            "terminal_size": (width, height),
            "compact_mode": self.compact_mode,
            "paused": self.paused,
            "theme": self.current_theme
        }
