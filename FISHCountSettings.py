# -*- coding: utf-8 -*-
"""
Created on Thu May 31 20:16:13 2018

@author: Roberto
"""

import configparser
from FISHCountLogic import Logic


class Settings(object):
    def __init__(self):
        self.default_filename = 'default.config'
        self.config = configparser.ConfigParser()
        response = self.config.read('last.config')
        if not response:
            self.config.read(self.default_filename)
        self.currentpreset = int(self.config['DEFAULT']['preset'])
        self.do_complete()
        #self.save()


    def print(self):
        for section in self.config:
            print(section)
            for key in self.config[section]:
                print(key + ' = ' + repr(self.config[section][key]))

    def to_string(self, data):
        if type(data) == list:
            return ' '.join([str(x) for x in data])
        elif type(data) == bool:
            return str(int(data))
        else:
            return str(data)
        

    def get(self, key, section=None):
        if not section:
            section = 'Preset_'+str(self.currentpreset)
        return self.config[section][key]
        

    def set(self, key, value, section=None):
        if not section:
            section = 'Preset_'+str(self.currentpreset)
        self.config[section][key] = value

    def set_preset(self, preset):
        self.currentpreset = preset
        self.config['DEFAULT']['preset'] = self.to_string(self.currentpreset)

    def collect(self, window):
        self.config['DEFAULT']['sound'] = self.to_string(window.has_sound)
        self.config['DEFAULT']['soundtype'] = self.to_string(window.soundtype)
        self.config['DEFAULT']['preset'] = self.to_string(self.currentpreset)
        self.config['DEFAULT']['total'] = self.to_string(window.logic.goal)
        self.config['DEFAULT']['current'] = self.to_string(window.logic.counts.values)
        
        
    def load(self, filename, data={'window': None, 'counts': False}):
        if filename is None:
            filename = self.default_filename
        newconfig = configparser.ConfigParser()
        error = False
        try:
            response = newconfig.read(filename)
        except:
            error = True
        if error or not newconfig['DEFAULT']:
            data['window'].err_msg.showMessage('This is not a valid file.')
            return
        if not data['counts']:
            # Ignore FISH counts
            newconfig['DEFAULT']['current'] = self.to_string([0 for i in range(6)])
        self.config = newconfig
            
            
            
    def save(self, filename = None, data={'window': None, 'counts': False}):
        if not filename:
            filename = 'last.config'
        if data['window']:
            self.collect(data['window'])
        if not data['counts']:
            self.config['DEFAULT']['current'] = self.to_string([0 for i in range(6)])
        try:
            with open(filename, 'w') as f:
                self.config.write(f)
        except OSError:
            print("File busy - unable to save")
            
    def is_valid_target(self, target, verbose = False):
        if target == '':
            if verbose:
                print("Target cannot be empty")
            return False
        valid = '123456BAGRFX' #No. of signals and Blue, Aqua, Green, Red, Fusion, X=Other
        test = target
        for character in valid:
            test = test.replace(character, '')
        if test != '':
            if verbose:
                print('Invalid characters: ', test)
            return False
        return True
            
    def do_complete(self):
        self.preset_names = ['Preset_'+str(i) for i in range(0,6)]
        self.target_names = ['trg_'+str(i) for i in range(0,6)]
        self.key_names = ['key_'+str(i) for i in range(0,6)]
        self.target_iscns = ['iscn_'+str(i) for i in range(0,6)]
        self.target_chimerism = ['chim_'+str(i) for i in range(0,6)]
        self.colors = ['blue', 'aqua', 'green', 'red']
        tnk = list(zip(self.key_names, self.target_names, self.target_iscns, self.target_chimerism))
        for preset in self.preset_names:
            if preset not in self.config.keys():
                self.config[preset] = {}
                self.config[preset]['label'] = 'empty'
                self.config[preset]['desc'] = ''
                self.config[preset]['chimerism'] = '0'
            for key, target, iscn, chim in tnk:
                if (key not in self.config[preset].keys()) or \
                   (target not in self.config[preset].keys()):
                    self.config[preset][key] = 'n/a'
                    self.config[preset][target] = 'n/a'
                if iscn not in self.config[preset].keys():
                    self.config[preset][iscn] = '[no ISCN string provided]'
                if chim not in self.config[preset].keys():
                    self.config[preset][chim] = 'a'
                for color in self.colors:
                    if color not in self.config[preset].keys():
                        self.config[preset][color] = ''

            