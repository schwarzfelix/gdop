class DisplayConfig():
    def __init__(self):

        # Anchors
        self.showAnchors = True
        self.showAnchorCircles = True
        self.showAnchorLabels = True

        # Tags
        self.showTagTruth = True
        self.showTags = True
        self.showTagLabels = True

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