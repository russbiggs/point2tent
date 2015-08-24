from osgeo import ogr
import timeit
import csv

def tent_defs(input_file):
    '''creates tent definition list of dictionaries'''
    tent_list = []
    with open(input_file, 'rb') as csv_file:
        reader = list(csv.DictReader(csv_file))
        '''if any(len(row) < 4 for row in reader):
            print "input file must contain 4 columns 'id', 'x', 'y', and 'z'"
        elif ['x', 'y', 'z', 'id'] not in row[0]:
            print "file must have fields 'id', 'x', 'y', and 'z'"
        else:'''
        i = 1
        for row in reader:
            sign_list = [(1,-1),(1,1),(-1,1),(-1,-1)]
            vertices = []
            for item in sign_list:
                vertex = (item[0] * (float(row['x'])/2),item[1] * (float(row['y'])/2))
                vertices.append(vertex)
            tent_list.append({'id':row['id'],'z':row['z'],'def':vertices})
            i += 1
        print "%d types of tents defined" %(i)
        return tent_list

class TentPoint(object):
    polygon = ogr.Geometry(ogr.wkbPolygon)
    out_ring = ogr.Geometry(ogr.wkbLinearRing)
    def __init__(self, input_feat, tent_defn):
        self.feat = input_feat
        self.x = self.get_point()[0]
        self.y = self.get_point()[1]
        self.theta = input_feat.GetFieldAsString('angle')
        self.tent_id = input_feat.GetFieldAsString('id')
        self.tent_defn = tent_defn
        self.geom = self

    def get_point(self):
        pt = self.feat.GetGeometryRef()
        coords = pt.GetPoint()
        return coords
    
    def draw_poly(input_ring):
        '''draws polygon geometry'''
        polygon.AddGeometry(input_ring)
        input_ring = None
        del input_ring
        return polygon      

    def tent_draw(self):
        '''draws tent ring'''
        point1 = ((self.x + 2), (self.y - 2))
        point2 = ((self.x  + 3.3), (self.y - 0.7))
        point3 = ((self.x  + 3.3), (self.y + 0.7))
        point4 = ((self.x  + 2), (self.y + 2))
        ring_list = point1, point2, point3, point4
        for item in ring_list:
            out_ring.AddPoint(item[0], item[1])
        out_ring.CloseRings()
        draw_poly(out_ring)
        
        
    def rotate(self):
        
        
    ###############################
    sign_array = [(1,-1),(1,1),(-1,1),(-1,-1)]
    new_list = list(sign_list)
    '''create sign list to make all point create fall into one function
    if a tent (e.g. UNHCR) has more than 4 point use loop to add more sign
    this can also be used for rotation since the onyl change is the sign until the change
    '''
    for item in sign_list:
        new_list.insert(index,item)
    ###########################
    
    
    
    def draw(self):
        for item in sign_array:
            point = (self.x 
    
    
    
    def unhcr_draw(self):
        '''draws unhcr family tent ring'''
        point1 = ((self.x + 2), (self.y - 2))
        point2 = ((self.x + 3.3), (self.y - 0.7))
        point3 = ((self.x + 3.3), (self.y + 0.7))
        point4 = ((self.x + 2), (self.y + 2))
        point5 = ((self.x - 2), (self.y + 2))
        point6 = ((self.x - 3.3), (self.y + 0.7))
        point7 = ((self.x - 3.3), (self.y - 0.7))
        point8 = ((self.x - 2), (self.y - 2))
        ring_list = point1, point2, point3, point4, point5, point6, point7, point8
        def rotation(ring_list):
            for point in ring_list:
                point_rotation = ()
        
        for item in ring_list:
            out_ring.AddPoint(item[0], item[1])
        out_ring.CloseRings()
        draw_poly(out_ring)

    def draw_geom(self):
    '''chooses the correct draw function '''
        if self.tent_defn['id'] == 99:
            self.unhcr_draw()
        else:
            self.tent_draw()