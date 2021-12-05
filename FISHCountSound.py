# -*- coding: utf-8 -*-
"""
Created on Sat Jun  2 13:31:41 2018

@author: Roberto

Tones generated with Audacity, sine  wave, 50 ms sound + 20 ms silence
Frequency (Hz) gotten from: http://www.szynalski.com/tone-generator/

"""

import wave
from PyQt5.QtMultimedia import QSound
from HelperFunctions import trg_to_tuples

sounddir = 'sound/'

class Sound(object):
    def __init__(self, has_sound, soundtype, target_strings):
        # targets = ['2R2G', '1R1G2F', ...] in order
        self.basenotes  = dict([(note+'5', sounddir+note+'5.wav') for note in 'ABCDEFG'])
        self.autotrg = {'R': 'C5', # red
                        'G': 'D5', # green
                        'A': 'E5', # aqua
                        'B': 'F5', # blue
                        'F': 'G5', # fusion
                        'U': 'A5', # custom_1
                        'V': 'B5'  # custom_2
                        }
        self.attrib_wavs(has_sound, soundtype, target_strings)

        
    def attrib_wavs(self, has_sound, soundtype, target_strings):
        self.silence = QSound(sounddir+"silence_20ms.wav")
        self.start = self.silence

        if not has_sound:
            self.target_wavs = [self.silence for i in range(6)]
            self.error = self.silence
            self.success = self.silence
            self.finished = self.silence
        else:
            self.error = QSound(self.join_wav([sounddir+"F4.wav" for i in range(3)], sounddir+'error.wav'))
            self.success = QSound(self.join_wav([sounddir+"E6.wav" for i in range(2)], sounddir+'success.wav'))
            self.finished = QSound(self.join_wav([sounddir+"E6.wav" for i in range(5)], sounddir+'finished.wav'))
            if soundtype == 0:
                self.target_wavs = [QSound(self.basenotes['A5']) for i in range(6)]
            elif soundtype == 1:
                self.target_wavs = [QSound(self.basenotes[letter+'5']) for letter in 'CDEFGA']
            elif soundtype == 3:
                self.target_wavs = [QSound(sounddir+'smb_coin.wav') for i in range(6)]
                self.error = QSound(sounddir+"smb_bump.wav")
                self.success = QSound(sounddir+"smb_jump-small.wav")
                self.finished = QSound(sounddir+"smb_stage_clear.wav")
                self.start = QSound(sounddir+"overworld_start.wav")
                self.play_start()
            else:
                self.target_wavs = [self.silence for i in range(6)]
                for target_no, target_string in enumerate(target_strings):
                    if target_string != 'n/a':
                        self.set_wav(target_no, target_string)
                    else:
                        self.target_wavs[target_no] = self.silence


    def play(self, target_no):
        self.target_wavs[target_no].play()


    def play_error(self):
        self.error.play()
        
        
    def play_success(self):
        self.success.play()


    def play_finished(self):
        self.finished.play()
        
    def play_start(self):
        self.start.play()


    def set_wav(self, target_no, target_string):
            wavfile = self.create_target_wav(target_no, target_string)
            self.target_wavs[target_no] = QSound(wavfile)


    def create_target_wav(self, target_no, target_string):
        notes = trg_to_tuples(target_string)
        return self.join_notes(target_no, notes)
        

    def join_notes(self, target_no, notes):
        #notes = [(2, 'C'), (2, 'D')]
        # part of the `wave`library code by Stack Overflow user 'tom10'
        # https://stackoverflow.com/questions/2890703/how-to-join-two-wav-files-using-python
        infiles = []
        for repetitions, note in notes:
            for reps in range(repetitions):
                infiles.append(self.basenotes[self.autotrg[note]])
        outfile = sounddir+"target_"+str(target_no)+"_sound.wav"
        self.join_wav(infiles, outfile)
        return outfile


    def join_wav(self, infiles, outfile):
        
        data= []
        for infile in infiles:
            w = wave.open(infile, 'rb')
            data.append([w.getparams(), w.readframes(w.getnframes())])
            w.close()
        
        output = wave.open(outfile, 'wb')
        output.setparams(data[0][0])
        for item in data:
            output.writeframes(item[1])
        output.close()
        return outfile