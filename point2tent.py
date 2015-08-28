from osgeo import ogr
import math
import os
import csv

def tent_defs(input_file):
    '''creates tent definition list of dictionaries'''
    tent_list = []
    unhcr_def = {'type':'99', 'z':'2.2', 'def':[(2, -2), (3.3, -0.7), (3.3, 0.7), (2, 2), (-2, 2), (-3.3, 0.7), (-3.3, -0.7), (-2, -2)]}
    with open(input_file, 'rb') as csv_file:
        reader = list(csv.DictReader(csv_file))
        for row in reader:
            if len(row) < 3:
                print 'Missing one or more fields'
        i = 1
        for row in reader:
            sign_list = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
            vertices = []
            for item in sign_list:
                vtx = (item[0] * (float(row['x'])/2), item[1] * (float(row['y'])/2))
                vertices.append(vtx)
            tent_list.append({'type':row['type'], 'z':row['z'], 'def':vertices})
            i += 1
        tent_list.append(unhcr_def)
        print "%d types of tents defined" %(i)
        return tent_list

def _valid_crs(input_lyr):
    '''tests to make sure input shapefile is in metre projection'''
    spatial_ref = input_lyr.GetSpatialRef()
    sr_unit = spatial_ref.GetAttrValue('UNIT')
    if sr_unit == 'Meter':
        return spatial_ref
    else:
        raise ValueError('Input shapefile is not projected in metres please\
        project')

def _create_feature(input_lyr):
    '''creates feature and adds relevant fields'''
    id_field = ogr.FieldDefn('id', ogr.OFTInteger)
    type_field = ogr.FieldDefn('type', ogr.OFTInteger)
    height_field = ogr.FieldDefn('height', ogr.OFTReal)
    input_lyr.CreateField(id_field)
    input_lyr.CreateField(type_field)
    input_lyr.CreateField(height_field)
    feature_defn = input_lyr.GetLayerDefn()
    feature = ogr.Feature(feature_defn)
    return feature

def draw_tents(input_file, tent_defns, output_file = None):
    '''iterates through points and draws tent polys'''
    shp = ogr.Open(input_file)
    lyr = shp.GetLayer()
    try:
        spatial_ref = _valid_crs(lyr)
    except ValueError as err:
        print err
    if output_file == None:
        base_name = os.path.splitext(input_file)[0]
        output_file = base_name + "_poly.shp"
    else:
        pass
    drv = ogr.GetDriverByName('ESRI Shapefile')
    output_shp = drv.CreateDataSource(output_file)
    out_lyr = output_shp.CreateLayer('Tents', spatial_ref, geom_type=ogr.wkbPolygon)
    feature = _create_feature(out_lyr)
    i = 1
    for feat in lyr:
        feat_type = feat.GetFieldAsString('type')
        tent_def = filter(lambda defn: defn['type'] == feat_type, tent_defns)
        tent = TentPoint(feat, tent_def)
        tent.add_to_feature(feature, out_lyr)
        i += 1
    output_shp = None
    del output_shp
    print "%d feature(s) drawn" % (i)
    print "complete"

class TentPoint(object):
    '''class to define points used to iterate over features in draw_tents 
    function'''
    def __init__(self, input_feat, tent_defn):
        self.feat = input_feat
        self.xval = self.get_point()[0]
        self.yval = self.get_point()[1]
        self.zval = tent_defn[0].get('z')
        self.angle = input_feat.GetFieldAsDouble('angle')
        self.tent_id = input_feat.GetFieldAsInteger('id')
        self.tent_type = input_feat.GetFieldAsInteger('type')
        self.tent_defn = tent_defn[0].get('def')

    def get_point(self):
        '''gets point from feature returns tuple'''
        pt = self.feat.GetGeometryRef()
        coords = pt.GetPoint()
        return coords

    @staticmethod
    def draw_poly(input_ring):
        '''draws polygon geometry'''
        polygon = ogr.Geometry(ogr.wkbPolygon)
        polygon.AddGeometry(input_ring)
        input_ring = None
        del input_ring
        return polygon

    def tent_draw(self):
        '''draws tent ring'''
        out_ring = ogr.Geometry(ogr.wkbLinearRing)
        angle_cos = math.cos(math.radians(self.angle))
        angle_sin = math.sin(math.radians(self.angle))
        for vertice in self.tent_defn:
            point_init = (self.xval + vertice[0], self.yval + vertice[1])
            x_rotate = (vertice[0] * angle_cos - vertice[1] * angle_sin)
            y_rotate = (vertice[0] * angle_sin + vertice[1] * angle_cos)
            point_change = (-1 * vertice[0] - x_rotate, -1 * vertice[1] - y_rotate)
            point = (point_init[0] + point_change[0], point_init[1] + point_change[1])
            out_ring.AddPoint(point[0], point[1])
        out_ring.CloseRings()
        return TentPoint.draw_poly(out_ring)

    def add_to_feature(self, feature, out_lyr):
        '''adds polygon to feature'''
        polygon = self.tent_draw()
        feature.SetGeometry(polygon)
        feature.SetField('id', self.tent_id)
        feature.SetField('type',self.tent_type)
        feature.SetField('height', self.zval)
        out_lyr.CreateFeature(feature)