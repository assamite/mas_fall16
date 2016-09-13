'''
Horn drawer for testing purposes.
'''
import numpy as np
from skimage import draw
from matplotlib import pyplot as plt
from time import time
import math

GENE_LABELS = ['num_points', 'num_arms', 'bend_angle1', 'bend_angle2', 'xstack1', 'ystack1', 'xstack2', 'ystack2', 'radius1', 'radius2']
MIN_GENE_VALUES = [ 3,  6, -np.pi*2, -np.pi*2, -100.0, -100.0, -100.0, -100.0, -50.0, -50.0]
MAX_GENE_VALUES = [18, 12,  np.pi*2,  np.pi*2,  100.0,  100.0,  100.0,  100.0,  50.0,  50.0]
GENE_TYPES = [int, int, float, float, float, float, float, float, int, int]

class Circle():
    '''Basic circle with some utility functions.'''
    def __init__(self, x, y, radius):
        self.x = x
        self.y = y
        self.radius = int(radius)

    def move(self, dx, dy):
        self.x += dx
        self.y += dy

    def rotate(self, angle):
        nx = self.x * np.cos(angle) - self.y * np.sin(angle)
        ny = self.x * np.sin(angle) + self.y * np.cos(angle)
        self.x = nx
        self.y = ny

    def grow(self, delta):
        self.radius += delta


class Horn:
    '''Horns have multiple arms divided evenly in a circular manner. Each arm
    consists of multiple circles stacked together.
    '''
    def __init__(self, num_circles, num_arms):
        self.num_circles = int(np.around(num_circles))
        self.num_arms = int(np.around(num_arms))
        self.circles = [Circle(0,0,0) for i in range(int(num_circles))]

    def stack(self, sx, sy):
        dx = sx / (self.num_circles - 1)
        dy = sy / (self.num_circles - 1)
        for i, c in enumerate(self.circles):
            c.move(i*dx, i*dy)

    def move(self, mx, my):
        for c in self.circles:
            c.move(mx, my)

    def bend(self, angle):
        delta = angle / (self.num_circles - 1)
        for i, c in enumerate(self.circles):
            c.rotate(i*delta)

    def grow(self, radius1, radius2):
        delta = (radius2 - radius1) / (self.num_circles - 1)
        for i, c in enumerate(self.circles):
            c.grow(i*delta)

    def draw(self, image_width, aa=False):
        '''Draw horn(s) into a square 2D numpy array.

        :param int image_width: Width of the square image
        :rtype: 2D numpy array with dtype=uint8
        :returns: Image of the horn(s)
        '''
        img = np.zeros((int(image_width), int(image_width)), dtype=np.uint8)
        imgc = int(image_width / 2)
        arm_angle = 2 * np.pi / self.num_arms

        for a in range(self.num_arms):
            angle = a*arm_angle
            for c in self.circles:
                cx = int(imgc + c.x * np.cos(angle) - c.y * np.sin(angle))
                cy = int(imgc + c.x * np.sin(angle) + c.y * np.cos(angle))
                rad = int(abs(c.radius))
                if aa:
                    rr, cc, val = draw.circle_perimeter_aa(cx, cy, rad)
                    # Remove indeces that are not inside the image borders
                    rrc = (rr < image_width) & (rr >= 0)
                    ccc = (cc < image_width) & (cc >= 0)
                    ind = rrc & ccc
                    rr = rr[ind]
                    cc = cc[ind]
                    val = val[ind]
                    img[rr, cc] = val*255
                else:
                    #rr, cc = draw.circle_perimeter(cx, cy, rad)
                    rr, cc = draw.circle(cx, cy, rad)
                    # Remove indeces that are not inside the image borders
                    rri = (rr < image_width) & (rr >= 0)
                    cci = (cc < image_width) & (cc >= 0)
                    ind = rri & cci
                    rr = rr[ind]
                    cc = cc[ind]
                    img[rr, cc] = 255
        return img


class Genotype:
    def __init__(self,
                 min_gene_values=MIN_GENE_VALUES,
                 max_gene_values=MAX_GENE_VALUES,
                 gene_types=GENE_TYPES):
        self.gene_value_bounds = list(zip(min_gene_values, max_gene_values))
        self.gene_types = gene_types
        self.gene_intervals = np.array([g[1]-g[0] for g in self.gene_value_bounds])
        self.initialise()

    def initialise(self):
        self.genes = np.zeros((len(self.gene_types),))
        for i, bounds in enumerate(self.gene_value_bounds):
            if self.gene_types[i] == int:
                gene = np.random.randint(bounds[0], bounds[1]+1)
            else:
                gene = np.random.random() * (bounds[1] - bounds[0]) + bounds[0]
            self.genes[i] = gene

    def mutate_rp(self):
        '''Random point mutation.
        '''
        i = np.random.randint(0, len(self.genes))
        bounds = self.gene_value_bounds[i]
        if self.gene_types[i] == int:
                gene = np.random.randint(bounds[0], bounds[1]+1)
        else:
            gene = np.random.random() * (bounds[1] - bounds[0]) + bounds[0]
        self.genes[i] = gene

    def get_mutation_rp(self):
        '''Get copy of this genotype with one random point mutation.
        '''
        g = Genotype()
        g.genes = np.array(self.genes, copy=True)
        g.mutate_rp()
        return g

    def get_mutation(self, rad=0.1):
        '''Get copy of this genotype with radius mutation for each gene.

        :param float rad: radius of normal distribution, between 0.0 and 1.0
        '''
        g = Genotype()
        g.genes = np.array(self.genes, copy=True)
        rng = np.random.normal(0.0, rad, g.genes.shape)
        for i in range(len(g.genes)):
            gene = g.genes[i]
            ming = self.gene_value_bounds[i][0]
            maxg = self.gene_value_bounds[i][1]
            mm = maxg - ming
            mm = mm / 2.0
            mut = gene + mm*rng[i]
            if mut < ming:
                mut = ming
            elif mut > maxg:
                mut = maxg
            g.genes[i] = mut
        return g

    def dist(self, genes):
        '''Compute distance to genes.'''
        return np.sqrt(np.sum(np.square((self.genes - genes)/self.gene_intervals)))

    def interpolate(self, genotype1, genotype2, pct):
        self.genes = []
        for g1, g2 in zip(genotype1.genes, genotype2.genes):
            gene = g1 + pct * (g2 - g1)
            self.genes.append(gene)


def express(g):
    h = Horn(g.genes[GENE_LABELS.index('num_points')], g.genes[GENE_LABELS.index('num_arms')])
    h.move(g.genes[GENE_LABELS.index('xstack1')], g.genes[GENE_LABELS.index('ystack1')])
    h.bend(g.genes[GENE_LABELS.index('bend_angle1')])
    h.stack(g.genes[GENE_LABELS.index('xstack2')], g.genes[GENE_LABELS.index('ystack2')])
    h.bend(g.genes[GENE_LABELS.index('bend_angle2')])
    h.grow(g.genes[GENE_LABELS.index('radius1')], g.genes[GENE_LABELS.index('radius2')])
    return h


if __name__ == '__main__':
    N = 1
    t = time()
    gen = Genotype(MIN_GENE_VALUES, MAX_GENE_VALUES, GENE_TYPES)
    h = express(gen)
    img = h.draw(512)
    print("{} for {} images.".format(time()-t, N))
    plt.imshow(img, cmap='Greys', interpolation='nearest')
    plt.imsave('test.png', img, cmap='Greys')
    plt.show()

