class DisplayConfig():
    def __init__(self):

        # Anchors
        self.showAnchors = True
        self.showAnchorCircles = True
        self.showAnchorNames = True
        self.showAnchorCoordinates = False

        # Tags
        self.showTagTruth = True
        self.showTags = True
        self.showPositionErrorLines = True
        self.showTagNames = True
        self.showTagCoordinates = False

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
        self.useBorderRectangleForViewport = False

        # Legend Elements
        self.showLegendAnchors = True
        self.showLegendTags = True
        self.showLegendTagTruth = True
        self.showLegendBorder = True

        # Import Options
        self.useStandardAggregationMethod = True