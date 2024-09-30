from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as spatialmodels


# Base model with audit fields
class AuditBaseModel(models.Model):
    is_active = models.BooleanField(default=True, verbose_name='Active Status')
    created_by = models.ForeignKey(User, related_name='+', verbose_name='Created by', null=True, blank=True,
                                   on_delete=models.PROTECT)
    modified_by = models.ForeignKey(User, related_name='+', verbose_name='Modified by', null=True,
                                    blank=True, on_delete=models.PROTECT)
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Creation Timestamp')
    updated_at = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Modification Timestamp')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        if self.id:
            self.modified_by = user if user else None
            self.updated_at = datetime.now()
        else:
            self.created_by = user if user else None
            self.created_at = datetime.now()
        super(AuditBaseModel, self).save(*args, **kwargs)


# GIS Model type options
GIS_TYPE_CHOICES = (
    (0, 'File'),
    (1, 'Point'),
    (2, 'LineString'),
    (3, 'Polygon'),
    (4, 'MultiPoint'),
    (5, 'MultiLineString'),
    (6, 'MultiPolygon'),
    (7, 'Raster File'),
)


# Geographic Information System Model
class GISRecord(AuditBaseModel):
    gis_type = models.IntegerField(verbose_name='GIS Data Type', choices=GIS_TYPE_CHOICES, default=0)
    data_file = models.FileField(upload_to='GISRecords/%Y/%m/%d', null=True, blank=True, verbose_name='Data File')
    srid = models.IntegerField(verbose_name='Spatial Reference System Identifier (SRID)', default=3857)
    # Spatial fields
    point_geometry = spatialmodels.PointField(verbose_name='Point Geometry', null=True, blank=True)
    linestring_geometry = spatialmodels.LineStringField(verbose_name='LineString Geometry', null=True, blank=True)
    polygon_geometry = spatialmodels.PolygonField(verbose_name='Polygon Geometry', null=True, blank=True)
    multipoint_geometry = spatialmodels.MultiPointField(verbose_name='MultiPoint Geometry', null=True, blank=True)
    multilinestring_geometry = spatialmodels.MultiLineStringField(verbose_name='MultiLineString Geometry', null=True,
                                                                  blank=True)
    multipolygon_geometry = spatialmodels.MultiPolygonField(verbose_name='MultiPolygon Geometry', null=True, blank=True)

    class Meta:
        verbose_name = 'Geographic Information System Record'
        verbose_name_plural = 'Geographic Information System Records'
        ordering = ['id']

    def save(self, *args, **kwargs):
        if not self.srid:
            self.srid = 3857  # Default SRID value
        if self.point_geometry: self.point_geometry.srid = self.srid
        if self.linestring_geometry: self.linestring_geometry.srid = self.srid
        if self.polygon_geometry: self.polygon_geometry.srid = self.srid
        if self.multipoint_geometry: self.multipoint_geometry.srid = self.srid
        if self.multilinestring_geometry: self.multilinestring_geometry.srid = self.srid
        if self.multipolygon_geometry: self.multipolygon_geometry.srid = self.srid
        super(GISRecord, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.get_gis_type_display()} (SRID: {self.srid})"

    def get_geometry_geojson(self):
        """Return the GeoJSON of the geometry based on the gis_type."""
        if self.gis_type == 1 and self.point_geometry:
            return self.point_geometry.json  # GeoJSON format
        elif self.gis_type == 2 and self.linestring_geometry:
            return self.linestring_geometry.json
        elif self.gis_type == 3 and self.polygon_geometry:
            return self.polygon_geometry.json
        elif self.gis_type == 4 and self.multipoint_geometry:
            return self.multipoint_geometry.json
        elif self.gis_type == 5 and self.multilinestring_geometry:
            return self.multilinestring_geometry.json
        elif self.gis_type == 6 and self.multipolygon_geometry:
            return self.multipolygon_geometry.json
        else:
            return None  # No valid geometry found


# GIS Detail Record
class GISDetailRecord(AuditBaseModel):
    gis_record = models.ForeignKey(GISRecord, verbose_name='Associated GIS Record', null=True, blank=True,
                                   on_delete=models.CASCADE)
    title = models.CharField(max_length=500, verbose_name='Title', null=True, blank=True)
    description = models.TextField(verbose_name='Description', null=True, blank=True)

    class Meta:
        verbose_name = 'Geographic Information System Detail Record'
        verbose_name_plural = 'Geographic Information System Detail Records'
        ordering = ['title']

    def __str__(self):
        return f"{self.title}"


# Sector Type
class SectorType(AuditBaseModel):
    order = models.IntegerField(verbose_name='Order', null=True, blank=True)
    name = models.CharField(verbose_name='Sector Type Name', max_length=350, unique=True)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Sector Type'
        verbose_name_plural = 'Sector Types'
        ordering = ('order', 'name')


