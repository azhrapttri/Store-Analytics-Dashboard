"""
Theme configuration for the DVDRental dashboard.
Provides color palettes for Dark / Light mode and a shared chart styling helper.
"""

import plotly.graph_objects as go

DARK_PALETTE = {
    "bg_grad":     "linear-gradient(135deg, #0A1628 0%, #142347 50%, #1B1733 100%)",
    "text":        "#EAF0FA",
    "muted":       "#9AB0D1",
    "surface":     "rgba(255,255,255,0.05)",
    "surface_2":   "rgba(255,255,255,0.03)",
    "border":      "rgba(249,168,212,0.25)",
    "border_soft": "rgba(249,168,212,0.18)",
    "navy":        "#1E3A8A",
    "navy_2":      "#2E4FB8",
    "pink":        "#F9A8D4",
    "pink_soft":   "#FBCFE8",
    "pink_hot":    "#EC4899",
    "accent_text": "#F9A8D4",
    "kpi_text":    "#FBCFE8",
    "ok":          "#86EFAC",
    "sidebar_bg":  "#0A1628",
    "scrollbar":   "rgba(249,168,212,0.45)",
}

LIGHT_PALETTE = {
    "bg_grad":     "linear-gradient(135deg, #FFF5F8 0%, #FFE9F1 50%, #EEF3FF 100%)",
    "text":        "#1E2A4A",
    "muted":       "#6B7BA8",
    "surface":     "rgba(255,255,255,0.75)",
    "surface_2":   "rgba(255,255,255,0.55)",
    "border":      "rgba(30,58,138,0.22)",
    "border_soft": "rgba(236,72,153,0.20)",
    "navy":        "#1E3A8A",
    "navy_2":      "#3B5BCC",
    "pink":        "#EC4899",
    "pink_soft":   "#F9A8D4",
    "pink_hot":    "#DB2777",
    "accent_text": "#1E3A8A",
    "kpi_text":    "#1E3A8A",
    "ok":          "#16A34A",
    "sidebar_bg":  "#FFE9F1",
    "scrollbar":   "rgba(30,58,138,0.35)",
}


def get_palette(mode: str) -> dict:
    """Return the color palette for the given theme mode ('Dark' or 'Light')."""
    return DARK_PALETTE if mode == "Dark" else LIGHT_PALETTE


def apply_chart_theme(
    fig: go.Figure,
    palette: dict,
    mode: str,
    h: int = 260,
    t: int = 30,
    b: int = 8,
    l: int = 8,
    r: int = 8,
) -> go.Figure:
    """Apply the shared visual theme to a Plotly figure."""
    plot_bg  = "rgba(255,255,255,0.02)" if mode == "Dark" else "rgba(255,255,255,0.55)"
    grid_col = palette["border_soft"]

    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        plot_bgcolor=plot_bg,
        font=dict(family="Inter, sans-serif", color=palette["text"], size=10),
        title=dict(text="", font=dict(size=11, color=palette["accent_text"])),
        height=h,
        margin=dict(t=t, b=b, l=l, r=r),
        legend=dict(bgcolor="rgba(0,0,0,0)", font=dict(size=9)),
        xaxis_title="",
        yaxis_title="",
    )
    fig.update_xaxes(gridcolor=grid_col, linecolor=grid_col, tickfont=dict(size=9), title_text="")
    fig.update_yaxes(gridcolor=grid_col, linecolor=grid_col, tickfont=dict(size=9), title_text="")
    return fig
