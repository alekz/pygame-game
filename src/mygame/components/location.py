from mygame.components import Component

class LocationComponent(Component):

    def __init__(self, coord=(0, 0), offset=(0.0, 0.0)):
        self.coord = coord
        self.offset = offset

    @property
    def coord(self):
        return (self.xc, self.yc)

    @coord.setter
    def coord(self, value):
        self.xc = value[0]
        self.yc = value[1]

    @property
    def offset(self):
        return (self.xo, self.yo)

    @offset.setter
    def offset(self, value):
        self.xo = value[0]
        self.yo = value[1]

    @property
    def location(self):
        return (self.x, self.y)

    @property
    def xc(self):
        return self._xc

    @xc.setter
    def xc(self, value):
        self._xc = int(value)

    @property
    def yc(self):
        return self._yc

    @yc.setter
    def yc(self, value):
        self._yc = int(value)

    @property
    def xo(self):
        return self._xo

    @xo.setter
    def xo(self, value):
        self._xo = float(value)

    @property
    def yo(self):
        return self._yo

    @yo.setter
    def yo(self, value):
        self._yo = float(value)

    @property
    def x(self):
        return self._xc + self._xo

    @x.setter
    def x(self, value):
        self.xc = value[0]
        self.xo = value[1]

    @property
    def y(self):
        return self._yc + self._yo

    @y.setter
    def y(self, value):
        self.yc = value[0]
        self.yo = value[1]