# Sector Model
class Sector(AuditBaseModel):
    sector_type = models.ForeignKey(SectorType, verbose_name='Sector Type', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Sector Name', max_length=350)
    parent_sector = models.ForeignKey('self', verbose_name='Parent Sector', on_delete=models.PROTECT, null=True,
                                      blank=True, db_index=True)
    associated_gis_record = models.ForeignKey(GISRecord, verbose_name='Associated GIS Record', on_delete=models.CASCADE,
                                              null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.sector_type})'

    class Meta:
        verbose_name = 'Geographical Sector'
        verbose_name_plural = 'Geographical Sectors'
        ordering = ('sector_type', 'name')

    def has_subordinates(self):
        return Sector.objects.values('id').filter(is_active=True, parent_sector=self).exists()

    def get_subordinates(self):
        return Sector.objects.filter(is_active=True, parent_sector=self).order_by('sector_type', 'name')

    def get_all_parents(self):
        """
        This function returns a list of all parent sectors recursively from the current sector
        to the top-level parent sector (the root).
        """
        parents = []
        current_sector = self
        first = current_sector

        while current_sector.parent_sector:
            parents.append(current_sector.parent_sector)
            current_sector = current_sector.parent_sector
        if first:
            parents.append(first)

        return parents


# Person Model
class Person(AuditBaseModel):
    user = models.OneToOneField(User, verbose_name='User Account', null=True, blank=True, on_delete=models.CASCADE)
    identifier = models.CharField(verbose_name='Identification Document', max_length=100)
    full_name = models.CharField(verbose_name='Full Name', max_length=800)
    first_last_name = models.CharField(verbose_name='First Last Name', max_length=500)
    second_last_name = models.CharField(verbose_name='Second Last Name', max_length=500)
    phone_number = models.CharField(verbose_name='Phone Number', max_length=25)
    mobile_number = models.CharField(verbose_name='Mobile Number', max_length=25)
    primary_street = models.CharField(verbose_name='Primary Street', max_length=300)
    secondary_street = models.CharField(verbose_name='Secondary Street', max_length=300)
    reference_point = models.CharField(verbose_name='Reference Point', max_length=300)
    country = models.ForeignKey(Sector, related_name='country', verbose_name='Country', null=True, blank=True,
                                on_delete=models.CASCADE)
    province = models.ForeignKey(Sector, related_name='province', verbose_name='Province', null=True, blank=True,
                                 on_delete=models.CASCADE)
    canton = models.ForeignKey(Sector, related_name='canton', verbose_name='Canton', null=True, blank=True,
                               on_delete=models.CASCADE)
    parish = models.ForeignKey(Sector, related_name='parish', verbose_name='Parish', null=True, blank=True,
                               on_delete=models.CASCADE)
    location_point = spatialmodels.PointField(srid=3857)

    def __str__(self):
        return f'{self.identifier} - {self.full_name} {self.first_last_name} {self.second_last_name}'

    class Meta:
        verbose_name = 'Individual'
        verbose_name_plural = 'Individuals'
        ordering = ('first_last_name', 'second_last_name', 'full_name')
        constraints = [
            models.UniqueConstraint(fields=['identifier'], name='unique_identifier')
        ]

    def complete_name(self):
        return f'{self.full_name} {self.first_last_name} {self.second_last_name}'

    def short_name(self):
        return f'{self.full_name.split(" ")[0]} {self.first_last_name}'


# Category Model
class Category(AuditBaseModel):
    name = models.CharField(verbose_name='Category Name', max_length=300)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Research Category'
        verbose_name_plural = 'Research Categories'
        ordering = ('name',)

    def get_subcategories(self):
        return self.subcategory_set.filter(is_active=True)


# Subcategory Model
class SubCategory(AuditBaseModel):
    category = models.ForeignKey(Category, verbose_name='Parent Category', null=True, blank=True,
                                 on_delete=models.PROTECT)
    name = models.CharField(verbose_name='Subcategory Name', max_length=300)

    def __str__(self):
        return f'{self.category} - {self.name}'

    class Meta:
        verbose_name = 'Research Subcategory'
        verbose_name_plural = 'Research Subcategories'
        ordering = ('name',)

    def get_indicators(self):
        return self.indicator_set.filter(is_active=True)


# Indicator Model
class Indicator(AuditBaseModel):
    subcategory = models.ForeignKey(SubCategory, verbose_name='Parent Subcategory', null=True, blank=True,
                                    on_delete=models.PROTECT)
    name = models.CharField(verbose_name='Indicator Name', max_length=300)

    def __str__(self):
        return f'{self.subcategory} - {self.name}'

    class Meta:
        verbose_name = 'Research Indicator'
        verbose_name_plural = 'Research Indicators'
        ordering = ('name',)

    def get_indicator_data(self):
        return self.indicatordata_set.filter(is_active=True)


