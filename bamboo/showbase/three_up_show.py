"""ThreeUpShow is a variant of Window that defines three cameras covering
different parts of the window."""

__all__ = ['ThreeUpShow']

from bamboo.showbase import Window


class ThreeUpShow(Window):
    def __init__(self):
        Window.__init__(self)

    def makeCamera(self, win, sort=0, scene=None,
                   displayRegion=(0, 1, 0, 1), stereo=None,
                   aspectRatio=None, clearDepth=0, clearColor=None,
                   lens=None, camName='cam', mask=None,
                   useCamera=None):
        self.camRS = Window.ShowBase.make_camera(
            self, win, displayRegion=(.5, 1, 0, 1), aspectRatio=.67, camName='camRS')
        self.camLL = Window.ShowBase.make_camera(
            self, win, displayRegion=(0, .5, 0, .5), camName='camLL')
        self.camUR = Window.ShowBase.make_camera(
            self, win, displayRegion=(0, .5, .5, 1), camName='camUR')
        return self.camUR


if __name__ == "__main__":
    a = ThreeUpShow()
    a.run()
