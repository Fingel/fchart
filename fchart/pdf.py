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
import zlib
import string

from fchart.graphics_interface import INCH, DPI, DPMM, POINT, GraphicsInterface, paper_A
from fchart.fonts import *

from cStringIO import StringIO


EPSILON = 1e-4

ARC_MAGIC = (2**0.5-1)*4.0/3


def check_zero(number):
    r = number
    if abs(number) < EPSILON:
        r = 0.0
        pass
    return r

class PDFObject:
    def __init__(self, number=0, generation=0, text=''):
        self.text=text
        self.number     = number
        self.generation = generation
        pass

    def complete_text(self):
        return str(self.number)+ ' '+str(self.generation)+' obj\n'+self.text\
               +'\nendobj\n'

    pass


class PDFDrawing(GraphicsInterface):

    def __init__(self, filename, width, height, font_metrics, use_compression=True):
        """
        width (horizontal) and height (vertical) in mm
        font_metrics is an object of type fonts.FontMetrics
        """
        GraphicsInterface.__init__(self, width, height)

        self.use_compression = use_compression
        self.font_metrics = font_metrics
        self.object_list = []        
        self.pdf    = None
        self.set_filename(filename)
        
        self.drawingtext=StringIO()
        self.set_linewidth(0.1)
        self.set_font('Times-Roman', 12*POINT)

        self.starttext = '%PDF-1.4\n%\283\200\250\202\n'
        self.xref_list = []

        A4w, A4h = paper_A(4)
        self.set_origin(self.gi_width/2.0, self.gi_height/2.0)
        self.start_drawing()
        pass


    def new(self):
        if self.pdf != None:
            self.pdf.close()
            self.pdf = None
            pass
        self.starttext = '%PDF-1.4\n%\283\200\250\202\n'
        self.drawingtext = StringIO()
        self.xref_list   = []
        self.object_list = []
        self.start_drawing()
        pass



    def start_drawing(self):
        self.object_list.append(PDFObject(1,0,'<< /Type /Catalog  /Pages 2 0 R >>'))
        self.object_list.append(PDFObject(2,0,'<< /Type /Pages /Kids [4 0 R] /Count 1 >>'))
        self.object_list.append(PDFObject(3,0,'[/PDF /Text]'))
        pass



    def finish_drawing(self):
        self.object_list.append(PDFObject(4,0,'<< /Type /Page /Parent \
        2 0 R\n/Resources <<\n/ProcSet 3 0 R\n/Font << /F1 6 0 R >>\n>>\n/MediaBox [ 0 0 '+str(self.gi_width*DPMM)+' '+str(self.gi_height*DPMM)+' ]\n/CropBox  [ 0 0 '+str(self.gi_width*DPMM)+' '+str(self.gi_height*DPMM)+'  ]\n/Contents 5 0 R >>'))


        # scale and translate
        text = str(DPMM)+'  0 0 '+str(DPMM)+' 0 0  cm '+'1 0 0 1 '+str(check_zero(self.gi_origin_x))+' '+str(check_zero(self.gi_origin_y))+' cm '+self.drawingtext.getvalue()
        
        compressed = ''

        if self.use_compression:
            compressed = zlib.compress(text,9)
        else:
            compressed = text
            pass
        contentstr = '<< /Length '+str(len(compressed))
        if self.use_compression:
            contentstr += ' /Filter /FlateDecode'
            pass
        
        self.object_list.append(PDFObject(5,0,contentstr+' >>\nstream\n'+compressed+'\nendstream'))
        self.object_list.append(PDFObject(6,0,'<</Type /Font\n/Subtype /Type1\n/Name /F1\n/BaseFont /Times-Roman\n>>'))

        self.add_crossref_entry(0,65535,'f')
        for object in self.object_list:
            offset = len(self.starttext)
            self.starttext += object.complete_text()
            self.add_crossref_entry(offset,0,'n')
            pass

        xrefoffset = len(self.starttext)
        self.starttext +='xref\n'+'0 '+str(len(self.xref_list))+'\n'
        for xrefline in self.xref_list:
            self.starttext += xrefline
            pass

        self.starttext +='\n\ntrailer\n<< /Size '+str(len(self.xref_list))+'\n/Root 1 0 R >>\n'
        self.starttext += 'startxref\n'+str(xrefoffset)+'\n%%EOF\n'
        pass

    def add_crossref_entry(self,offset, generation, letter='n'):
        line = str(offset).rjust(10).replace(' ','0')+' '+str(generation).rjust(5).replace(' ','0')+' '+letter+' \n'
        self.xref_list.append(line)
        pass


    def save(self):
        GraphicsInterface.save(self)
        self.drawingtext.write('q ')
        pass

    def restore(self):
        GraphicsInterface.restore(self)
        self.drawingtext.write('Q ')
        pass


    def set_linewidth(self, linewidth):
        GraphicsInterface.set_linewidth(self,linewidth)
        self.drawingtext.write(str(check_zero(linewidth))+' w ')
        pass


    def set_pen_gray(self, whiteness):
        GraphicsInterface.set_pen_gray(self, whiteness)
        self.drawingtext.write(str(check_zero(whiteness))+' G ')
        pass

    def set_fill_gray(self, whiteness):
        GraphicsInterface.set_fill_gray(self, whiteness)
        self.drawingtext.write(str(check_zero(whiteness))+' g ')
        pass


    def set_solid_line(self):
        GraphicsInterface.set_solid_line(self)
        self.drawingtext.write('[] 0 d ')
        pass

    def set_dashed_line(self, on, off, start=0.0):        
        GraphicsInterface.set_dashed_line(self, on, off, start)
        self.drawingtext.write('['+str(on)+' '+str(off)+'] '+str(start)+' d ')
        pass

    def line(self, x1,y1,x2,y2):
        x1 = check_zero(x1)
        y1 = check_zero(y1)
        x2 = check_zero(x2)
        y2 = check_zero(y2)
        self.drawingtext.write(str(x1)+' '+str(y1)+' m '+str(x2)+' '+str(y2)+' l S ')
        pass

    def circle(self, x,y,r, mode='P'):
        """
        Draw a circle with centre at (x,y) and radius r. 'mode'
        determines how it  is drawn:
        'P': only draw border with pen
        'F': only fill interior
        'PF': fill interior with fill gray value and draw border with
        pen gray value 
        """

        ra = round (r*ARC_MAGIC,3)
        lstr = str

        strx  = lstr(check_zero(x))
        sxpr  = lstr(check_zero(x+r))
        sxpra = lstr(check_zero(x+ra))
        sxmr  = lstr(check_zero(x-r))
        sxmra = lstr(check_zero(x-ra))

        stry  = lstr(check_zero(y))
        sypr  = lstr(check_zero(y+r))
        sypra = lstr(check_zero(y+ra))
        symr  = lstr(check_zero(y-r))
        symra = lstr(check_zero(y-ra))

        strlist = [sxpr,stry,'m',
                   sxpr,sypra,
                   sxpra,sypr,
                   strx,sypr,'c',
                   sxmra,sypr,
                   sxmr,sypra,
                   sxmr,stry,'c',
                   sxmr,symra,
                   sxmra,symr,
                   strx,symr,'c',
                   sxpra,symr,
                   sxpr,symra,
                   sxpr,stry,'c h']

        if mode == 'P':
            m = 'S'
        elif mode == 'F':
            m = 'f'
        elif mode == 'PF':
            m = 'B'
        else:
            print 'PDFDrawing.circle: invalid mode'
            m = 'S'
            pass
        
        self.drawingtext.write(string.joinfields(strlist+[m,' ']))
        pass



    def ellipse(self,x,y,rlong,rshort, posangle, mode='P'):
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
        arc_magic = ARC_MAGIC

        sp = check_zero(sin(posangle))
        cp = check_zero(cos(posangle))
        x = check_zero(x)
        y = check_zero(y)

        rlong = check_zero(rlong)
        rshort = check_zero(rshort)
        
        # translate
        strlist = ['q','1 0 0 1', str(x), str(y), 'cm']
        # rotate
        strlist += [str(cp),str(sp),str(-sp),str(cp),'0 0 cm']

        lstr = str
        strlist += [lstr(rlong),'0 m', lstr(rlong),lstr(rshort*arc_magic),
                    lstr(rlong*arc_magic),lstr(rshort),'0',lstr(rshort),'c',
                    lstr(-rlong*arc_magic),lstr(+rshort),
                    lstr(-rlong),lstr(+rshort*arc_magic),
                    lstr(-rlong),'0 c',
                    lstr(-rlong),lstr(-rshort*arc_magic),
                    lstr(-rlong*arc_magic),lstr(-rshort),
                    '0',lstr(-rshort),'c',
                    lstr(+rlong*arc_magic),lstr(-rshort),
                    lstr(+rlong),lstr(-rshort*arc_magic),
                    lstr(+rlong),'0 c h']
        
        if mode == 'P':
            m = 'S'
        elif mode == 'F':
            m = 'f'
        elif mode == 'PF':
            m = 'B'
        else:
            print 'PDFDrawing.ellipse: invalid mode'
            m = 'S'
            pass
        strlist += [m, 'Q ']
        self.drawingtext.write(string.joinfields(strlist))
        pass


    def text(self,text, begin=False, end=False):
        if begin:
            self.drawingtext.write('BT\n')
            pass
            
        self.drawingtext.write('/F1 '+str(self.gi_fontsize)+' Tf\n'\
                               +'('+text+') Tj\n')
        if end:
            self.drawingtext.write('ET\n')
            pass
        pass


    def text_superscript(self,text, begin=False, end=False):
        if begin:
            self.drawingtext.write('BT\n')
            pass

        oldsize = self.gi_fontsize
        self.drawingtext.write('/F1 '+str(self.gi_fontsize)+' Tf\n'\
                               +str(oldsize/3.0)+' Ts\n'\
                               '/F1 '+str(self.gi_fontsize*0.75)+' Tf\n'\
                               +'('+text+') Tj\n'\
                               +'/F1 '+str(oldsize)+' Tf\n'\
                               +'0 Ts\n')

        if end:
            self.drawingtext.write('ET\n')
            pass
        pass


    def text_right(self, x, y, text, begin=False, end=False):
        if begin:
            self.drawingtext.write('BT\n')
            pass

        x = check_zero(x)
        y = check_zero(y)
        
        self.drawingtext.write('/F1 '+str(self.gi_fontsize)+' Tf\n'\
                               +'1 0 0 1 '+str(x)+' '+str(y)+' Tm ('+text+') Tj\n')
        
        if end:
            self.drawingtext.write('ET\n')
            pass
        pass


    def text_left(self, x, y, text, begin=False, end=False):
        dx = self.font_metrics.string_width(self.gi_font, self.gi_fontsize, text)
        if begin:
            self.drawingtext.write('BT\n')
            pass

        x = check_zero(x)
        y = check_zero(y)
        dx = check_zero(dx)

        self.drawingtext.write('/F1 '+str(self.gi_fontsize)+' Tf\n'\
                               +'1 0 0 1 '+str(x-dx)+' '+str(y)+' Tm ('+text+') Tj\n')
        
        if end:
            self.drawingtext.write('ET\n')
            pass
        pass
    
    
    def text_centred(self,x,y,text,begin=False, end=False):
        dx = self.font_metrics.string_width(self.gi_font, self.gi_fontsize, text)
        dy = self.gi_fontsize/3.0

        x = check_zero(x)
        y = check_zero(y)
        dx = check_zero(dx)
        dy = check_zero(dy)
        

        if begin:
            self.drawingtext.write('BT\n')
            pass

        self.drawingtext.write('/F1 '+str(self.gi_fontsize)+' Tf\n'\
                               +'1 0 0 1 '+str(x-dx/2.0)+' '+str(y-dy)+' Tm ('+text+') Tj\n')
        
        if end:
            self.drawingtext.write('ET\n')
            pass
        pass



    def moveto(self,x,y):
        x = check_zero(x)
        y = check_zero(y)
        self.drawingtext.write(str(x)+' '+str(y)+' m ')
        pass


    def translate(self, dx, dy):
        dx = check_zero(dx)
        dy = check_zero(dy)
        self.drawingtext.write('1 0 0 1 '+str(dx)+' '+str(dy)+' cm ')
        pass



    def rotate(self, angle):
        sa = check_zero(sin(angle))
        ca = check_zero(cos(angle))
        self.drawingtext.write(str(ca)+' '+str(sa)+' '+str(-sa)+' '+str(ca)+' 0 0 cm ')
        pass

    
    def finish(self):
        self.pdf = file(self.gi_filename, 'w')
        self.finish_drawing()
        self.pdf.write(self.starttext)
        self.pdf.close()
        self.pdf = None
        pass
    
    pass




if __name__ == '__main__':

    fm = FontMetrics('font-metrics')
    
    drawing = PDFDrawing('test.pdf', 150,150, fm, True)
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


__all__ = ['PDFDrawing']
