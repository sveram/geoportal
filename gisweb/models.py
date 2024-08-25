from datetime import datetime
from django.db import models
from django.contrib.auth.models import User
from django.contrib.gis.db import models as spatialmodels


# Create your models here.

class BaseModel(models.Model):
    status = models.BooleanField(default=True, verbose_name='Estado')
    create_user = models.ForeignKey(User, related_name='+', verbose_name=u'Usuario de creación', null=True, blank=True,
                                    on_delete=models.PROTECT)
    modify_user = models.ForeignKey(User, related_name='+', verbose_name=u'Usuario de modificación', null=True,
                                    blank=True, on_delete=models.PROTECT)
    create_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True, verbose_name='Fecha de creación')
    update_datetime = models.DateTimeField(auto_now_add=True, null=True, blank=True,
                                           verbose_name='Fecha de modificación')

    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        user = None
        if len(args):
            user = args[0].user.id
        if self.id:
            self.modify_user_id = user if user else None
            self.update_datetime = datetime.now()
        else:
            self.create_user_id = user if user else None
            self.create_datetime = datetime.now()
        models.Model.save(self)


TYPE_GIS = (
    (0, 'File'),
    (1, 'Point'),
    (2, 'LineString'),
    (3, 'Polygon'),
    (4, 'MultiPoint'),
    (5, 'MultiLineString'),
    (6, 'MultiPolygon'),
    (7, 'RasterFile'),
)


class GISModel(BaseModel):
    type_gis = models.IntegerField(verbose_name='Tipo de valor', choices=TYPE_GIS, default=0)
    file = models.FileField(upload_to='GISModels/%Y/%m/%d', null=True, blank=True)
    # Datos geograficos lineales
    point = spatialmodels.PointField(verbose_name='Punto', srid=3857, null=True, blank=True)
    linestring = spatialmodels.LineStringField(verbose_name='Linea', srid=3857, null=True, blank=True)
    polygon = spatialmodels.PolygonField(verbose_name='Poligono', srid=3857, null=True, blank=True)
    # Datos geograficos multiple
    multipoint = spatialmodels.MultiPointField(verbose_name='Multipunto', srid=3857, null=True, blank=True)
    multilinestring = spatialmodels.MultiLineStringField(verbose_name='Multilinea', srid=3857, null=True, blank=True)
    multipolygon = spatialmodels.MultiPolygonField(verbose_name='Multipoligono', srid=3857, null=True, blank=True)

    # Datos geografico raste
    # raster = spatialmodels.RasterField(verbose_name='Raster', srid=3857)

    class Meta:
        verbose_name = 'Modelo GIS'
        verbose_name_plural = 'Modelos GIS'
        ordering = ['id']

    def __str__(self):
        return f"{self.get_type_gis_display()}"


class GISDetail(BaseModel):
    gismodel = models.ForeignKey(GISModel, verbose_name='GIS', null=True, blank=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=500, verbose_name='Nombre', null=True, blank=True)
    detail = models.TextField(verbose_name='Detalle', null=True, blank=True)

    class Meta:
        verbose_name = 'Detalle GIS'
        verbose_name_plural = 'Detalles GIS'
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"


class TypeSector(BaseModel):
    name = models.CharField(verbose_name='Nombre', max_length=350)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Tipo sector'
        verbose_name_plural = 'Tipos sectores'
        ordering = ('name',)


