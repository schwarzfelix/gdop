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
