# -*- coding: utf-8 -*-
"""
/***************************************************************************
 TTCoordinateCapturer
                                 A QGIS plugin
 It's use to capture the cooridnates on Map Canvas.
                              -------------------
        begin                : 2016-05-30
        git sha              : $Format:%H$
        copyright            : (C) 2016 by Miles TOMTOM
        email                : miles.lee@tomtom.com
 ***************************************************************************/

/***************************************************************************
 *                                                                         *
 *   This program is free software; you can redistribute it and/or modify  *
 *   it under the terms of the GNU General Public License as published by  *
 *   the Free Software Foundation; either version 2 of the License, or     *
 *   (at your option) any later version.                                   *
 *                                                                         *
 ***************************************************************************/
"""
import os
from PyQt4.QtCore import QSettings, QTranslator, qVersion, QCoreApplication, QObject, SIGNAL
from PyQt4.QtGui import * #QAction, QIcon
# Initialize Qt resources from file resources.py
import resources
# Import the code for the dialog
from coordinate_capturer_dialog import TTCoordinateCapturerDialog
from PyQt4.QtGui import QDialogButtonBox
import os.path
from qgis.gui import *
from qgis.core import *
import ogr, osr

class TTCoordinateCapturer:
    """QGIS Plugin Implementation."""

    def __init__(self, iface):
        """Constructor.

        :param iface: An interface instance that will be passed to this class
            which provides the hook by which you can manipulate the QGIS
            application at run time.
        :type iface: QgsInterface
        """
        # Save reference to the QGIS interface
        self.iface = iface
        #a reference to map cavans
        self.canvas = self.iface.mapCanvas()
        # this QGIS tool emits as QgsPoint after each click on the map canvas
        self.clickTool = QgsMapToolEmitPoint(self.canvas)
        # initialize plugin directory
        self.plugin_dir = os.path.dirname(__file__)
        # initialize locale
        locale = QSettings().value('locale/userLocale')[0:2]
        locale_path = os.path.join(
            self.plugin_dir,
            'i18n',
            'TTCoordinateCapturer_{}.qm'.format(locale))

        if os.path.exists(locale_path):
            self.translator = QTranslator()
            self.translator.load(locale_path)

            if qVersion() > '4.3.3':
                QCoreApplication.installTranslator(self.translator)

        # Create the dialog (after translation) and keep reference
        self.dlg = TTCoordinateCapturerDialog()

        # Declare instance attributes
        self.actions = []
        self.menu = self.tr(u'&TomTom Coordinate Capturer')
        # TODO: We are going to let the user set this up in a future iteration
        self.toolbar = self.iface.addToolBar(u'TTCoordinateCapturer')
        self.toolbar.setObjectName(u'TTCoordinateCapturer')

    # noinspection PyMethodMayBeStatic
    def tr(self, message):
        """Get the translation for a string using Qt translation API.

        We implement this ourselves since we do not inherit QObject.

        :param message: String for translation.
        :type message: str, QString

        :returns: Translated version of message.
        :rtype: QString
        """
        # noinspection PyTypeChecker,PyArgumentList,PyCallByClass
        return QCoreApplication.translate('TTCoordinateCapturer', message)


    def add_action(
        self,
        icon_path,
        text,
        callback,
        enabled_flag=True,
        add_to_menu=True,
        add_to_toolbar=True,
        status_tip=None,
        whats_this=None,
        parent=None):
        """Add a toolbar icon to the toolbar.

        :param icon_path: Path to the icon for this action. Can be a resource
            path (e.g. ':/plugins/foo/bar.png') or a normal file system path.
        :type icon_path: str

        :param text: Text that should be shown in menu items for this action.
        :type text: str

        :param callback: Function to be called when the action is triggered.
        :type callback: function

        :param enabled_flag: A flag indicating if the action should be enabled
            by default. Defaults to True.
        :type enabled_flag: bool

        :param add_to_menu: Flag indicating whether the action should also
            be added to the menu. Defaults to True.
        :type add_to_menu: bool

        :param add_to_toolbar: Flag indicating whether the action should also
            be added to the toolbar. Defaults to True.
        :type add_to_toolbar: bool

        :param status_tip: Optional text to show in a popup when mouse pointer
            hovers over the action.
        :type status_tip: str

        :param parent: Parent widget for the new action. Defaults None.
        :type parent: QWidget

        :param whats_this: Optional text to show in the status bar when the
            mouse pointer hovers over the action.

        :returns: The action that was created. Note that the action is also
            added to self.actions list.
        :rtype: QAction
        """

        icon = QIcon(icon_path)
        action = QAction(icon, text, parent)
        action.triggered.connect(callback)
        action.setEnabled(enabled_flag)

        if status_tip is not None:
            action.setStatusTip(status_tip)

        if whats_this is not None:
            action.setWhatsThis(whats_this)

        if add_to_toolbar:
            self.toolbar.addAction(action)

        if add_to_menu:
            self.iface.addPluginToMenu(
                self.menu,
                action)

        self.actions.append(action)

        return action

    def initGui(self):
        """Create the menu entries and toolbar icons inside the QGIS GUI."""

        icon_path = ':/plugins/TTCoordinateCapturer/icon.png'
        self.add_action(
            icon_path,
            text=self.tr(u'Capture Coordinates'),
            callback=self.run,
            parent=self.iface.mainWindow())

        self.keyAction = QAction("ShortCut", self.iface.mainWindow())
        self.iface.registerMainWindowAction(self.keyAction, "Ctrl+c")
        self.iface.addPluginToMenu("&XYCaptureShortCut", self.keyAction)
        #result_keyShortCut = QObject.connect(self.keyAction, SIGNAL("triggered()"),self.keyActionF2)  #Old Style
        self.keyAction.triggered.connect(self.keyActionF2)
        
        result_canvasClicked = QObject.connect(self.clickTool, SIGNAL("canvasClicked(const QgsPoint &, Qt::MouseButton)"), self.handleMouseDown)
        result_Clip2Board = self.dlg.pushButton.clicked.connect(self.ClipToBoard)


    def unload(self):
        """Removes the plugin menu item and icon from QGIS GUI."""
        for action in self.actions:
            self.iface.removePluginMenu(
                self.tr(u'&TomTom Coordinate Capturer'),
                action)
            self.iface.removeToolBarIcon(action)
        # remove the toolbar
        self.iface.unregisterMainWindowAction(self.keyAction)
        del self.toolbar


    def run(self):
        """Run method that performs all the real work"""
        # show the dialog
        self.dlg.show()
        # make our clickTool the tool that we'll use for now
        self.canvas.setMapTool(self.clickTool)
        result = self.dlg.exec_()
        # See if OK was pressed
        if result:
            # Do something useful here - delete the line containing pass and
            # substitute with your code.
            self.iface.unregisterMainWindowAction(self.keyAction)
            pass

    def CoordinateConversion(self, Lat, Lon):
        Canvas = self.iface.mapCanvas()
        CurrentCRS = int(Canvas.mapRenderer().destinationCrs().authid().split(":")[1])
        OutputCRS = 4326
        point = ogr.Geometry(ogr.wkbPoint)
        point.AddPoint(Lat, Lon)

        # create coordinate transformation
        inSpatialRef = osr.SpatialReference()
        inSpatialRef.ImportFromEPSG(CurrentCRS)

        outSpatialRef = osr.SpatialReference()
        outSpatialRef.ImportFromEPSG(OutputCRS)

        coordTransform = osr.CoordinateTransformation(inSpatialRef, outSpatialRef)

        # transform point
        point.Transform(coordTransform)

        Lon = point.GetX()
        Lat = point.GetY()
     
        self.dlg.lineEdit.setText(str(round(Lat, 7)) + "," + str(round(Lon,7)))
        self.dlg.lineEdit_2.setText(str(round(Lat, 7)))
        self.dlg.lineEdit_3.setText(str(round(Lon, 7)))

    def handleMouseDown(self, point, button):
        self.CoordinateConversion(point.x(), point.y())

    def ClipToBoard(self):
        command = 'echo ' + str(self.dlg.lineEdit.text()) + '| clip'
        os.system(command)

    def keyActionF2(self):
        command = 'echo ' + str(self.dlg.lineEdit.text()) + '| clip'
        exec_result = os.system(command)

    