# GIS Data Types for Template
GEODATA_TYPE_CHOICES = (
    (0, 'NONE'),
    (1, 'POINT'),
    (2, 'LINE'),
    (3, 'POLYGON'),
)

# Value Types for Template
VALUE_TYPE_CHOICES = (
    (0, 'NONE'),
    (1, 'INTEGER'),
    (2, 'PERCENTAGE'),
    (3, 'NUMBER'),
    (4, 'DECIMAL NUMBER'),
    (5, 'TEXT'),
)


# Source Type Model
class SourceType(AuditBaseModel):
    name = models.CharField(verbose_name='Source Type Name', max_length=350)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Data Source Type'
        verbose_name_plural = 'Data Source Types'
        ordering = ('name',)


# Template for Indicators
class IndicatorTemplate(AuditBaseModel):
    person = models.ForeignKey(Person, verbose_name='Related Individual', null=True, blank=True,
                               on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, verbose_name='Research Indicator', null=True, blank=True,
                                  on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Description', default='')

    def __str__(self):
        return f'{self.indicator}: {self.description}'

    class Meta:
        verbose_name = 'Indicator Data Template'
        verbose_name_plural = 'Indicator Data Templates'
        ordering = ('indicator', 'pk')


# Extra Data Template
class ExtraDataTemplate(AuditBaseModel):
    indicator_data = models.ForeignKey(IndicatorTemplate, verbose_name='Indicator Data', null=True, blank=True,
                                       on_delete=models.CASCADE)
    value_type = models.IntegerField(verbose_name='Value Type', choices=VALUE_TYPE_CHOICES, default=3)
    name = models.CharField(verbose_name='Field Name', max_length=350)
    precision = models.IntegerField(default=0)
    short_name = models.CharField(verbose_name='Short name', default='')  # Field to export shapefile

    class Meta:
        verbose_name = 'Extra Data Template'
        verbose_name_plural = 'Extra Data Templates'
        ordering = ('name',)

    def save(self, *args, **kwargs):
        # Generar una abreviación del campo 'name', eliminando espacios y limitando a 10 caracteres
        self.short_name = self.generate_short_name(self.name)
        super(ExtraDataTemplate, self).save(*args, **kwargs)

    def generate_short_name(self, name):
        # Eliminar espacios y acortar el nombre a un máximo de 10 caracteres
        short_name = name.replace(' ', '')[:10].lower()  # Quitar espacios y limitar a 10 caracteres
        return short_name

    def get_value_example_by_type(self):
        if self.value_type == 0:
            return ''
        if self.value_type == 1:
            return 10
        if self.value_type == 2:
            return 100
        if self.value_type == 3:
            return 1
        if self.value_type == 4:
            if self.precision:
                return round(2.3554, self.precision)
            return round(2.3554, 2)
        if self.value_type == 5:
            return 'Test'
        return ''


# GIS Template Model
class GISTemplate(AuditBaseModel):
    # Geographic location (Sector)
    sector = models.ForeignKey(Sector, verbose_name='Geographical Sector', on_delete=models.PROTECT, null=True,
                               blank=True)
    # Indicator Data
    indicator_data = models.OneToOneField(IndicatorTemplate, verbose_name='Indicator Data', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'GIS Data Template'
        verbose_name_plural = 'GIS Data Templates'
        ordering = ('sector', 'indicator_data')

    def __str__(self):
        return f'{self.sector} - {self.indicator_data}'

    def get_geom_type(self):
        return self.sector.associated_gis_record.get_gis_type_display()


class IndicatorRecord(AuditBaseModel):
    indicator_template = models.ForeignKey(IndicatorTemplate, verbose_name='Template', on_delete=models.SET_NULL,
                                           blank=True, null=True)
    source_type = models.ForeignKey(SourceType, verbose_name='Source type', on_delete=models.PROTECT)
    indicator = models.ForeignKey(Indicator, verbose_name='Indicator', on_delete=models.PROTECT)
    sector = models.ForeignKey(Sector, verbose_name='Sector', on_delete=models.PROTECT)
    gis = models.ForeignKey(GISRecord, verbose_name='Gis', on_delete=models.SET_NULL, null=True, blank=True)
    name = models.CharField(max_length=500, verbose_name='Name')
    value = models.FloatField(verbose_name='Value', default=0.0)
    date = models.DateField(verbose_name='Date', null=True, blank=True)

    class Meta:
        verbose_name = 'Record indicator'
        verbose_name_plural = 'Records indicators'
        ordering = ['name']
