import os
import sys
from qgis.core import QgsApplication, QgsProcessingFeedback
from qgis.analysis import QgsNativeAlgorithms

QgsApplication.setPrefixPath(r'C:\OSGeo4W64\apps\qgis', True)
qgs = QgsApplication([], False)
qgs.initQgis()
# Add the path to processing so we can import it next
sys.path.append(r'C:\OSGeo4W64\apps\qgis\python\plugins')
# Imports usually should be at the top of a script but this unconventional
# order is necessary here because QGIS has to be initialized first

import processing
from processing.core.Processing import Processing
Processing.initialize()
QgsApplication.processingRegistry().addProvider(QgsNativeAlgorithms())
feedback = QgsProcessingFeedback()
rivers = r'C:\webmapping\Capas\nxprovincias.shp'
output = r'C:\temp\nile.shp'
expression = "DPA_DESPRO LIKE '%GUAYAS%'"

nile = processing.run(
    'native:extractbyexpression',
    {'INPUT': rivers, 'EXPRESSION': expression, 'OUTPUT': output},
    feedback=feedback
)['OUTPUT']

print(nile)

from osgeo import gdal
print(gdal.VersionInfo("RELEASE_NAME"))