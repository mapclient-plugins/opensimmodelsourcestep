
import os
from PySide6 import QtWidgets
from mapclientplugins.opensimmodelsourcestep.ui_configuredialog import Ui_Dialog

INVALID_STYLE_SHEET = 'background-color: rgba(239, 0, 0, 50)'
DEFAULT_STYLE_SHEET = ''

class ConfigureDialog(QtWidgets.QDialog):
    '''
    Configure dialog to present the user with the options to configure this step.
    '''

    def __init__(self, parent=None):
        '''
        Constructor
        '''
        QtWidgets.QDialog.__init__(self, parent)
        
        self._ui = Ui_Dialog()
        self._ui.setupUi(self)

        # Keep track of the previous identifier so that we can track changes
        # and know how many occurrences of the current identifier there should
        # be.
        self._previousIdentifier = ''
        self._previousFileLoc = ''
        # Set a place holder for a callable that will get set from the step.
        # We will use this method to decide whether the identifier is unique.
        self.identifierOccursCount = None

        self._makeConnections()

    def _makeConnections(self):
        self._ui.idLineEdit.textChanged.connect(self.validate)
        self._ui.fileLocButton.clicked.connect(self._fileLocClicked)
        self._ui.fileLocLineEdit.textChanged.connect(self._fileLocEdited)

    def accept(self):
        '''
        Override the accept method so that we can confirm saving an
        invalid configuration.
        '''
        result = QtWidgets.QMessageBox.Yes
        if not self.validate():
            result = QtWidgets.QMessageBox.warning(self, 'Invalid Configuration',
                'This configuration is invalid.  Unpredictable behaviour may result if you choose \'Yes\', are you sure you want to save this configuration?)',
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No, QtWidgets.QMessageBox.No)

        if result == QtWidgets.QMessageBox.Yes:
            QtWidgets.QDialog.accept(self)

    def validate(self):
        '''
        Validate the configuration dialog fields.  For any field that is not valid
        set the style sheet to the INVALID_STYLE_SHEET.  Return the outcome of the 
        overall validity of the configuration.
        '''
        # Determine if the current identifier is unique throughout the workflow
        # The identifierOccursCount method is part of the interface to the workflow framework.
        idValue = self.identifierOccursCount(self._ui.idLineEdit.text())
        idValid = (idValue == 0) or (idValue == 1 and self._previousIdentifier == self._ui.idLineEdit.text())
        if idValid:
            self._ui.idLineEdit.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.idLineEdit.setStyleSheet(INVALID_STYLE_SHEET)

        fileLocValid = os.path.exists(self._ui.fileLocLineEdit.text())
        if fileLocValid:
            self._ui.fileLocLineEdit.setStyleSheet(DEFAULT_STYLE_SHEET)
        else:
            self._ui.fileLocLineEdit.setStyleSheet(INVALID_STYLE_SHEET)
            
        valid = idValid and fileLocValid
        self._ui.buttonBox.button(QtWidgets.QDialogButtonBox.Ok).setEnabled(valid)

        return valid

    def getConfig(self):
        '''
        Get the current value of the configuration from the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        '''
        self._previousIdentifier = self._ui.idLineEdit.text()
        self._previousFileLoc = self._ui.fileLocLineEdit.text()
        config = {}
        config['identifier'] = self._ui.idLineEdit.text()
        config['file location'] = self._ui.fileLocLineEdit.text()
        return config

    def setConfig(self, config):
        '''
        Set the current value of the configuration for the dialog.  Also
        set the _previousIdentifier value so that we can check uniqueness of the
        identifier over the whole of the workflow.
        '''
        self._previousIdentifier = config['identifier']
        self._previousFileLoc = config['file location']
        self._ui.idLineEdit.setText(config['identifier'])
        self._ui.fileLocLineEdit.setText(config['file location'])

    def _fileLocClicked(self):
        location = QtWidgets.QFileDialog.getOpenFileName(self, 'Select File Location', self._previousFileLoc)
        if location[0]:
            self._previousFileLoc = location[0]
            self._ui.fileLocLineEdit.setText(location[0])

    def _fileLocEdited(self):
        self.validate()