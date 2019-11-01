#!/usr/bin/env python
#!/bin/bash
#chmod a+x prepare_data.sh  
"""
Command : prepare_noise_data.py --src [...]/LibriSpeech/data --dst [...]

Replace [...] with appropriate paths
"""

from __future__ import absolute_import, division, print_function, unicode_literals

import argparse
import os
import sys
from pydub import AudioSegment
from pydub.utils import db_to_float
import ffmpeg
import shutil
#from pydub.generators import WhiteNoise
import numpy as np
import soundfile as sf

from pathlib import Path
import subprocess



def findtranscriptfiles(dir):
    files = []
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith(".trans.txt"):
                files.append(os.path.join(dirpath, filename))
    return files

def add_noise(dir,dst):
    files = []
    wrd_file=[]
    id_file=[]
    tkn_file=[]
    count_file =0
    count_wrd =0
    count_id =0
    count_tkn =0
    for dirpath, _, filenames in os.walk(dir):
        for filename in filenames:
            if filename.endswith(os.path.join("%09d" % count_file)+".flac"):
                files.append(os.path.join(dirpath, filename))
                count_file = count_file + 1
            if filename.endswith(os.path.join("%09d" % count_wrd)+".wrd"):
                wrd_file.append(os.path.join(dirpath, filename))
                count_wrd = count_wrd + 1
            if filename.endswith(os.path.join("%09d" % count_id)+".id"):
                id_file.append(os.path.join(dirpath, filename))
                count_id = count_id + 1
            if filename.endswith(os.path.join("%09d" % count_tkn)+".tkn"):
                tkn_file.append(os.path.join(dirpath, filename))
                count_id = count_tkn + 1
    n=len(files)
    count=0
    for i in files:
        if (count <= n):
           # intro=AudioSegment.from_file(i)
           # outro=AudioSegment.from_wav("subway-train-1.wav")
           # outro =WhiteNoise().to_audio_segment(duration=500)
            #op=intro.overlay(outro)
            #outro=outro-20
            #op=intro.overlay(outro,position=200)
            data, samplerate = sf.read(i)
            noise = np.random.normal(0,1,len(data))
            #op=intro.overlay(noise)
            op=data+0.0009*noise
            #op.export(os.path.join(dst, "%09d" % count)+".flac",format="flac")
            sf.write(os.path.join(dst, "%09d" % count)+".flac",op,samplerate)
            count=count+1
        else:
            break
    n=len(wrd_file)
    count=0
    for wrd_n in wrd_file:
        if (count <= n):
            shutil.copy(wrd_n,os.path.join(dst, "%09d" % count)+".wrd")
            count=count+1
        else:
            break

    n=len(id_file)
    count=0
    for id_n in id_file:
        if (count <= n):
            shutil.copy(id_n,os.path.join(dst, "%09d" % count)+".id")
            count=count+1
        else:
            break
    n=len(tkn_file)
    count=0
    for tkn_n in tkn_file:
        if (count <= n):
            shutil.copy(tkn_n,os.path.join(dst, "%09d" % count)+".tkn")
            count=count+1
        else:
            break
                
    

if __name__ == "__main__":
  
    parser = argparse.ArgumentParser(description="Librispeech Dataset creation.")
    parser.add_argument("--src", help="source directory")
    parser.add_argument("--dst", help="destination directory", default="./librispeech")

    args = parser.parse_args()

    assert os.path.isdir(
        str(args.src)
    ), "Librispeech src directory not found - '{d}'".format(d=args.src)
   
    subpaths = ["test-clean","train-clean-100"]

    os.makedirs(args.dst, exist_ok=True)

    for subpath in subpaths:
        src = os.path.join(args.src, subpath)
        dst = os.path.join(args.dst, "random_noisy_data", subpath)
        os.makedirs(dst, exist_ok=True)
        transcripts = []
        assert os.path.exists(src), "Unable to find the directory - '{src}'".format(
            src=src
        )

        sys.stdout.write("analyzing {src}...\n".format(src=src))
        sys.stdout.flush()
        transcriptfiles = findtranscriptfiles(src)
        transcriptfiles.sort()
        sys.stdout.write("writing to {dst}...\n".format(dst=dst))
        sys.stdout.flush()


        add_noise(src,dst) 
               
    #create tokens dictionary
    tkn_file = os.path.join(args.dst, "random_noisy_data", "tokens.txt")
    sys.stdout.write("creating tokens file {t}...\n".format(t=tkn_file))
    sys.stdout.flush()
    with open(tkn_file, "w") as f:
        f.write("|\n")
        f.write("'\n")
        for alphabet in range(ord("a"), ord("z") + 1):
            f.write(chr(alphabet) + "\n")

    sys.stdout.write("Done !\n")
