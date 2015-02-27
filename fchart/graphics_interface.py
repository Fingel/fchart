#    fchart draws beautiful deepsky charts in vector formats
#    Copyright (C) 2005  Michiel Brentjens
#
#    This program is free software; you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation; either version 2 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program; if not, write to the Free Software
#    Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  USA

INCH   = 25.4
DPI    = 72.0
DPMM   = DPI/INCH
POINT  = 1.0/DPMM

def paper_A(n):
    """
    Returns (width, height) of ISO An paper in mm
    """
    w = (2.0**-n/2.0**0.5)**0.5
    h = w*2**0.5
    return (int(1000*w+0.5), int(1000*h+0.5))


class GraphicsInterface:
    """
    A GraphicsInterface has many data members and methods. The default unit is the mm

    gi_width       width of drawing in mm
    gi_height      height of drawing in mm
    gi_pen_gray    gray value of pen (0.0 = black, 1.0 = white)
    gi_fill_gray   gray value of filler
    gi_linewidth   width of the pen line in mm
    gi_font        name of the default font
    gi_fontsize    height of the font in mm
    gi_origin_x    horizontal position of the user coordinate system relative
                   to the bottom left corner of the drawing.
    gi_origin_y    vertical position of the user coordinate system relative
                   to the bottom left corner of the drawing.
    gi_dash_style  line /dash style: ([on, off], start). Solid = ([],0.0)
    gi_stack       graphics state stack.
    """
    def __init__(self, width, height):
        """
        width and height in mm
        """
        self.gi_width     = width*1.0
        self.gi_height    = height*1.0
        self.gi_pen_gray  = 0.0
        self.gi_fill_gray = 0.0
        self.gi_linewidth = 0.1
        self.gi_dash_style = ([], 0.0)
        self.gi_font      = 'Times-Roman'
        self.gi_fontsize  = 12*POINT
        self.gi_origin_x  = self.gi_width/2.0
        self.gi_origin_y  = self.gi_height/2.0

        self.gi_filename = ''
        
        self.gi_stack = []
        pass


    def save(self):
        """
        Save graphics state to stack. This method should be extended,
        not overriden.
        """
        self.gi_stack.append((self.gi_pen_gray,
                              self.gi_fill_gray,
                              self.gi_linewidth,
                              self.gi_dash_style,
                              self.gi_font,
                              self.gi_fontsize))
        pass

    def restore(self):
        """
        Save graphics state to stack. This method should be extended,
        not overriden.
        """

        (self.gi_pen_gray,
         self.gi_fill_gray,
         self.gi_linewidth,
         self.gi_dash_style,
         self.gi_font,
         self.gi_fontsize) = self.gi_stack.pop()
        
        pass

    def new(self):
        """
        Erase all graphics, but keep graphics state (font, fontsize,
        linewidth&style , width, height, origin as they are.
        """
        pass


    def set_filename(self, filename):
        self.gi_filename = filename
        pass

    
    def set_dimensions(self, width, height):
        """
        Sets gi_width and gi_height
        """
        self.gi_width  = width
        self.gi_height = height
        pass


    def set_origin(self, origin_x, origin_y):
        """
        Sets gi_origin_x and gi_origin_y
        """
        self.gi_origin_x = origin_x
        if abs(self.gi_origin_x) < 1e-5:
            self.gi_origin_x = 0.0
            pass
        self.gi_origin_y = origin_y
        if abs(self.gi_origin_y) < 1e-5:
            self.gi_origin_y = 0.0
            pass
        pass
    



    def set_linewidth(self, linewidth):
        """
        Sets gi_linewidth. Derived classes should extend, not override this method.
        """
        self.gi_linewidth = linewidth
        pass


    def set_pen_gray(self, pen_gray):
        """
        Sets gi_pen_gray. Derived classes should extend, not override this method.
        """
        self.gi_pen_gray = pen_gray
        pass


    def set_fill_gray(self, fill_gray):
        """
        Sets gi_fill_gray. Derived classes should extend, not override this method.
        """
        self.gi_fill_gray = fill_gray
        pass


    def set_solid_line(self):
        """
        From now on, all lines should be drawn solid. Extend this method.
        """
        self.gi_dash_style = ([],0.0)
        pass


    def set_dashed_line(self, on, off, start=0.0):
        """
        From now on, all lines should be drawn dashed. \"on\" mm on followed by
        \"off\" mm off. The dash pattern starts \"start\" mm from the beginning of
        the \"on\" pattern. Extend this method
        """
        self.gi_dash_style = ([on, off], start)
        pass




    def set_font(self, font='Times-Roman', fontsize=12*POINT):
        """
        \"font\" is the fontname (a string)
        \"fontsize\" the fontsize in mm.

        This method must be extended by derived classes, not overriden. It sets
        gi_font and gi_fontsize. In order to set a 12 point Helvetica font, use:
        GI.set_font('Helvetica', 12*POINT)
        """

        self.gi_font     = font
        self.gi_fontsize = fontsize
        pass


    def moveto(self,x,y):
        """
        Move to position x,y. Derived classes should override this
        method.
        """
        print 'GraphicsInterface.moveto()'
        pass


    def translate(self, dx, dy):
        """
        Shift origin of coordinate system (dx,dy) mm with respect to
        self.gi_origin_{x,y}
        """
        print 'GraphicsInterface.translate())'
        pass


    def rotate(self, angle):
        """
        Rotate coordinates angle radians around current origin.
        """
        print 'GraphicsInterface.rotate()'
        pass



    def line(self, x1, y1, x2, y2):
        """
        Draw a line from (x1,y1) to (x2,y2) using the current pen gray value, linestyle
        and linewidth.
        """
        print 'GraphicsInterface.line()'
        pass
    

    def circle(self, x, y, r, mode='P'):
        """
        Draw a circle with centre at (x,y) and radius r. 'mode' determines how it is drawn:
        'P': only draw border with pen
        'F': only fill interior
        'PF': fill interior with fill gray value and draw border with pen gray value
        """
        print 'GraphicsInterface.circle()'
        pass

    def ellipse(self, x, y, rlong, rshort, position_angle, mode='P'):
        """
        Draw an ellipse with centre at (x,y) and long radius rlong and
        short radius rshort. position_angle is the angle between the
        long axis and the positive x-axis in radians. 'mode'
        determines how it is drawn: 
        'P': only draw border with pen
        'F': only fill interior
        'PF': fill interior with fill gray value and draw border with
        pen gray value 
        """
        print 'GraphicsInterface.ellipse()'
        pass



    def text(self, text, begin=False, end=False):
        """
        Draw 'text' at the current position. The current position is
        the bottom left corner of the text to be drawn.

        if begin: open text context, if end: close text context
        """
        print 'GraphicsInterface.text()'
        pass

    def text_superscript(self, text, begin=False, end=False):
        """
        Draw 'text' at the current position in superscript.
        if begin: open text context, if end: close text context
        """
        print 'GraphicsInterface.text_superscript()'
        pass


    def text_right(self, x, y, text, begin=False, end=False):
        """
        x, y is the bottom left corner of text
        if begin: open text context, if end: close text context
        """
        print 'GraphicsInterface.text_right()'
        pass


    def text_left(self, x, y, text, begin=False, end=False):
        """
        x, y is the bottom right corner of text
        if begin: open text context, if end: close text context
        """
        print 'GraphicsInterface.text_left()'
        pass

    def text_centred(self, x, y, text, begin=False, end=False):
        """
        Draw text centred at (x,y)
        if begin: open text context, if end: close text context
        """
        print 'GraphicsInterface.text_centred()'
        pass

    
    def finish(self):
        """
        Finalize the drawing (Store to disk, memory, whatever).
        """
        print 'GraphicsInterface.finish()'
        pass
    pass



__all__=['INCH', 'DPI', 'DPMM', 'POINT', 'GraphicsInterface', 'paper_A']