class Sector(BaseModel):
    type_sector = models.ForeignKey(TypeSector, verbose_name='Tipo sector', on_delete=models.CASCADE)
    name = models.CharField(verbose_name='Nombre', max_length=350)
    sectormaster = models.ForeignKey('self', verbose_name='Sector padre', on_delete=models.PROTECT, null=True,
                                     blank=True)
    gismodel = models.ForeignKey(GISModel, verbose_name='GIS', on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f'{self.name} ({self.type_sector})'

    class Meta:
        verbose_name = 'Sector'
        verbose_name_plural = 'Sectores'
        ordering = ('type_sector', 'name')

    def subordinados(self):
        return Sector.objects.values('id').filter(status=True, sectormaster=self).exists()

    def loadsubordinados(self):
        return Sector.objects.filter(status=True, sectormaster=self).order_by('type_sector', 'name')


# class Pais(BaseModel):
#     name = models.CharField(verbose_name='Nombre',max_length=500)
#     reference = spatialmodels.PolygonField(srid=3857)
#
#     def __str__(self):
#         return f'{self.name}'
#
#     class Meta:
#         verbose_name = 'Pais'
#         verbose_name_plural = 'Paises'
#         ordering = ('name',)
#
# class Provincia(BaseModel):
#     pais = models.ForeignKey(Pais,verbose_name='Pais',null=True,blank=True,on_delete=models.CASCADE)
#     name = models.CharField(verbose_name='Nombre', max_length=500)
#     reference = spatialmodels.PolygonField(srid=3857)
#
#     def __str__(self):
#         return f'{self.name}'
#
#     class Meta:
#         verbose_name = 'Provincia'
#         verbose_name_plural = 'Provincias'
#         ordering = ('name',)
#
# class Canton(BaseModel):
#     provincia = models.ForeignKey(Provincia,verbose_name='Provincia',null=True,blank=True,on_delete=models.CASCADE)
#     name = models.CharField(verbose_name='Nombre', max_length=500)
#     reference = spatialmodels.PolygonField(srid=3857)
#
#     def __str__(self):
#         return f'{self.name}'
#
#     class Meta:
#         verbose_name = 'Canton'
#         verbose_name_plural = 'Cantones'
#         ordering = ('name',)
#
# class Parroquia(BaseModel):
#     canton = models.ForeignKey(Canton,verbose_name='Canton',null=True,blank=True,on_delete=models.CASCADE)
#     name = models.CharField(verbose_name='Nombre', max_length=500)
#     reference = spatialmodels.PolygonField(srid=3857)
#
#     def __str__(self):
#         return f'{self.name}'
#
#     class Meta:
#         verbose_name = 'Parroquia'
#         verbose_name_plural = 'Parroquias'
#         ordering = ('name',)

class Person(BaseModel):
    user = models.OneToOneField(User, verbose_name=u'Usuario', null=True, blank=True, on_delete=models.CASCADE)
    identificador = models.CharField(verbose_name='Documento de identidad', max_length=100)
    fullname = models.CharField(verbose_name='Nombres completos', max_length=800)
    lastname = models.CharField(verbose_name='Apellido 1', max_length=500)
    surname = models.CharField(verbose_name='Apellido 2', max_length=500)
    telephone = models.CharField(verbose_name='Telefono', max_length=25)
    mobile = models.CharField(verbose_name='Telefono celular', max_length=25)
    principal_street = models.CharField(verbose_name='Calle 1', max_length=300)
    secundary_street = models.CharField(verbose_name='Calle 2', max_length=300)
    reference_direction = models.CharField(verbose_name='Referecia', max_length=300)
    pais = models.ForeignKey(Sector, related_name='pais', verbose_name='Pais', null=True, blank=True,
                             on_delete=models.CASCADE)
    provincia = models.ForeignKey(Sector, related_name='provincia', verbose_name='Provincia', null=True, blank=True,
                                  on_delete=models.CASCADE)
    canton = models.ForeignKey(Sector, related_name='canton', verbose_name='Canton', null=True, blank=True,
                               on_delete=models.CASCADE)
    parroquia = models.ForeignKey(Sector, related_name='parroquia', verbose_name='Parroquia', null=True, blank=True,
                                  on_delete=models.CASCADE)
    ubication = spatialmodels.PointField(srid=3857)

    def __str__(self):
        return f'{self.identificador} - {self.fullname} {self.lastname} {self.surname}'

    class Meta:
        verbose_name = 'Persona'
        verbose_name_plural = 'Personas'
        ordering = ('lastname', 'surname', 'fullname')
        unique_together = ('identificador',)

    def fully_names(self):
        return f'{self.fullname} {self.lastname} {self.surname}'

    def minus_names(self):
        return f'{self.fullname.split(" ")[0]} {self.lastname}'


class Category(BaseModel):
    name = models.CharField(verbose_name='Nombre de la categoría', max_length=300)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'
        ordering = ('name',)

    def subcategorias(self):
        return self.subcategory_set.filter(status=True)


class SubCategory(BaseModel):
    category = models.ForeignKey(Category, verbose_name='Categoría', null=True, blank=True, on_delete=models.PROTECT)
    name = models.CharField(verbose_name='Nombre de la subcategoría', max_length=300)

    def __str__(self):
        return f'{self.category} - {self.name}'

    class Meta:
        verbose_name = 'Sub Categoría'
        verbose_name_plural = 'Sub Categorías'
        ordering = ('name',)

    def indicadores(self):
        return self.indicator_set.filter(status=True)


class Indicator(BaseModel):
    subcategory = models.ForeignKey(SubCategory, verbose_name='Sub Categoría', null=True, blank=True,
                                    on_delete=models.PROTECT)
    name = models.CharField(verbose_name='Nombre del indicador', max_length=300)

    def __str__(self):
        return f'{self.subcategory} - {self.name}'

    class Meta:
        verbose_name = 'Indicador'
        verbose_name_plural = 'Indicadores'
        ordering = ('name',)

    def dataindicadores(self):
        return self.indicatordata_set.filter(status=True)


TYPE_GEODATA = (
    (0, 'NINGUNA'),
    (1, 'PUNTO'),
    (2, 'LINEA'),
    (3, 'POLIGONO'),
)

TYPE_VALUE = (
    (0, 'NINGUNO'),
    (1, 'ENTERO'),
    (2, 'PORCENTAJE'),
)


class TypeSource(BaseModel):
    name = models.CharField(verbose_name='Nombre', max_length=350)

    def __str__(self):
        return f'{self.name}'

    class Meta:
        verbose_name = 'Tipo de fuente'
        verbose_name_plural = 'Tipos de fuentes'
        ordering = ('name',)


class IndicatorData(BaseModel):
    typesource = models.ForeignKey(TypeSource, verbose_name='Tipo de fuente', null=True, blank=True, on_delete=models.CASCADE)
    person = models.ForeignKey(Person, verbose_name='Persona', null=True, blank=True, on_delete=models.CASCADE)
    indicator = models.ForeignKey(Indicator, verbose_name='Indicador', null=True, blank=True, on_delete=models.CASCADE)
    description = models.TextField(verbose_name='Descripción', default='')
    type_value = models.IntegerField(verbose_name='Tipo de valor', choices=TYPE_VALUE, default=0)
    value = models.IntegerField(verbose_name='Valor', default=0)

    def __str__(self):
        return f'{self.indicator}: {self.value}({self.type_value})'

    class Meta:
        verbose_name = 'Información indicador'
        verbose_name_plural = 'Información indicadores'
        ordering = ('indicator', 'pk')


class IndicatorDataExtra(BaseModel):
    class TypeIndicator:
        NUMBER = 'NUMERO'
        TEXT = 'TEXTO'
        LIST = 'LISTA'  # EJ. [1,2,3,4]
        JSON = 'JSON'  # EJ {'data':{'ejemplo':'prueba'}}

    inidatordata = models.ForeignKey(IndicatorData, verbose_name='Indicador', null=True, blank=True, on_delete=models.CASCADE)
    type_value = models.IntegerField(verbose_name='Tipo de valor', choices=TYPE_VALUE, default=TypeIndicator.NUMBER)
    name = models.CharField(verbose_name='Nombre', max_length=350)
    value = models.TextField(verbose_name='Valor')


class Indicator(models.Model):
    # Ubicación geográfica (Sector)
    sector = models.ForeignKey(Sector, verbose_name='Sector', on_delete=models.PROTECT)
    # Tipo de geografía (GIS Model)
    gis_model = models.ForeignKey(GISModel, verbose_name='Modelo GIS', on_delete=models.CASCADE)
    # Datos del Indicador
    indicator_data = models.ForeignKey(IndicatorData, verbose_name='Datos del Indicador', on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'Registro del Formulario'
        verbose_name_plural = 'Registros del Formulario'
        ordering = ('sector', 'gis_model', 'indicator_data')

    def __str__(self):
        return f'{self.sector} - {self.gis_model} - {self.indicator_data}'
