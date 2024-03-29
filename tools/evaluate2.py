# need numpy==1.23.1
import os
import subprocess
import sys
import glob
from tools.preprocess import get_mel
import numpy as np
import torch
from argparse import ArgumentParser
from tools.preprocess import MAX_WAV_VALUE, get_mel, normalize
import os
from pathlib import Path
from mel_cepstral_distance import get_metrics_wavs, get_metrics_mels
from glob import glob
#import torchcrepe
import torch
import scipy.stats
from misc.stft_loss import MultiResolutionSTFTLoss
import librosa
import torch

def mean_confidence_interval(data, confidence=0.95):
    a = 1.0 * np.array(data)
    n = len(a)
    m, se = np.mean(a), scipy.stats.sem(a)
    h = se * scipy.stats.t.ppf((1 + confidence) / 2., n-1)
    return m, h

def main(args):
    mcds = []
    mstft = []
    pitches = []
    periodicities = []
    sr = 22050
    mstft_loss = MultiResolutionSTFTLoss()

    for fname in glob(os.path.join(args.sdir, f"{args.prefix}*.wav")):
        swav, _ = librosa.load(fname, sr=sr, mono=True)
        owav, _ = librosa.load(os.path.join(args.odir, Path(fname).name), sr=sr, mono=True)
        owav = owav[:swav.shape[0]]
        #print(f"swav: {swav.shape}")
        #print(f"owav: {owav.shape}")

        mcd, penalty, _ = get_metrics_wavs(Path(fname), 
            Path(os.path.join(args.odir, Path(fname).name)))

        stft, _ = mstft_loss(torch.from_numpy(swav).unsqueeze(0), torch.from_numpy(owav).unsqueeze(0))

        mcds.append(mcd)
        mstft.append(stft.squeeze().numpy())

        '''
        audio1, sr1 = torchcrepe.load.audio(fname)
        audio2, sr2 = torchcrepe.load.audio(os.path.join(args.odir, Path(fname).name))

        if audio1.shape[1] > audio2.shape[1]:
            audio1 = audio1[:,:audio2.shape[1]]
        
        if audio2.shape[1] > audio1.shape[1]:
            audio2 = audio2[:,:audio1.shape[1]]

        pitch1, periodicity1 = torchcrepe.predict(audio1, sr1, 256, 50, 550,
                           'full', return_periodicity=True, batch_size=1024,
                           device='cuda:0')
        
        pitch2, periodicity2 = torchcrepe.predict(audio2, sr2, 256, 50, 550,
                           'full', return_periodicity=True, batch_size=1024,
                           device='cuda:0')

        pitches.append(torch.abs(torch.mean(1200 * torch.log2(pitch2 / pitch1))).cpu().numpy())
        periodicities.append(torch.sqrt(torch.nn.functional.mse_loss(periodicity1, periodicity2)).cpu().numpy())
        '''
    
    m_mcd = mean_confidence_interval(mcds)
    m_mstft = mean_confidence_interval(mstft)
    #m_pitches = mean_confidence_interval(pitches)
    #m_periodicities = mean_confidence_interval(periodicities)

    print(f"MCD: {m_mcd[0]} \u00b1 {m_mcd[1]}")
    print(f"MSTFT: {m_mstft[0]} \u00b1 {m_mstft[1]}")
    #print(f"Pitch: {m_pitches[0]} \u00b1 {m_pitches[1]}")
    #print(f"Periodicity: {m_periodicities[0]} \u00b1 {m_periodicities[1]}\n")

if __name__ == '__main__':
    parser = ArgumentParser(description='Calculate MCD')
    parser.add_argument('--sdir', help='Synthetic directory of waveform')
    parser.add_argument('--odir', help='Original directory of waveform')
    parser.add_argument('--sr', type=int, default=22050, help='Sampling rate')
    parser.add_argument('--prefix', default='LJ', help='Prefix')
    
    main(parser.parse_args())
