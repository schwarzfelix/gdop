"""
DisplayConfig - Central configuration for GDOP application display settings.

This class provides centralized control over:
- Visibility toggles for UI elements (anchors, tags, lines, etc.)
- Import and trilateration method preferences
- Plot styling parameters (bar label offsets)
- **Font sizes for all plots** (titles, labels, annotations, etc.)

To change font sizes across all plots, modify the fontSize_* attributes in __init__.
The apply_font_sizes() method automatically applies these settings to matplotlib axes.
"""


class DisplayConfig():
    def __init__(self):

        # Anchors
        self.showAnchors = True
        self.showAnchorCircles = False
        self.showAnchorNames = True
        self.showAnchorCoordinates = False

        # Tags
        self.showTagTruth = True
        self.showTags = True
        self.showPositionErrorLines = True
        self.showTagNames = False
        self.showTagCoordinates = False
        self.showTagTruthLabels = True

        # Between Anchors and Tags
        self.showTagAnchorLabels = False
        self.showTagAnchorLines = True

        # Between Anchors
        self.showBetweenAnchorsLabels = False
        self.showBetweenAnchorsLines = False

        # Interaction
        self.rightClickAnchors = True
        self.dragAnchors = True

        # Plots
        self.showTrilatPlot = True
        self.showComparisonPlot = True

        # Border Rectangle
        self.showBorderRectangle = True
        self.useBorderRectangleForViewport = True

        # Legend Elements
        self.showLegendAnchors = True
        self.showLegendTags = False
        self.showLegendTagTruth = True
        self.showLegendBorder = True

        # Import Options
        # Options: "newest", "lowest", "mean", "median", "ask"
        # - "ask": Show dialog to select method at import time
        # - Other values: Use that method directly without asking
        self.aggregationMethod = "ask"

        # Trilateration Options
        # Options: "classical", "best_subset", "nonlinear", "ask"
        # - "ask": Show dialog to select method at import time
        # - "classical": Standard least-squares (fast, but fails with poor anchor geometry)
        # - "best_subset": Selects best 3-anchor subset by condition number (recommended for collinear anchors)
        # - "nonlinear": Nonlinear optimization with centroid start (requires scipy)
        self.trilaterationMethod = "ask"

        # Bar Chart Label Offset
        # Vertical offset (in data coordinates as fraction of y-range) for value labels above bars
        # Increase this value to move labels further above the bars
        self.barLabelOffset = 0.02  # 2% of y-axis range

        # Font Sizes (in points)
        # These control text sizes across all plots
        self.fontSize_title = 24
        self.fontSize_axisLabel = 20
        self.fontSize_tickLabel = 16
        self.fontSize_legend = 16
        self.fontSize_annotation = 16  # For value labels on bars, etc.
        self.fontSize_info = 16  # For info text at bottom of plots

    def apply_font_sizes(self, ax, fig=None):
        """Apply font size settings to a matplotlib axes (and optionally figure).
        
        Args:
            ax: matplotlib axes object
            fig: optional matplotlib figure object (for fig.text elements)
        
        Usage in plot classes:
            config = DisplayConfig()
            config.apply_font_sizes(self.ax, self.fig)
        """
        # Set title font size
        if ax.get_title():
            ax.title.set_fontsize(self.fontSize_title)
        
        # Set axis label font sizes
        ax.xaxis.label.set_fontsize(self.fontSize_axisLabel)
        ax.yaxis.label.set_fontsize(self.fontSize_axisLabel)
        
        # Set tick label font sizes
        ax.tick_params(axis='both', labelsize=self.fontSize_tickLabel)
        
        # Set legend font size if legend exists
        legend = ax.get_legend()
        if legend:
            for text in legend.get_texts():
                text.set_fontsize(self.fontSize_legend)
