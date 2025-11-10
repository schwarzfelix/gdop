class DisplayConfig():
    def __init__(self):

        # Anchors
        self.showAnchors = True
        self.showAnchorCircles = False
        self.showAnchorNames = False
        self.showAnchorCoordinates = False

        # Tags
        self.showTagTruth = True
        self.showTags = False
        self.showPositionErrorLines = False
        self.showTagNames = False
        self.showTagCoordinates = False
        self.showTagTruthLabels = True

        # Between Anchors and Tags
        self.showTagAnchorLabels = False
        self.showTagAnchorLines = False

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
        self.useStandardAggregationMethod = True