from models.diffwave import DiffWave
from models.hifidiff import HifiDiff
from models.hifidiffv2 import HifiDiffV2
from models.hifidiffv3 import HifiDiffV3
from models.wavegrad import WaveGrad

def build_model(params):
    if params.model == 1:
        model = DiffWave(params)
    elif params.model == 2:
        model = HifiDiff(params)
    elif params.model == 3:
        model = HifiDiffV2(params)
    elif params.model == 4:
        model = HifiDiffV3(params)
    elif params.model == 99:
        model = WaveGrad(params)

    #assert model is None

    return model