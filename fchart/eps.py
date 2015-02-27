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
from math import pi, acos, asin, atan2, sin, cos, tan

from fchart.graphics_interface import INCH, DPI, DPMM, POINT, GraphicsInterface, paper_A
from fchart.fonts import FontMetrics




class EPSDrawing(GraphicsInterface):
    def __init__(self, filename, width, height):
        """
        width (horizontal) and height (vertical) in mm
        """
        GraphicsInterface.__init__(self, width, height)
        
        self.psfile = None
        self.set_filename(filename)
        self.pstext=''

        self.set_linewidth(0.1)
        self.set_pen_gray(0.0)
        self.set_fill_gray(0.0)
        self.set_font('Times-Roman', 12*POINT)

        A4w, A4h = paper_A(4)
        self.offsetx = int((A4w - self.gi_width)/2.0*DPMM+0.5)  # points
        self.offsety = int((A4h - self.gi_height)/2.0*DPMM+0.5) # points

        self.set_origin(self.gi_width/2.0,self.gi_height/2.0)
        pass


    def new(self):
        if self.psfile != None:
            self.psfile.close()
            self.psfile = None
            pass
        self.pstext = ''
        self.set_linewidth(0.1)
        self.set_pen_gray(0.0)
        self.set_fill_gray(0.0)
        self.set_font('Times-Roman', 12*POINT)
        pass


    def eps3_header(self, llx, lly, urx, ury):
        self.psfile.write('%!PS-Adobe-3.0 EPSF-3.0\n')
        self.psfile.write('%%LanguageLevel: 2\n')
        self.psfile.write('%%BoundingBox: '+str(llx+self.offsetx)+' '+str(lly+self.offsety)+' '+str(urx+self.offsetx)+' '+str(ury+self.offsety)+'\n')
        self.psfile.write('%%EndComments\n')
        pass
    
    def prolog(self):
        self.psfile.write('%%BeginProlog\n')
        self.psfile.write('/mabdict 20 dict def\n')
        self.psfile.write('mabdict begin\n')
        self.prolog_definitions()
        self.psfile.write('end % of mabdict\n')
        self.psfile.write('%%EndProlog\n')
        pass

    def prolog_definitions(self):
        """
        Definitions and macro's that go into the prolog section of the
        EPS file. This method may be extended by derived classes. If
        extending the method, the first sthing one should do is to
        call PostscriptDrawing.prolog_definitions(self) in order to
        properly define required macro's.
        """
        
        self.psfile.write('/C {% Circle. usage: x y r C\n')
        self.psfile.write('newpath 0 360 arc stroke} bind def\n')
        self.psfile.write('/FC {% Filled circle. usage: x y r FC\n')
        self.psfile.write('newpath 0 360 arc fill} bind def\n')
                        
        self.psfile.write('/PFC{% Circle with . Usage: fillcol strokecol x y r ST\n')
        self.psfile.write('gsave 4 index SG 2 index 2 index 2 index FC 3 index SG\n')
        self.psfile.write('C pop pop grestore\n')
        self.psfile.write('} bind def\n')

        self.psfile.write('/E{% Ellipse. usage: x y posangle long short E\n')
        self.psfile.write('gsave\n')
        self.psfile.write('4 index 4 index translate 2 index rotate\n')
        self.psfile.write('1 index 0 moveto 1 1 360\n')
        self.psfile.write('{ dup cos 3 index mul exch sin 2 index mul lineto\n')
        self.psfile.write('} for closepath stroke grestore} bind def\n')
        self.psfile.write('/FE{% Filled ellipse. usage: x y posangle long short E\n')
        self.psfile.write('gsave\n')
        self.psfile.write('4 index 4 index translate 2 index rotate\n')
        self.psfile.write('1 index 0 moveto 1 1 360\n')
        self.psfile.write('{ dup cos 3 index mul exch sin 2 index mul lineto\n')
        self.psfile.write('} for closepath fill grestore} bind def\n')


        self.psfile.write('/PFE{% Filled ellipse with border. usage: fillcol strokecol x y posangle long short E\n')
        self.psfile.write('gsave\n')
        self.psfile.write('6 index SG 4 index 4 index 4 index 4 index 4 index FE\n')
        self.psfile.write('5 index SG E pop pop grestore} bind def\n')
        self.psfile.write('/SG {setgray} bind def\n')
        pass


    def start_drawing(self):
        self.psfile.write('mabdict begin\ngsave\n')
        self.psfile.write(str(self.offsetx)+' '+str(self.offsety)+' translate\n')
        self.psfile.write(str(DPMM)+' '+str(DPMM)+' scale\n')
        self.psfile.write( str(self.gi_origin_x)+' '+ str(self.gi_origin_y)+' translate\n')
        pass


    def finish_drawing(self):
        self.psfile.write('grestore\nend\n%%Trailer\nshowpage\n%%EOF\n')
        pass


    def save(self):
        GraphicsInterface.save(self)
        self.pstext += 'gsave\n'
        pass

    def restore(self):
        GraphicsInterface.restore(self)
        self.pstext += 'grestore\n'
        pass


    def set_offset(self, offsetx, offsety):
        self.offsetx = offsetx
        self.offsety = offsety
        pass

    def set_linewidth(self, linewidth):
        GraphicsInterface.set_linewidth(self,linewidth)
        self.pstext += str(linewidth)+' setlinewidth\n'
        pass

    def set_pen_gray(self, whiteness):
        GraphicsInterface.set_pen_gray(self,whiteness)
        self.pstext+=str(whiteness)+' SG\n'
        pass

    def set_fill_gray(self, whiteness):
        GraphicsInterface.set_fill_gray(self,whiteness)
        self.pstext+=str(whiteness)+' SG\n'
        pass


    def set_dashed_line(self, on, off, start= 0):
        GraphicsInterface.set_dashed_line(self, on, off, start)
        self.pstext+='['+str(on)+' '+str(off)+'] '+str(start)+ ' setdash\n'
        pass

    def set_solid_line(self):
        GraphicsInterface.set_solid_line(self)
        self.pstext += '[] 0 setdash\n'
        pass

    def moveto(self,x,y):
        self.pstext += str(x)+' '+str(y)+' moveto\n'
        pass

    def translate(self, dx, dy):
        self.pstext += str(dx) +' '+str(dy)+' translate\n'
        pass

    def rotate(self, angle):
        self.pstext += str(angle*180/pi)+' rotate\n'
        pass

    def line(self,startx, starty, endx, endy):
        self.pstext +=str(self.gi_pen_gray)+' SG newpath '+str(startx)+' '+str(starty)+' moveto '+str(endx)+' '+str(endy)+' lineto stroke\n'
        pass
    


    def circle(self, x, y, r, mode='P'):
        if mode == 'P':            
            self.pstext += str(self.gi_pen_gray)+' SG '+str(x)+' '+str(y)+' '+str(r)+' C\n'
        elif mode == 'F':
            self.pstext +=str(self.gi_fill_gray)+' SG '+ str(x)+' '+str(y)+' '+str(r)+' FC\n'
        elif mode == 'PF':
            self.pstext +=str(self.gi_fill_gray)+' '+str(self.gi_pen_gray)+' '+ str(x)+' '+str(y)+' '+str(r)+' PFC\n'
        else:
            print 'Invalid circle mode: '+mode
            pass        
        pass


    def ellipse(self, x, y, rlong, rshort, posangle, mode='P'):
        """
        Position angle in radians. Positive  x through positive y.
        """
        if mode == 'P':            
            self.pstext += str(self.gi_pen_gray)+' SG '+str(x)+' '+str(y)+' '+str(posangle*180/pi)+' '+str(rlong)+' '+str(rshort)+' E\n'
        elif mode == 'F':
            self.pstext += str(self.gi_fill_gray)+' SG '+str(x)+' '+str(y)+' '+str(posangle*180/pi)+' '+str(rlong)+' '+str(rshort)+' FE\n'
        elif mode == 'PF':
            self.pstext += str(self.gi_fill_gray)+' '+str(self.gi_pen_gray)+' '+str(x)+' '+str(y)+' '+str(posangle*180/pi)+' '+str(rlong)+' '+str(rshort)+' PFE\n'
        else:
            print 'Invalid ellipse mode: '+mode
            pass        
        pass
    

    def text_right(self, x, y, text, begin=False, end=False):
        """
        x,y is lower righthand corner of text
        """
        self.pstext += str(x)+' '+str(y)+' moveto ('+text+') show\n'
        pass

    def text(self, text, begin=False, end=False):
        self.pstext += '('+text+') show\n'
        pass


    def text_superscript(self, text, begin=False, end=False):
        prev_fontheight = self.gi_fontsize
        self.set_font(self.gi_font, self.gi_fontsize*0.75)
        self.pstext +='0 '+str(prev_fontheight/3.0) +' rmoveto ('+text+') show 0 '+str(-prev_fontheight/3.0)+' rmoveto\n'
        self.set_font(self.gi_font, prev_fontheight)
        pass


    def text_centred(self, x, y, text, begin=False, end=False):
        """
        text is centred on x,y
        """
        self.pstext += str(x)+' '+str(y)+' moveto ('+text+') dup stringwidth pop -2 div ' + str(-self.gi_fontsize/3.0) + ' rmoveto show\n'
        pass


    def text_left(self,x,y,text,begin=False, end=False):
        """
        x,y is lower righthand corner of text
        """
        self.pstext += str(x)+' '+str(y)+' moveto ('+text+') dup stringwidth pop -1 mul 0  rmoveto show\n'
        pass


    def set_font(self, font='Times-Roman', fontsize=12*POINT):
        """
        Fontscale is the font height in mm.
        """
        GraphicsInterface.set_font(self,font,fontsize)
        self.pstext += '/'+font+' findfont '+str(fontsize)+' scalefont setfont\n'
        pass


    def finish(self):
        """
        Finish the Drawing and close the Postscript file.
        """
        llx = 0
        lly = 0
        urx = int(self.gi_width*DPMM+0.5)
        ury = int(self.gi_height*DPMM+0.5)
        self.psfile = file(self.gi_filename, 'w')
        self.eps3_header(llx, lly, urx, ury)
        self.prolog()
        self.start_drawing()
        self.psfile.write(self.pstext)
        self.finish_drawing()
        self.psfile.close()
        self.psfile = None
        pass
    
    pass




