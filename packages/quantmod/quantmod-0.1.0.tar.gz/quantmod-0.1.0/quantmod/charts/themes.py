import plotly.graph_objects as go

THEMES = {
    "pearl": {
        "colorscale": "original",
        "linewidth": 1.3,
        "bargap": 0.01,
        "layout": {
            "legend": {"bgcolor": "#F5F6F9", "font": {"color": "#4D5663"}},
            "paper_bgcolor": "#F5F6F9",
            "plot_bgcolor": "#F5F6F9",
            "title": {"font": {"color": "#4D5663"}, "x": 0.5},
            "yaxis": {
                "tickfont": {"color": "#4D5663"},
                "gridcolor": "#E1E5ED",
                "title": {"font": {"color": "#4D5663"}},
                "zerolinecolor": "#E1E5ED",
                "showgrid": True,
            },
            "xaxis": {
                "tickfont": {"color": "#4D5663"},
                "gridcolor": "#E1E5ED",
                "title": {"font": {"color": "#4D5663"}},
                "zerolinecolor": "#E1E5ED",
                "showgrid": True,
            },
        },
        "annotations": {"fontcolor": "#4D5663", "arrowcolor": "#9499A3"},
        "3d": {
            "scene": {
                "yaxis": {
                    "gridcolor": "#9499A3",
                    "zerolinecolor": "#9499A3",
                    "title": {"font": {"color": "#4D5663"}},
                },
                "xaxis": {
                    "gridcolor": "#9499A3",
                    "zerolinecolor": "#9499A3",
                    "title": {"font": {"color": "#4D5663"}},
                },
                "zaxis": {
                    "gridcolor": "#9499A3",
                    "zerolinecolor": "#9499A3",
                    "title": {"font": {"color": "#4D5663"}},
                },
            }
        },
    },
    "henanigans": {
        "colorscale": "original",
        "linewidth": 1.3,
        "bargap": 0.01,
        "layout": {
            "legend": {"bgcolor": "#242424", "font": {"color": "#F4F4F4"}},
            "paper_bgcolor": "#242424",
            "plot_bgcolor": "#242424",
            "title": {"font": {"color": "#F4F4F4"}, "x": 0.5},
            "yaxis": {
                "tickfont": {"color": "#A4A4A4"},
                "gridcolor": "#343434",
                "title": {"font": {"color": "#A4A4A4"}},
                "zerolinecolor": "#444444",
                "showgrid": True,
            },
            "xaxis": {
                "tickfont": {"color": "#A4A4A4"},
                "gridcolor": "#343434",
                "title": {"font": {"color": "#A4A4A4"}},
                "zerolinecolor": "#444444",
                "showgrid": True,
            },
        },
        "annotations": {"fontcolor": "#EBB483", "arrowcolor": "#EBB483"},
        "3d": {
            "scene": {
                "yaxis": {
                    "gridcolor": "#343434",
                    "zerolinecolor": "#343434",
                    "title": {"font": {"color": "#A4A4A4"}},
                },
                "xaxis": {
                    "gridcolor": "#343434",
                    "zerolinecolor": "#343434",
                    "title": {"font": {"color": "#A4A4A4"}},
                },
                "zaxis": {
                    "gridcolor": "#343434",
                    "zerolinecolor": "#343434",
                    "title": {"font": {"color": "#A4A4A4"}},
                },
            }
        },
    },
}

# Custom color scales
COLOR_SCALES = {
    "original": [
        "#FF6B35",
        "#004E89",
        "#00A896",
        "#7209B7",
        "#E63946",
        "#2A9D8F",
        "#F4A261",
        "#6A994E",
        "#FA8072",
        "#87CEEB",
    ]
}


# Create pearl template
def create_pearl_template():
    """Create a proper Plotly template from the theme configuration"""
    theme_config = THEMES["pearl"]["layout"]

    template = go.layout.Template(layout=go.Layout(**theme_config))

    return template


# Create henanigans template
def create_henanigans_template():
    """Create a proper Plotly template from the theme configuration"""
    theme_config = THEMES["henanigans"]["layout"]

    template = go.layout.Template(layout=go.Layout(**theme_config))

    return template


# Function to create any template
def create_template(theme_name):
    """Create a template for any theme"""
    if theme_name not in THEMES:
        raise ValueError(f"Theme '{theme_name}' not found in THEMES")

    theme_config = THEMES[theme_name]["layout"]
    template = go.layout.Template(layout=go.Layout(**theme_config))

    return template
