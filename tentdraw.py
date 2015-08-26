from osgeo import ogr
import math
import csv

def tent_defs(input_file):
    '''creates tent definition list of dictionaries'''
    tent_list = []
    unhcr_def = {'id':'99', 'z':'2.2', 'def':[(2, -2), (3.3, -0.7), (3.3, 0.7), (2, 2), (-2, 2), (-3.3, 0.7), (-3.3, -0.7), (-2, -2)]}
    with open(input_file, 'rb') as csv_file:
        reader = list(csv.DictReader(csv_file))
        '''if any(len(row) < 4 for row in reader):
            print "input file must contain 4 columns 'id', 'x', 'y', and 'z'"
        elif ['x', 'y', 'z', 'id'] not in row[0]:
            print "file must have fields 'id', 'x', 'y', and 'z'"
        else:'''
        i = 1
        for row in reader:
            sign_list = [(1, -1), (1, 1), (-1, 1), (-1, -1)]
            vertices = []
            for item in sign_list:
                vertex = (item[0] * (float(row['x'])/2), item[1] * (float(row['y'])/2))
                vertices.append(vertex)
            tent_list.append({'id':row['id'], 'z':row['z'], 'def':vertices})
            i += 1
        tent_list.append(unhcr_def)
        print "%d types of tents defined" %(i)
        return tent_list
        
def draw_tents(input_file, tent_defns):
    ''''''
    shp = ogr.Open(input_file)
    lyr = shp.GetLayer()
    drv = ogr.GetDriverByName('ESRI Shapefile')
    output_file = "drawn_tent.shp"
    output_shp = drv.CreateDataSource(output_file)
    spatial_ref = lyr.GetSpatialRef()
    out_lyr = output_shp.CreateLayer('Tents', spatial_ref, geom_type=ogr.wkbPolygon)
    id_field = ogr.FieldDefn('id', ogr.OFTInteger)
    height_field = ogr.FieldDefn('height', ogr.OFTReal)
    out_lyr.CreateField(id_field)
    out_lyr.CreateField(height_field)
    feature_defn = out_lyr.GetLayerDefn()
    feature = ogr.Feature(feature_defn)
    i = 1
    for feat in lyr:
        feat_id = feat.GetFieldAsString('id')
        tent_def = filter(lambda defn: defn['id'] == feat_id, tent_defns)
        tent = TentPoint(feat, tent_def)
        tent.add_to_feature(feature, out_lyr)
        tent = None
        tent_def = None
        del tent_def
        del tent
        print "%d feature made" % (i)
        i += 1
    output_shp = None
    del output_shp
    print "complete"

class TentPoint(object):
    ''''''
    def __init__(self, input_feat, tent_defn):
        self.feat = input_feat
        self.xval = self.get_point()[0]
        self.yval = self.get_point()[1]
        self.zval = tent_defn[0].get('z')
        self.angle = input_feat.GetFieldAsDouble('angle')
        self.tent_id = input_feat.GetFieldAsInteger('id')
        self.tent_defn = tent_defn[0].get('def')

    def get_point(self):
        ''''''
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
            point_change = (-1*vertice[0] - x_rotate,-1* vertice[1] - y_rotate)
            point = (point_init[0] + point_change[0], point_init[1] + point_change[1])
            out_ring.AddPoint(point[0], point[1])
        out_ring.CloseRings()
        return TentPoint.draw_poly(out_ring)

    def add_to_feature(self, feature, out_lyr):
        '''adds polygon to feature'''
        polygon = self.tent_draw()
        feature.SetGeometry(polygon)
        feature.SetField('id', self.tent_id)
        feature.SetField('height', self.zval)
        out_lyr.CreateFeature(feature)