if __name__ == '__main__':
    fm = FontMetrics('font-metrics')

    drawing = EPSDrawing('test.eps', 150,150)
    drawing.set_origin(75,75)
    drawing.set_linewidth(0.2)
    drawing.set_fill_gray(0)
    drawing.set_pen_gray(0.0)

    drawing.line(-35,0,35,0)
    drawing.set_pen_gray(1.0)
    drawing.circle(-35,0,10, 'PF')
    drawing.set_pen_gray(0.0)
    
    drawing.circle(5,1,5,'F')

    drawing.ellipse(0,40,40,10,30*pi/180)

    drawing.set_linewidth(0.2)
    drawing.set_dashed_line(1.0,2.0)
    drawing.circle(-35,0,10, 'P')

    drawing.set_font(fontsize = 6.0)
    drawing.text_right(30,10, 'Leuk geweest?', True, True)

    drawing.translate(10, -30)
    drawing.rotate(-30*pi/180)
    drawing.text_right(0,0, 'NGC M 0123456789', True, True)
    l = fm.string_width(drawing.gi_font, drawing.gi_fontsize, 'NGC M 0123456789')
    drawing.line(0,0,l,0)
    drawing.line(0,0,0,0.667*drawing.gi_fontsize)
    drawing.line(0,0.667*drawing.gi_fontsize,l,0.667*drawing.gi_fontsize)
    drawing.line(l,0.667*drawing.gi_fontsize,l,0)
    drawing.text_left(0,0,'Links ervan?<-',True, True)
    drawing.text_centred(0,-3, 'Gecentreerd',True,True)
    drawing.line(-20,-3,20,-3)
    drawing.rotate(+30*pi/180)
    drawing.translate(-10, 30)

    drawing.text_right(-70, -30, '12',True,False)
    drawing.text_superscript('h')
    drawing.text('13')
    drawing.text_superscript('m')
    drawing.text('47')
    drawing.text_superscript('s', False, True)
    drawing.close()
    pass

__all__ = ['EPSDrawing']
