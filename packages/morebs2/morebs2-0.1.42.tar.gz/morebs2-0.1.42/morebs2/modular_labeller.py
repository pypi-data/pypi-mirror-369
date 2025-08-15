from .relevance_functions import *

class LabelDeltaPattern:

    def __init__(self, tickLength, deviationPr, deviationRange, labelRange,startLabel):
        assert len(labelRange) == 2 and labelRange[1] >= labelRange[0] 
        assert startLabel >= labelRange[0] and startLabel <= labelRange[1]
                
        self.tickLength = tickLength
        self.deviationPr = deviationPr
        self.deviationRange = deviationRange
        self.labelRange = labelRange
        self.label = startLabel
        self.tick = 1
        return

    def output_label(self):
        self.tick = self.tick % self.tickLength
        if self.tick == 0:
            self.label = self.labelRange[0] + (self.label + 1) % (self.labelRange[1] - self.labelRange[0])
        self.tick += 1

        if random.random() < self.deviationPr:
            return self.deviated_label()
        return self.label

    def deviated_label(self):
        dc = int(random.uniform(self.deviationRange[0],self.deviationRange[1] + 1))
        return self.labelRange[0] + (self.label + dc) % (self.labelRange[1] - self.labelRange[0])

class ModularLabeller:

    def __init__(self,ldp):
        assert type(ldp) == LabelDeltaPattern, "invalid ldp"
        self.ldp = ldp

    def label(self, p):
        return np.array(list(p) + [self.ldp.output_label()])

def rch_modular_labeller_1(ldp):

    ml = ModularLabeller(ldp)

    def qf(v):
        return ml.label(v)

    rch = RChainHead()
    kwargs = ['nr',qf]
    rch.add_node_at(kwargs)
    return rch 