# https://nikolak.com/pyqt-qt-designer-getting-started/

# cd C:\Users\Roberto\Dropbox\Scripts\FISHcounter
# C:\Users\Roberto\Anaconda3\Library\bin\pyuic5.bat FISHcounter_QtDesigner.ui -o FISHCountDesign.py
# C:\Users\Roberto\Anaconda3\Library\bin\pyuic5.bat Report.ui -o ReportDesign.py
# python FISHcount.py

from PyQt5.QtCore import Qt, QRegExp
from PyQt5.QtWidgets import QMainWindow, QApplication, QDialog, QFileDialog, QErrorMessage, QPlainTextEdit
from PyQt5.QtGui import QIntValidator, QValidator, QRegExpValidator
import sys
from FISHCountDesign import Ui_MainWindow
from ReportDesign import Ui_ReportDialog
from FISHCountLogic import Logic
from FISHCountSettings import Settings
from FISHCountSound import Sound
from HelperFunctions import trg_to_tuples



class Report(Ui_ReportDialog, QDialog):
    def __init__(self, parent):
        super(Report, self).__init__(parent)
        self.parent = parent
        self.setupUi(self)
        self.sorted_cats = self.parent.logic.sort_categories()
        self.initialize_all()
        self._do_connect()
        self.create_ISCNstring_text()
            
    def initialize_all(self):
        self.TrgLabels = [self.TrgLabel_1,
                          self.TrgLabel_2,
                          self.TrgLabel_3,
                          self.TrgLabel_4,
                          self.TrgLabel_5,
                          self.TrgLabel_6]
        
        self.TrgCounts = [self.TrgCount_1,
                          self.TrgCount_2,
                          self.TrgCount_3,
                          self.TrgCount_4,
                          self.TrgCount_5,
                          self.TrgCount_6]
        
        self.checkboxes = [self.IncludecheckBox_1,
                           self.IncludecheckBox_2,
                           self.IncludecheckBox_3,
                           self.IncludecheckBox_4,
                           self.IncludecheckBox_5,
                           self.IncludecheckBox_6]
        
        for i, label in enumerate(self.TrgLabels):
            label.setText(self.parent.settings.get('trg_'+str(self.sorted_cats[i])))
        
        self.is_checked = [True for i in range(6)]
        totcount = self.parent.logic.counts.get_sum()
        for i, count in enumerate(self.TrgCounts):
            if totcount > 0:
                value = self.parent.logic.counts.values[self.sorted_cats[i]]
                count.setText('{:>3}/'.format(value)+str(totcount))
                self.checkboxes[i].setChecked(value > 0)
                self.is_checked[i] = (value > 0)
            else:
                count.setText('-')
        
   
    def _do_connect(self):
        for checkbox in self.checkboxes:
            checkbox.stateChanged.connect(self.include)


    def include(self):
        sender = self.sender()
        sender_index = self.checkboxes.index(sender)
        self.is_checked[sender_index] = sender.isChecked()
        self.create_ISCNstring_text()
        


    def create_ISCNstring_text(self):
        message = []
        top = ("<!DOCTYPE HTML PUBLIC \"-//W3C//DTD HTML 4.0//EN\" \"http://www.w3.org/TR/REC-html40/strict.dtd\">\n"
                "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n"
                "p, li { white-space: pre-wrap; }\n"
                "</style></head><body style=\" font-family:\'Courier New\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n"
                "<p style=\" margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">")
        bottom = "</p>\n</body></html>"
        totcount = self.parent.logic.counts.get_sum()
        if totcount > 0:
            for i, item in enumerate(self.is_checked):
                if item:
                    key = self.parent.settings.get('iscn_'+str(self.sorted_cats[i]))
                    key = key.strip()
                    if key.startswith('nuc ish'):
                        key = key[7:].strip()
                    count = self.parent.logic.counts.values[self.sorted_cats[i]]
                    if count > 0:
                        message.append('{}[{}/{}]'.format(key, count, totcount))
            html = top+'nuc ish'+'/'.join(message)+bottom
        else:
            html = top+'No counts yet'+bottom
        
        
        self.ISCNStringsTextBrowser.setHtml(html)

            

# https://stackoverflow.com/questions/42237147/pyqt-5-keypressevent-doesnt-work-for-terminating-app-qt-designer
class FISHCountMainWindow(QMainWindow, Ui_MainWindow):
    def __init__(self, parent=None, app=None):
        self.app = app
        super(FISHCountMainWindow, self).__init__(parent)
        self.setupUi(self)
        self.app.setStyle('WindowsVista')
        self.savefile = None
        self.logic = None
        self.x_size = 450
        self.settings = Settings()
        self.initialize_all()
        self._do_connect()
        self.do_reset()
        self.updateViews()
        self.originalpalette = self.palette()
        self.show()        

    def initialize_all(self):
        self.initialize_presets()
        self.initialize_targets()
        self.lock_check()
        self.initialize_audiovideo()
        self.sound = Sound(self.has_sound, self.soundtype, self.target_strings)
        if not self.logic:
            goal = int(self.settings.get('total', section='DEFAULT'))
            current = [int(x) for x in self.settings.get('current', section='DEFAULT').split(' ')]
            self.logic = Logic(goal=goal, keys=self.key_nums, current_counts=current)
        self.initialize_bars()
        self._tweak()
        self._create_button_landers()


    def _do_connect(self):
        self.actionSaveSettings.triggered.connect(self.file_save)
        self.actionSave_as.triggered.connect(self.file_save)
        self.actionSave_FISH_count.triggered.connect(self.file_save)
        self.actionLoadSettings.triggered.connect(self.file_load)
        self.actionLoad_FISH_count.triggered.connect(self.file_load)
        self.actionDefault.triggered.connect(self.file_load)
        self.ExpandButton.clicked.connect(self.flip_size)
        self.PresetDescButton.clicked.connect(self.goto_setting)
        self.SaveButton.clicked.connect(self.file_save)
        self.CountGoal.textChanged.connect(self.check_state)
        self.CountGoal.editingFinished.connect(self.update_goal)
        self.SoundButton.clicked.connect(self.toggle_sound)
        self.SoundComboBox.currentIndexChanged.connect(self.toggle_soundtype)
        self.UndoButton.clicked.connect(self.act_undo)
        self.SaveCountButton.clicked.connect(self.file_save)
        self.ReportButton.clicked.connect(self.expand_iscn)
        self.ResetButton.clicked.connect(self.do_reset)
        self.LockCheckBox.stateChanged.connect(self.lock_check)
        self.ChimerismCheckBox.stateChanged.connect(self.chimerism_switch)
        self.ShowReportButton.clicked.connect(self.create_report)
        self.PresetDesc.returnPressed.connect(self.update_labels)
        self.PresetLabel.returnPressed.connect(self.update_labels)
        for line in self.targetlines + self.colorlines:
            line.returnPressed.connect(self.update_labels)
        for item in self.keyb:
            item.textChanged.connect(self.check_state)
            item.editingFinished.connect(self.update_keys)
        for preset in self.presets:
            preset.clicked.connect(self.load_preset)
        for item in self.targetbuttons + self.colorbuttons:
            item.clicked.connect(self.goto_setting)
        for pair in self.chimrbs:
            for item in pair:
                item.toggled.connect(self.chimradiotoggled)
            

    def _create_button_landers(self):
        landers = [(self.PresetDescButton, self.PresetDesc)]
        landers.extend((button, line) for button, line in zip(self.targetbuttons, self.targetlines))
        landers.extend((button, line) for button, line in zip(self.colorbuttons, self.colorlines))
        self.landers = dict(landers)        

    
    def goto_setting(self):
        self.expand_iscn()
        sender = self.sender()
        self.landers[sender].setFocus()
        
        
    def initialize_presets(self):
        # Group some widgets:
        # Preset buttons
        self.presets = [self.Preset_0,
                        self.Preset_1,
                        self.Preset_2,
                        self.Preset_3,
                        self.Preset_4,
                        self.Preset_5
                        ]

        for i, preset in enumerate(self.presets):
            preset.setText(str(self.settings.get('label', section=self.settings.preset_names[i])))
        self.load_preset_settings()
        self.statusbar.showMessage('Preset "'+self.presets[self.settings.currentpreset].text()+'" loaded',5000)


    def load_preset_settings(self):
        self.PresetDesc.setText(self.settings.get('desc'))
        self.PresetDescButton.setText(self.settings.get('desc'))
        self.PresetLabel.setText(self.settings.get('label'))
        self.PresetDesc.setText(self.settings.get('desc'))
        self.presetlock = bool(int(self.settings.get('locked')))
        self.LockCheckBox.setChecked(self.presetlock)
        


    def initialize_targets(self):
        # Target buttons (2R2G, etc.)
        self.targetbuttons = [self.Trg_0,
                        self.Trg_1,
                        self.Trg_2,
                        self.Trg_3,
                        self.Trg_4,
                        self.Trg_5
                        ]

        # Keyboard 'buttons' (lineedits)
        self.keyb = [self.LineEdit_Key0,
                     self.LineEdit_Key1,
                     self.LineEdit_Key2,
                     self.LineEdit_Key3,
                     self.LineEdit_Key4,
                     self.LineEdit_Key5
                     ]
        
        self.targetlines = [self.Trg_0_string,
                                  self.Trg_1_string,
                                  self.Trg_2_string,
                                  self.Trg_3_string,
                                  self.Trg_4_string,
                                  self.Trg_5_string
                        ]
        
        
        self.targetISCNlines = [self.Trg_0_ISCN,
                                self.Trg_1_ISCN,
                                self.Trg_2_ISCN,
                                self.Trg_3_ISCN,
                                self.Trg_4_ISCN,
                                self.Trg_5_ISCN
                                ]
        
        self.colorlines = [self.BlueLine,
                           self.AquaLine,
                           self.GreenLine,
                           self.RedLine
                           ]

        self.colorbuttons = [self.BlueButton,
                             self.AquaButton,
                             self.GreenButton,
                             self.RedButton
                             ]
        
        self.chimerism_boxes = [self.ChimGB_0,
                                self.ChimGB_1,
                                self.ChimGB_2,
                                self.ChimGB_3,
                                self.ChimGB_4,
                                self.ChimGB_5]
        
        self.chimrbs  = [(self.Chim_0_a, self.Chim_0_b),
                         (self.Chim_1_a, self.Chim_1_b),
                         (self.Chim_2_a, self.Chim_2_b),
                         (self.Chim_3_a, self.Chim_3_b),
                         (self.Chim_4_a, self.Chim_4_b),
                         (self.Chim_5_a, self.Chim_5_b)]


        # Label target buttons and set self.target_strings list
        # Label key buttons and set self.key_nums list
        self.target_strings = [None for i in range(6)]
        self.target_ISCN_strings = [None for i in range(6)]
        self.colorstrings = [None for i in range(6)]
        
        self.key_nums = [None for i in range(6)]
        for stringlist, widgetlist, nameslist in [(self.target_strings, self.targetbuttons, self.settings.target_names),
                                                  (self.target_strings, self.targetlines, self.settings.target_names),
                                                  (self.target_ISCN_strings, self.targetISCNlines, self.settings.target_iscns),
                                                  (self.colorstrings, self.colorlines, self.settings.colors),
                                                  (self.colorstrings, self.colorbuttons, self.settings.colors),
                                                  (self.key_nums, self.keyb, self.settings.key_names)]:
            for i, widget in enumerate(widgetlist):
                widget_string = str(self.settings.get(nameslist[i]))
                if type(widget) == QPlainTextEdit:
                    widget.setPlainText(widget_string)
                else:
                    widget.setText(widget_string)
                if widget_string is not 'n/a':
                    stringlist[i] = widget_string
        self.chimerism_on = (self.settings.get('chimerism') == '1')
        self.ChimerismCheckBox.setChecked(self.chimerism_on)
        self.ChimerismWidget.setHidden(not self.chimerism_on)
        self.chimerism_attrib = [0 for i in range(6)]
        for i, buttons in enumerate(self.chimrbs):
            is_b = (self.settings.get('chim_'+str(i)) == 'b')
            self.chimerism_attrib[i] = int(is_b) # 0 == a, 1 == b
            settings = [(True, False), (False, True)][int(is_b)]
            for button, status in zip(buttons, settings):
               button.setChecked(status)
                

    def chimradiotoggled(self):
        sender = self.sender()
        for i, (a, b) in enumerate(self.chimrbs):
            if sender in (a, b):
                self.chimerism_attrib[i] = int(b.isChecked())
                self.settings.set('chim_'+str(i), ['a', 'b'][int(b.isChecked())])


    def chimerism_switch(self):
        sender = self.sender()
        self.chimerism_on = sender.isChecked()
        self.ChimerismWidget.setHidden(not self.chimerism_on)
        if self.ChimerismCheckBox.isChecked() and (not self.LockCheckBox.isChecked()):
            for item in self.chimerism_boxes:
                item.setEnabled(True)
        self.settings.set('chimerism', str(int(self.chimerism_on)))


    def initialize_audiovideo(self):
        self.has_sound = bool(int(self.settings.get('sound', section='DEFAULT')))
        self.soundtype = int(self.settings.get('soundtype', section='DEFAULT'))
        self.set_soundwidgets()

            
    def lock_check(self):
        enable = not self.LockCheckBox.isChecked()
        self.settings.set('locked', str(int(not enable)))
        self.PresetLabel.setEnabled(enable)
        self.PresetDesc.setEnabled(enable)
        for item in self.targetlines:
            item.setEnabled(enable)
        for item in self.targetISCNlines:
            item.setEnabled(enable)
        for item in self.colorlines:
            item.setEnabled(enable)
        self.ChimerismCheckBox.setEnabled(enable)
        for item in self.chimerism_boxes:
            item.setEnabled(enable and self.ChimerismCheckBox.isChecked())
                
                
    def flip_size(self):
        if self.ExpandButton.text() == '<':
            self.expand_iscn()
        else:
            self.retract_iscn()


    def expand_iscn(self):
        self.x_size = 900
        self.resize_x()
        self.ExpandButton.setText('>')
        
        

    def retract_iscn(self):
        self.x_size = 450
        self.resize_x()
        self.ExpandButton.setText('<')
    
    
    def resize_x(self):
        self.resize(self.x_size, 630)
        
    
    def toggle_sound(self):
        self.has_sound = not self.has_sound
        self.set_soundwidgets()
        self.set_wavs()


    def toggle_soundtype(self):
        self.soundtype = self.SoundComboBox.currentIndex()
        self.set_wavs()
        self.HiddenFocus.setFocus()

        
    def set_soundwidgets(self):
        self.SoundButton.setText(["Sound: OFF", "Sound: ON"][self.has_sound])
        self.SoundComboBox.setCurrentIndex(self.soundtype)
        self.SoundComboBox.setEnabled(self.has_sound)

    def set_wavs(self):
        self.sound.attrib_wavs(self.has_sound, self.soundtype, self.target_strings)
    
        
    def initialize_bars(self):
        self.countingbars = [(self.PrBar_0, self.Label_0),
                             (self.PrBar_1, self.Label_1),
                             (self.PrBar_2, self.Label_2),
                             (self.PrBar_3, self.Label_3),
                             (self.PrBar_4, self.Label_4),
                             (self.PrBar_5, self.Label_5),
                             ]
        for bar, label in self.countingbars:
            bar.setStyleSheet(" QProgressBar { border: 1px solid grey; border-radius: 0px; text-align: top center; } QProgressBar::chunk {background-color: blue; height: 1px;}")
            bar.setMaximum(self.logic.goal)
            bar.setMinimum(0)
        

    def _tweak(self):
        self.CountGoal.setMaxLength(3)
        self.CountGoal.setText(str(self.logic.goal))
        key_regex =  QRegExp("[A-Za-z0-9_]{1}")
        for item in self.keyb:
            item.setMaxLength(1)
            item.setValidator(QRegExpValidator(key_regex))
        self.err_msg = QErrorMessage(self)
        self.err_msg.setWindowModality(Qt.WindowModal)


        # HTML template for the current nuclei count textbox
        self.curr_c_txt = "<html><head><meta name=\"qrichtext\" content=\"1\" /><style type=\"text/css\">\n" + \
                          "p, li {{ white-space: pre-wrap; }}\n" + \
                          "</style></head><body style=\" font-family:\'MS Shell Dlg 2\'; font-size:8.25pt; font-weight:400; font-style:normal;\">\n" + \
                          "<p style=\" text-align: right; margin-top:0px; margin-bottom:0px; margin-left:0px; margin-right:0px; -qt-block-indent:0; text-indent:0px;\">" + \
                          "{0}" + \
                          "</p></body></html>"        


    def check_state(self, *args, **kwargs):
        # https://snorfalorpagus.net/blog/2014/08/09/validating-user-input-in-pyqt4-using-qvalidator/
        sender = self.sender()
        validator = sender.validator()
        state = validator.validate(sender.text(), 0)[0]
        if state == QValidator.Acceptable:
            color = '#c4df9b' # green
        elif state == QValidator.Intermediate:
            color = '#fff79a' # yellow
        else:
            color = '#f6989d' # red
        sender.setStyleSheet('QLineEdit { background-color: %s }' % color)


    def file_save(self):
        sender =  self.sender()
        self.update_labels()
        if sender in [self.actionSave_FISH_count, self.SaveCountButton]:
            save_text = 'FISH count'
        elif sender == self.actionSave_as:
            save_text = 'Settings'
        elif sender in [self.actionSaveSettings, self.SaveButton] and self.savefile != None:
            self.settings.save(filename=self.savefile, data=self._forward_sender_data(sender))
            self.statusbar.showMessage('Settings saved to: "'+self.savefile+'"',5000)
            return
        elif sender in [self.actionSaveSettings, self.SaveButton]:
            save_text = 'Settings'
            self.settings.save(filename=None, data=self._forward_sender_data(sender))
        else:
            raise Exception('Unknown save sender widget')
        myfilter = save_text+" files "+['(*.config)', '(*.FISH)'][save_text=='FISH count']
        name = QFileDialog.getSaveFileName(self, 'Save '+save_text, filter=myfilter)[0]
        if name != '':
            self.settings.save(filename=name, data=self._forward_sender_data(sender))
            self.statusbar.showMessage(save_text+' saved to: "'+name+'"',5000)
            if sender in [self.actionSaveSettings, self.SaveButton, self.actionSave_as]:
                self.savefile = name


    def file_load(self):
        sender =  self.sender()
        default = False
        if sender == self.actionLoadSettings:
            load_text = 'Settings'
        elif sender == self.actionLoad_FISH_count:
            load_text = 'FISH count'
        elif sender == self.actionDefault:
            default = True
            load_text = 'Default settings'
        else:
            raise Exception('Unknown load sender widget')
        if default:
            name = None
        else:
            name = QFileDialog.getOpenFileName(self, 'Load '+load_text)[0]
        if name != '':
            self.logic = None
            self.settings.load(filename=name, data=self._forward_sender_data(sender))
            if sender == self.actionLoadSettings:
                self.savefile = name
        self.initialize_all()
        self.updateViews()
        self.statusbar.showMessage('Loaded '+load_text+': "'+name+'"',5000)
            
            
    def _forward_sender_data(self, sender):
        if sender in [self.actionSaveSettings, self.actionSave_as, self.SaveButton, 
                      self.actionLoadSettings, self.actionDefault]:
            return {'window': self, 'counts': False}
        elif sender in [self.actionSave_FISH_count, self.actionLoad_FISH_count]:
            return {'window': self, 'counts': True}



    def load_preset(self):
        sender = self.sender()
        self.settings.set_preset(self.presets.index(sender))
        self.initialize_targets()
        self.load_preset_settings()
        self.logic = Logic(self.logic.goal, keys=self.key_nums)
        self.set_wavs()
        self.do_reset()
        self.statusbar.showMessage('Preset "'+str(self.settings.currentpreset)+'" loaded',5000)
        

    def do_reset(self):
        # At start, only accept values 1-999
        self.CountGoal.setValidator(QIntValidator(1, 999, self))
        self.logic.reset_counts()
        self.LastNucleus.setText('-')
        self.UndoButton.setEnabled(False)
        self.update_goal()
        self.statusbar.showMessage('Count has been reset',5000)
        self.sound.play_start()
        
        
    def update_keys(self):
        sender = self.sender()
        if ord(sender.text().upper()) not in self.logic.keys.keys:
            for i, key in enumerate(self.keyb):
                if i < len(self.logic.keys.keys):
                    if len(key.text()) > 0:
                        character = key.text().upper()
                        key.setText(character)
                        self.settings.set('key_'+str(i), character)
                        self.logic.keys.alter(i, ord(character))
                    else:
                        key.setText(self.settings.get('key_'+str(i)))
        else:
            sender.setText(self.settings.get('key_'+str(self.keyb.index(sender))))
        sender.setStyleSheet("background-color: rgb(230, 230, 230);")

        
    def update_goal(self):
        newgoal = int(self.CountGoal.text())
        # Adding a custom validating condition, because tabs are tricky
        if max([1, self.logic.counts.get_sum()]) <= newgoal < 1000:
            self.logic.set_goal(int(newgoal))
            self.CountGoal.setStyleSheet('QLineEdit { background-color: %s }' % '#ffffff')
            self.initialize_bars()
            self.updateViews()
            self.updateProgress()
            self.settings.set('TOTAL', str(newgoal), section='DEFAULT')
            self.statusbar.showMessage('Counting '+str(newgoal)+' nuclei',5000)
        else:
            self.statusbar.showMessage('Invalid goal; reverting...',5000)
            self.CountGoal.setText(str(self.logic.goal))


    def update_labels(self):
        self.HiddenFocus.setFocus()
        self.presets[self.settings.currentpreset].setText(self.PresetLabel.text())
        self.settings.set('label', self.PresetLabel.text())
        self.PresetDescButton.setText(self.PresetDesc.text())
        self.settings.set('desc', self.PresetDesc.text())
        colors = ['blue', 'aqua', 'green', 'red']
        for number, (line, button) in enumerate(zip(self.colorlines, self.colorbuttons)):
            button.setText(line.text())
            self.settings.set(colors[number], line.text())
        for number, (line, button) in enumerate(zip(self.targetlines, self.targetbuttons)):
            button.setText(line.text())
            self.settings.set('trg_'+str(number), line.text())
        for number, line in enumerate(self.targetISCNlines):
            self.settings.set('iscn_'+str(number), line.toPlainText())
        self.statusbar.showMessage('Labels updated.',5000)
        


        
    def updateViews(self, bar = None):
        if bar is not None:
            self.updateBars(bar)
        else:
            self.updateBars()
        self.CountGoal.setValidator(QIntValidator(max([1, self.logic.counts.get_sum()]), 999, self))
        self.CountGoal.setText(str(self.logic.goal))
        self.CountGoal.setStyleSheet('QLineEdit { background-color: %s }' % '#ffffff')
        self.updateProgress()
            
        
    def keyPressEvent(self, event):
        if self.logic.is_key(event.key()):
            self.act_count_event(event.key())
        elif event.key() == Qt.Key_Escape:
            self.close()
        elif event.key() == Qt.Key_Backspace:
            self.act_undo()
        elif event.key() == Qt.Key_Return:
            self.HiddenFocus.setFocus()
            self.updateViews()
        else:
            print("Unregistered key:", event.key())
                

    def act_undo(self):
                success = self.logic.undo()
                if success:
                    self.sound.play_success()
                    self.ReportButton.setEnabled(False)
                    self.updateViews()
                    if self.logic.last_positions[-1] == None:
                        newlast = '-'
                        self.UndoButton.setEnabled(False)
                        self.statusbar.showMessage('Undo successful. Undo queque is now empty.',5000)
                    else:
                        newlast = self.targetbuttons[self.logic.last_positions[-1]].text()
                        self.statusbar.showMessage('Undo successful.',5000)
                    self.LastNucleus.setText(newlast)
                else:
                    self.sound.play_error()
                    self.statusbar.showMessage('Undo queue is empty; unable to undo.',5000)
        
    def act_count_event(self, keypress):
            success = self.logic.register(keypress)
            if success:
                position = self.logic.keys.get_position(keypress)
                self.sound.play(position)
                self.LastNucleus.setText(self.targetbuttons[self.logic.last_positions[-1]].text())
                self.UndoButton.setEnabled(True)
                self.updateViews(bar=position)
                    
    
    def create_report(self):
        report = Report(self)
        report.exec_()
        
        

    def tuples_to_ISCN(self, target_tuple):
        '''
        ADD EACH CELL TYPE AS A DESC STRING!!! SOLVED - except chimeras (individual 1, individual 2?)
        
        "X" is best used as symbol:
            Symbol  ASCII     Unicode  Name
            ×       Alt+0215  U+00D7   MULTIPLICATION SIGN (z notation Cartesian product)

       
        NB:
            1) Probes in the same chromosome should be listed pter-> qter, so needs cytoband anyway p.112
            2) Probes in the same locus, 3' and 5', listed pter to qter also!
            3) Probes in different chromosomes listed X-Y chromosomes first, then autosomes
            4) Bracket / to separate counts
            5) Chimeras // (donor, recipient) p.113
            6) data with zero signals!
            7) Separate hybridizations (not needed here)
            8) 3', 5' go before the name of the gene (3'MLL, 5'MLL)
            
         - number of signals:    nuc ish(D21S65X2)[200]                        <- X2 inside parentheses because 1 locus
         - number ex. 10~20      nuc ish(D17Z1,ERBB2)X4~5[100/200]             <- X4~5 outside parentheses because 2 loci
         - different patterns    nuc ish(D17Z1x2~3),(ERBB2 amp)[100/200],(D17Z1,ERBB2)X3[20/200]
         - amplification         nuc ish(MYCN amp)[200]                         "beyond which can be reliably counted"
         - dim signal            nuc ish(D13S19X1,D13S19 dimX1,LAMPX2)[197/200]
         - zero signals          nuc ish(D13S19X0)[100/400]
         - fusions               nuc ish(ABL1,BCR)X3,(ABL1 con BCRX2)          <- observe "X3" outside because 2 loci, but fusion "X2" inside because it's joined
         - break-apart           nuc ish(KAL1,STS)X2,(KAL1 sep STSX1)
         
         
        
        '''
        pass



                
    def updateProgress(self):
        self.progressBar.setProperty("value", self.logic.get_progress())
        self.Current_count_text.setHtml(self.curr_c_txt.format(str(self.logic.counts.get_sum())))
        if self.logic.is_goal_reached():
            self.sound.play_finished()
            self.statusbar.showMessage('Goal reached.',5000)
            

    
    
    def updateBars(self, bar = None):
        assert (bar == None) or (type(bar) == int and 0 <= bar < 6)
        bar = None # TODO remove here
        if bar is not None:
            bars = [bar]
        else:
            bars = range(0,6)
        
        for bar in bars:
            self.countingbars[bar][0].setProperty("value", self.logic.counts.get_bar(bar))
            self.countingbars[bar][1].setText('{:.1f} %'.format(self.logic.get_progress(bar, rettype=float)))
            

if __name__ == "__main__":
    app = QApplication(sys.argv)
    MainWindow = FISHCountMainWindow(app=app) # <-- Instantiate QMainWindow object.
    sys.exit(app.exec_())