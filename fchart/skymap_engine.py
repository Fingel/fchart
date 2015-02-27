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
from numpy import *
import string
from fchart.label_potential import *
from fchart.astrocalc import *
import fchart.deepsky_object as deepsky


NL = {
    'h':'u',
    'm':'m',
    's':'s',
    'G':'Sterrenstelsel',
    'OCL':'Open sterrenhoop',
    'GCL':'Bolhoop',
    'AST':'Groepje sterren',
    'PN': 'Planetaire nevel',
    'N': 'Diffuse emissienevel',
    'SNR':'Supernovarest',
    'PG':'Deel van sterrenstelsel'
    }


EN = {
    'h':'h',
    'm':'m',
    's':'s',
    'G':'Galaxy',
    'OCL':'Open cluster',
    'GCL':'Globular cluster',
    'AST':'Asterism',
    'PN': 'Planetary nebula',
    'N': 'Diffuse nebula',
    'SNR':'Supernova remnant',
    'PG':'Part of external galaxy'
    }



#====================>>>  SkymapEngine  <<<====================

class SkymapEngine:

    def __init__(self, graphics, font_metrics, language=EN, ra=0.0, dec=0.0, fieldradius=-1.0, lm_stars=13.8, caption=''):
        """
        Width is width of the map including the legend in mm.
        """
        self.graphics = graphics
        self.font_metrics = font_metrics

        self.caption = ''
        self.language = language
        self.drawingwidth = self.graphics.gi_width
        self.min_radius   = 1.0 # of deepsky symbols (mm)
        self.star_border_linewidth = 0.06

        self.lm_stars     = lm_stars
        self.deepsky_label_limit = 15 # deepsky lm for labels

        self.set_caption(caption)
        self.set_field(ra,dec,fieldradius)
        pass

    def set_field(self, ra, dec,fieldradius):
        """
        Provide the RA, DEC, and radius of the map in radians. This method
        sets a new drawingscale and legend_fontscale
        """
        self.fieldcentre         = (ra,dec)
        self.fieldradius         = fieldradius
        self.drawingscale        = self.drawingwidth/2.0*0.98/sin(fieldradius)
        self.legend_fontscale    = self.drawingwidth/100.0

        self.set_caption(self.caption)
        pass


    def set_language(language):
        """
        Set the language of the legend.
        """
        self.language = language
        pass


    def set_caption(self, caption):
        self.caption = caption
        if caption == '':
            self.graphics.set_dimensions(self.drawingwidth, self.drawingwidth)
        else:
            self.graphics.set_dimensions(self.drawingwidth,self.drawingwidth + self.legend_fontscale*self.graphics.gi_fontsize*2.0)
            pass

        pass


    def magnitude_to_radius(self, magnitude):
        #radius = 0.13*1.35**(int(self.lm_stars)-magnitude)
        radius = 0.15*1.33**(int(self.lm_stars)-magnitude)
        return radius



    def draw_magnitude_scale(self,
                             xcentre_stars,
                             ybottom,
                             stars_in_scale=11):
        """
        Draws a vertical magnitude scale with at most \"stars_in_scale\" stars down
        to magnitude -1
        """
        mags_in_scale = int(self.lm_stars) - arange(stars_in_scale)
        legendx = xcentre_stars
        legendy = arange(stars_in_scale)*self.graphics.gi_fontsize + ybottom

        legendr = self.magnitude_to_radius(mags_in_scale)
        self.graphics.set_linewidth(self.star_border_linewidth)

        for i in range(len(legendy)):
            if mags_in_scale[i] >= -1:
                self.star(legendx, legendy[i], legendr[i])
                self.graphics.text_right(legendx+self.graphics.gi_fontsize, legendy[i]-self.graphics.gi_fontsize/3.0, str(mags_in_scale[i]),begin=True, end=True)
                pass
            pass

        pass



    def draw_caption(self):
        if self.caption != '':
            fh = self.graphics.gi_fontsize
            self.graphics.set_font(self.graphics.gi_font, 2.0*fh)
            self.graphics.text_centred(0,self.drawingwidth/2.0+fh, self.caption, begin=True, end=True)
            self.graphics.set_font(self.graphics.gi_font, fh)
            pass
        pass


    def draw_field_border(self):
        """
        Draw a circle representing bthe edge of the field of view.
        """
        self.graphics.set_linewidth(0.15)
        self.graphics.circle(0,0,sin(self.fieldradius)*self.drawingscale)
        pass


    def draw_mapscale(self,x, y, maxlength):
        """
        x,y are the coordinates of the leftmost point of the horizontal line.
        This is excluding the vertical end bars. maxlength is the maximum
        length of the ruler line excluding the endbars.
        """
        # Determine a suitable scale ruler in the topleft corner
        allowed_ruler = array([1,5,10,30,60,120,300.0]) # arcminutes
        allowed_labels = ['1\251', '5\251', '10\251', '30\251', '1\312', '2\312', '5\312']

        maxruler = maxlength
        ruler_mm = allowed_ruler*pi/180/60.0*self.drawingscale
        ruler_label = ''
        ruler_length= 0.0
        for i in range(len(allowed_ruler)):
            if ruler_mm[-(i+1)] <= maxruler:
                ruler_label = allowed_labels[-(i+1)]
                ruler_length= ruler_mm[-(i+1)]
                break
                pass
            pass

        # Draw ruler
        length = ruler_length
        left   = x
        yline  = y

        lw = self.graphics.gi_linewidth

        self.graphics.line(x, y, x+length, y)
        self.graphics.line(x-lw/2.0, y - 0.01*self.drawingwidth,
                           x-lw/2.0, y + 0.01*self.drawingwidth)
        self.graphics.line(x+length+lw/2.0,
                           y -0.01*self.drawingwidth,
                           x+length+lw/2.0,
                           y+0.01*self.drawingwidth)
        self.graphics.text_centred(x+length/2.0,
                                   y-self.graphics.gi_fontsize*2/3.0,
                                   ruler_label,
                                   begin=True, end=True)
        pass



    def draw_coordinates(self, x, y, ra, dec):
        """
        x,y are coordinates of the lower left corner of the textbox
        """
        rah = int(ra*12/pi)
        ram = int((ra*12/pi -rah)*60)
        ras = int(((ra*12/pi -rah)*60 - ram)*60+0.5)
        if ras == 60:
            ram +=1
            ras = 0
            pass
        if ram == 60:
            rah += 1
            ram = 0
            pass
        if rah == 24:
            rah = 0
            pass

        decsign = '+'
        if dec < 0.0:
            decsign = '-'
            pass
        decd= int(abs(dec)*180/pi)
        decm = int((abs(dec)*180/pi-decd)*60)
        decs = int( ((abs(dec)*180/pi-decd)*60 -decm)*60+0.5)

        if decs == 60:
            decm += 1
            decs = 0
            pass
        if decm == 60:
            decd+=1
            decm = 0
            pass

        self.graphics.text_right(x, y, str(rah).rjust(2),begin=True, end=False)
        self.graphics.text_superscript(self.language['h'])
        self.graphics.text(str(ram))
        self.graphics.text_superscript(self.language['m'])
        self.graphics.text(str(ras))
        self.graphics.text_superscript(self.language['s'])
        dectext = ' '+decsign+str(decd)+'\312'+str(decm)+'\251'+str(decs)+'\042'
        self.graphics.text(dectext,begin=False, end=True)
        pass



    def draw_legend(self):
        # Set the fontsize for the entire legend
        self.graphics.set_font(self.graphics.gi_font,
                               fontsize=2.6*self.legend_fontscale)

        self.draw_caption()

        # Draw vertical magnitude scale
        self.draw_magnitude_scale(xcentre_stars= -0.4775*self.drawingwidth,
                                  ybottom=-0.485*self.drawingwidth)

        # Draw border of field-of-view
        self.draw_field_border()

        # Draw scale of map
        self.draw_mapscale(x=-0.49*self.drawingwidth,
                           y=0.48*self.drawingwidth,
                           maxlength=self.drawingwidth/3.0)


        # Draw orientation indication
        x = -0.46*self.drawingwidth
        y =  0.32*self.drawingwidth
        dl = 0.03*self.drawingwidth

        fh = self.graphics.gi_fontsize
        self.graphics.line(x-dl,y, x+dl,y)
        self.graphics.line(x,y-dl, x,y+dl)
        self.graphics.text_centred(x, y+dl+fh/2.0, 'N',begin=True, end=True)
        self.graphics.text_right(x+dl+fh/6.0, y-fh/3.0, 'W',begin=True, end=True)

        # Draw coordinates of fieldcentre
        self.draw_coordinates(x=-0.49*self.drawingwidth,
                              y=0.49*self.drawingwidth -
                              3*fh,
                              ra=self.fieldcentre[0],
                              dec=self.fieldcentre[1])


        # Draw list of symbols
        legendx  = 0.48*self.drawingwidth
        legendy  = 0.49*self.drawingwidth
        legendinc= fh

        r = fh/3.0
        text_offset = -2.5*r


        toplabels=[('OCL', len(self.language['OCL'])),
                   ('AST', len(self.language['AST'])),
                   ('G', len(self.language['G'])),
                   ('GCL', len(self.language['GCL']))]
        bottomlabels=[('SNR', len(self.language['SNR'])),
                      ('N',len(self.language['N'])),
                      ('PN', len(self.language['PN'])),
                      ('PG',len(self.language['PG']))]
        def labsort(x,y):
            r = 0
            if x[1] < y[1]:
                r = -1
            if x[1] > y[1]:
                r = 1
            return r

        toplabels.sort(labsort)
        toplabels.reverse()
        tl = []
        for lab in toplabels:
            tl.append(lab[0])
            pass

        bottomlabels.sort(labsort)
        bottomlabels.reverse()
        bl = []
        for lab in bottomlabels:
            bl.append(lab[0])
            pass

        self.open_cluster(legendx, legendy-(tl.index('OCL')+1)*legendinc,r)
        self.graphics.text_left(legendx+text_offset, legendy-(tl.index('OCL')+1)*legendinc-fh/3.0, self.language['OCL'], begin=True, end=True)

        self.asterism(legendx, legendy-(tl.index('AST')+1)*legendinc,r)
        self.graphics.text_left(legendx+text_offset, legendy-(tl.index('AST')+1)*legendinc-fh/3.0, self.language['AST'],begin=True, end=True)

        self.galaxy(legendx, legendy-(tl.index('G')+1)*legendinc,r)
        self.graphics.text_left(legendx+text_offset, legendy-(tl.index('G')+1)*legendinc- fh/3.0, self.language['G'], begin=True, end=True)

        self.globular_cluster(legendx, legendy-(tl.index('GCL')+1)*legendinc,r)
        self.graphics.text_left(legendx+text_offset, legendy-(tl.index('GCL')+1)*legendinc-fh/3.0, self.language['GCL'], begin=True, end=True)


        legendy = 0.485*self.drawingwidth

        self.supernova_remnant(legendx, -legendy+bl.index('SNR')*legendinc,r)
        self.graphics.text_left(legendx+text_offset, -legendy+bl.index('SNR')*legendinc - fh/3.0, self.language['SNR'],begin=True, end=True)

        self.planetary_nebula(legendx, -legendy+bl.index('PN')*legendinc,r)
        self.graphics.text_left(legendx+text_offset, -legendy+bl.index('PN')*legendinc -  fh/3.0, self.language['PN'],begin=True, end=True)

        self.diffuse_nebula(legendx, -legendy +bl.index('N')*legendinc,r)
        self.graphics.text_left(legendx+text_offset, -legendy+bl.index('N')*legendinc-fh/3.0, self.language['N'], begin=True, end=True)

        self.unknown_object(legendx, -legendy+bl.index('PG')*legendinc,r)
        self.graphics.text_left(legendx+text_offset, -legendy+bl.index('PG')*legendinc-fh/3.0, self.language['PG'], begin=True, end=True)

        pass # end of draw_legend




    def draw_deepsky_objects(self, deepsky_catalog):
        # Draw deep sky
        print 'Drawing deepsky...'
        deepsky_list = deepsky_catalog.select_deepsky(self.fieldcentre,
                                                      self.fieldradius).deepsky_list
        if len(deepsky_list) == 1:
            print '1 deepsky object in map.'
        else:
            print str(len(deepsky_list))+' deepsky objects in map.'
            pass

        deepsky_list.sort(deepsky.cmp_mag)
        deepsky_list_mm = []
        for object in deepsky_list:
            l, m  =  radec_to_lm((object.ra, object.dec), self.fieldcentre)
            x,y   = -l*self.drawingscale, m*self.drawingscale
            rlong  = object.rlong*self.drawingscale
            if object.type == deepsky.GALCL:
                rlong = self.min_radius
                pass
            if rlong < self.min_radius:
                rlong = self.min_radius
            deepsky_list_mm.append((x,y,rlong))
            pass

        label_potential = LabelPotential(sin(self.fieldradius)*self.drawingscale ,deepsky_list_mm)

        print 'Drawing objects...'
        for i in range(len(deepsky_list)):
            object = deepsky_list[i]

            x,y,rlong  = deepsky_list_mm[i]
            rlong  = object.rlong*self.drawingscale
            rshort = object.rshort*self.drawingscale
            posangle=object.position_angle+direction_ddec(\
                (object.ra, object.dec), self.fieldcentre)+0.5*pi

            if rlong <= self.min_radius:
                rshort *= self.min_radius/rlong
                rlong = self.min_radius
                pass

            if object.type == deepsky.GALCL:
                rlong /= 3.0
                pass

            label=''
            if object.messier > 0:
                label = 'M '+str(object.messier)
            elif object.cat == 'NGC':
                object.all_names.sort()
                label = string.join(object.all_names,'-')
                if object.mag > self.deepsky_label_limit:
                    label = ''
                    pass
            else :
                label = object.cat+' '+string.join(object.all_names, '-')
                if object.mag > self.deepsky_label_limit:
                    label = ''
                    pass
                pass

            label_length = self.font_metrics.string_width(self.graphics.gi_font, self.graphics.gi_fontsize, label)
            labelpos = -1

            labelpos_list =[]
            if object.type == deepsky.G:
                labelpos_list = self.galaxy_labelpos(x,y,rlong,rshort,posangle,label_length)
            elif object.type == deepsky.N:
                labelpos_list = self.diffuse_nebula_labelpos(x,y,2.0*rlong,2.0*rshort,posangle,label_length)
            elif object.type in [deepsky.PN,deepsky.OC,deepsky.GC,deepsky.SNR]:
                labelpos_list = self.circular_object_labelpos(x,y, rlong, label_length)
            elif object.type == deepsky.STARS:
                labelpos_list = self.asterism_labelpos(x,y,rlong,label_length)
            else:
                labelpos_list = self.unknown_object_labelpos(x,y,rlong,label_length)
                pass

            pot = 1e+30
            for labelpos_index in range(len(labelpos_list)):
                [[x1,y1],[x2,y2],[x3,y3]] = labelpos_list[labelpos_index]
                pot1 = label_potential.compute_potential(x2,y2)
                #label_potential.compute_potential(x1,y1),
                #label_potential.compute_potential(x3,y3)])
                if pot1 < pot:
                    pot = pot1
                    labelpos = labelpos_index
                    pass
                pass

            [xx,yy] = labelpos_list[labelpos][1]
            label_potential.add_position(xx,yy,label_length)

            if object.type == deepsky.G:
                self.galaxy(x,y,rlong,rshort,posangle,label,labelpos)
            elif object.type == deepsky.N:
                self.diffuse_nebula(x,y,2.0*rlong,2.0*rshort,posangle,label,labelpos)
            elif object.type == deepsky.PN:
                self.planetary_nebula(x,y, rlong, label,labelpos)
            elif object.type == deepsky.OC:
                self.open_cluster(x,y,rlong,label,labelpos)
            elif object.type == deepsky.GC:
                self.globular_cluster(x,y,rlong, label,labelpos)
            elif object.type == deepsky.STARS:
                self.asterism(x,y,rlong,label,labelpos)
            elif object.type == deepsky.SNR:
                self.supernova_remnant(x,y,rlong,label,labelpos)
            else:
                self.unknown_object(x,y,rlong,label,labelpos)
                pass

            pass # object in deeplist
        pass


    def draw_extra_objects(self,extra_positions):
        # Draw extra objects
        print 'Drawing extra objects...'
        for object in extra_positions:
            rax,decx,label,labelpos = object
            if angular_distance((rax,decx),self.fieldcentre) < self.fieldradius:
                l,m =  radec_to_lm((rax,decx), self.fieldcentre)
                x,y = -l*self.drawingscale,m*self.drawingscale
                self.unknown_object(x,y,self.min_radius,label,labelpos)
                pass
            pass # for...
        pass



    def draw_stars(self, star_catalog):
        # Select and draw stars
        print 'Drawing stars...'
        selection = star_catalog.select_stars(self.fieldcentre,
                                              self.fieldradius,
                                              self.lm_stars)
        print str(selection.shape[0])+' stars in map.'
        print 'Faintest star: '+str(int(max(selection[:,2])*100.0+0.5)/100.0)

        l, m = radec_to_lm((selection[:,0], selection[:,1]), self.fieldcentre)
        x, y = -l, m

        mag       = selection[:,2]
        indices   = argsort(mag)
        magsorted = mag[indices]
        xsorted   = x[indices]*self.drawingscale
        ysorted   = y[indices]*self.drawingscale

        rsorted = self.magnitude_to_radius(magsorted)
        self.graphics.set_linewidth(self.star_border_linewidth)
        self.graphics.set_pen_gray(1.0)
        self.graphics.set_fill_gray(0.0)
        for i in range(len(xsorted)):
            if magsorted[i] <= 13.8:
                self.star(xsorted[i], ysorted[i], rsorted[i])
                pass
            pass
        self.graphics.set_pen_gray(0.0)
        pass


    def make_map(self, star_catalog=None, deepsky_catalog=None,
                 extra_positions=[]):
        self.graphics.new()
        self.graphics.set_pen_gray(0.0)
        self.graphics.set_fill_gray(0.0)
        self.graphics.set_font(fontsize=2.6)
        self.graphics.set_linewidth(0.15)

        if deepsky_catalog != None:
            self.draw_deepsky_objects(deepsky_catalog)
            pass
        if extra_positions != []:
            self.draw_extra_objects(extra_positions)
            pass
        if star_catalog != None:
            self.draw_stars(star_catalog)
            pass
        print 'Drawing legend'
        self.draw_legend()
        self.graphics.finish()
        pass



    def star(self, x, y, radius):
        """
        Filled circle with boundary. Set fill colour and boundary
        colour in advance using set_pen_gray and set_fill_gray
        """
        xx = int(x*100.0+0.5)/100.0
        yy = int(y*100.0+0.5)/100.0
        r = int((radius+self.graphics.gi_linewidth/2.0)*100.0+0.5)/100.0
        self.graphics.circle(xx,yy,r,'PF')
        pass



    def open_cluster(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        self.graphics.save()

        self.graphics.set_linewidth(0.3)
        self.graphics.set_dashed_line(0.6,0.4)
        self.graphics.circle(x,y,r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()
        pass



    def asterism(self,x,y,radius=-1, label='', labelpos=-1):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        w2=2**0.5
        d = r/2.0*w2

        self.graphics.save()

        self.graphics.set_linewidth(0.3)
        self.graphics.set_dashed_line(0.6,0.4)
        diff = self.graphics.gi_linewidth/2.0/w2

        self.graphics.line(x-diff, y+d+diff, x+d+diff,y-diff)
        self.graphics.line(x+d, y, x,y-d)
        self.graphics.line(x+diff, y-d-diff, x-d-diff,y+diff)
        self.graphics.line(x-d, y, x,y+d)

        fh =  self.graphics.gi_fontsize
        if label != '':
            if labelpos == 0 or labelpos == -1:
                self.graphics.text_centred(x, y-d-2*fh/3.0, label,begin=True, end=True)
            elif labelpos == 1:
                self.graphics.text_centred(x, y+d+fh/3.0, label,begin=True, end=True)
            elif labelpos == 2:
                self.graphics.text_left(x-d-fh/6.0, y-fh/3.0, label,begin=True, end=True)
            elif labelpos == 3:
                self.graphics.text_right(x+d+fh/6.0, y-fh/3.0, label, begin=True, end=True)
            pass
        self.graphics.restore()
        pass


    def asterism_labelpos(self,x,y,radius=-1,label_length=0.0):
        """
        x,y,radius, label_length in mm
        returns [[start, centre, end],()]
        """
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        w2=2**0.5
        d = r/2.0*w2
        fh =  self.graphics.gi_fontsize
        label_pos_list = []
        yy = y-d-2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        yy = y+d+2*fh/3.0
        label_pos_list.append([[x-label_length/2.0,yy],[x,yy],[x+label_length,yy]])
        xx = x-d-fh/6.0
        yy = y
        label_pos_list.append([[xx-label_length,yy],[xx-label_length/2.0,yy],[xx,yy]])
        xx = x+d+fh/6.0
        yy = y
        label_pos_list.append([[xx,yy],[xx+label_length/2.0,yy],[xx+label_length,yy]])
        return label_pos_list







    def galaxy(self, x, y, rlong=-1, rshort=-1, posangle=0.0, label='', labelpos=-1):
        """
        If rlong != -1 and rshort == -1 =>   rshort <- rlong
        if rlong < 0.0 => standard galaxy
        labelpos can be 0,1,2,3
        """
        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
            pass
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0
            pass

        self.graphics.save()

        self.graphics.set_linewidth(0.2)
        p = posangle
        if posangle >= 0.5*pi:
            p += pi
            pass
        if posangle < -0.5*pi:
            p -= pi
            pass

        fh = self.graphics.gi_fontsize
        self.graphics.ellipse(x,y,rl, rs, p)
        if label != '':
            self.graphics.save()
            self.graphics.translate(x,y)
            self.graphics.rotate(p)
            if labelpos == 0 or labelpos == -1:
                self.graphics.text_centred(0, -rshort-0.5*fh, label,begin=True, end=True)
            elif labelpos == 1:
                self.graphics.text_centred(0, +rshort+0.5*fh, label,begin=True, end=True)
            elif labelpos == 2:
                self.graphics.text_right(rlong+fh/6.0, -fh/3.0, label,begin=True, end=True)
            elif labelpos == 3:
                self.graphics.text_left(-rlong-fh/6.0, -fh/3.0, label,begin=True, end=True)
                pass
            self.graphics.restore()
            pass
        self.graphics.restore()
        pass



    def galaxy_labelpos(self,x,y,rlong=-1,rshort=-1,posangle=0.0,label_length=0.0):

        rl = rlong
        rs = rshort
        if rlong <= 0.0:
            rl = self.drawingwidth/40.0
            rs = rl/2.0
            pass
        if rlong > 0.0 and rshort < 0.0:
            rl = rlong
            rs = rlong/2.0
            pass

        p = posangle
        if posangle >= 0.5*pi:
            p += pi
            pass
        if posangle < -0.5*pi:
            p -= pi
            pass

        fh = self.graphics.gi_fontsize
        label_pos_list = []

        sp = sin(p)
        cp = cos(p)

        hl = label_length/2.0

        d = -rshort-0.5*fh
        xc = x + d*sp
        yc = y - d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xc = x - d*sp
        yc = y + d*cp
        xs = xc -hl*cp
        ys = yc -hl*sp
        xe = xc +hl*cp
        ye = yc +hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        d  = rlong+fh/6.0
        xs = x + d*cp
        ys = y + d*sp
        xc = xs + hl*cp
        yc = ys + hl*sp
        xe = xc + hl*cp
        ye = yc + hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])

        xe = x - d*cp
        ye = y - d*sp
        xc = xe - hl*cp
        yc = ye - hl*sp
        xs = xc - hl*cp
        ys = yc - hl*sp
        label_pos_list.append([[xs,ys],[xc,yc],[xe,ye]])



        return label_pos_list



    def draw_circular_object_label(self,x,y,r,label='',labelpos=-1):
        fh = self.graphics.gi_fontsize
        if label != '':
            arg = 1.0-2*fh/(3.0*r)
            if arg < 1.0 and arg > -1.0:
                a = arccos(arg)
            else:
                a = 0.5*pi
                pass
            if labelpos == 0 or labelpos == -1:
                self.graphics.text_right(x+sin(a)*r+fh/6.0, y-r, label,begin=True, end=True)
            elif labelpos == 1:
                self.graphics.text_left(x-sin(a)*r-fh/6.0, y-r, label,begin=True, end=True)
            elif labelpos == 2:
                self.graphics.text_right(x+sin(a)*r+fh/6.0, y+r-2*fh/3.0, label,begin=True, end=True)
            elif labelpos == 3:
                self.graphics.text_left(x-sin(a)*r-fh/6.0, y+r-2*fh/3.0, label,begin=True, end=True)
                pass
            pass
        pass


    def circular_object_labelpos(self,x,y,radius=-1.0,label_length=0.0):
        fh = self.graphics.gi_fontsize
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        arg = 1.0-2*fh/(3.0*r)
        if arg < 1.0 and arg > -1.0:
            a = arccos(arg)
        else:
            a = 0.5*pi
            pass


        label_pos_list = []
        xs = x+sin(a)*r+fh/6.0
        ys = y-r+fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        xs = x-sin(a)*r-fh/6.0 - label_length
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x+sin(a)*r+fh/6.0
        ys = y+r-fh/3.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list



    def globular_cluster(self, x,y,radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        self.graphics.save()

        self.graphics.set_linewidth(0.2)
        self.graphics.circle(x,y,r)
        self.graphics.line(x-r, y, x+r, y)
        self.graphics.line(x, y-r, x, y+r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()
        pass



    def diffuse_nebula(self, x, y, width=-1.0, height=-1.0, posangle=0.0, label='',labelpos=''):
        self.graphics.save()

        self.graphics.set_linewidth(0.2)
        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
            pass
        d1 = d+self.graphics.gi_linewidth/2.0
        self.graphics.line(x-d1, y+d, x+d1, y+d)
        self.graphics.line(x+d, y+d, x+d, y-d)
        self.graphics.line(x+d1, y-d, x-d1, y-d)
        self.graphics.line(x-d, y-d, x-d, y+d)
        fh = self.graphics.gi_fontsize
        if label != '':
            if labelpos == 0 or labelpos == -1:
                self.graphics.text_centred(x, y-d-fh/2.0, label,
                                           begin=True, end=True)
            elif labelpos == 1:
                self.graphics.text_centred(x, y+d+fh/2.0, label,
                                           begin=True, end=True)
            elif labelpos == 2:
                self.graphics.text_left(x-d-fh/6.0, y-fh/3.0, label,
                                        begin=True, end=True)
            elif labelpos == 3:
                self.graphics.text_right(x+d+fh/6.0, y-fh/3.0, label,
                                         begin=True, end=True)
            pass
        self.graphics.restore()
        pass



    def diffuse_nebula_labelpos(self,x,y,width=-1.0,height=-1.0, posangle=0.0,label_length=0.0):

        d = 0.5*width
        if width < 0.0:
            d = self.drawingwidth/40.0
            pass
        fh = self.graphics.gi_fontsize

        label_pos_list = []
        xs = x - label_length/2.0
        ys = y-d-fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        ys = y+d+fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - d - fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x + d + fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list




    def planetary_nebula(self, x, y, radius=-1.0, label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/60.0
            pass
        self.graphics.save()

        self.graphics.set_linewidth(0.2)
        self.graphics.circle(x,y,0.75*r)
        self.graphics.line(x-0.75*r, y, x-1.5*r, y)
        self.graphics.line(x+0.75*r, y, x+1.5*r, y)
        self.graphics.line(x, y+0.75*r, x, y+1.5*r)
        self.graphics.line(x, y-0.75*r, x, y-1.5*r)

        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()
        pass



    def supernova_remnant(self,x,y,radius=-1.0,label='', labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        self.graphics.save()

        self.graphics.set_linewidth(0.5)
        self.graphics.circle(x,y,r-self.graphics.gi_linewidth/2.0)
        #self.graphics.circle(x,y,r*0.85)
        #self.graphics.circle(x,y,r*0.7)
        self.draw_circular_object_label(x,y,r,label,labelpos)

        self.graphics.restore()
        pass

    def unknown_object(self,x,y,radius=-1.0,label='',labelpos=''):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass

        r/=2**0.5
        self.graphics.save()

        self.graphics.set_linewidth(0.2)
        self.graphics.line(x-r, y+r, x+r, y-r)
        self.graphics.line(x+r, y+r, x-r, y-r)
        fh = self.graphics.gi_fontsize
        if label != '':
            if labelpos == 0:
                self.graphics.text_right(x+r+fh/6.0, y-fh/3.0, label,begin=True, end=True)
            elif labelpos ==1:
                self.graphics.text_left(x-r-fh/6.0, y-fh/3.0, label,begin=True, end=True)
            elif labelpos == 2:
                self.graphics.text_centred(x, y+ r + fh/2.0, label,begin=True, end=True)
            else:
                self.graphics.text_centred(x, y - r - fh/2.0, label,begin=True, end=True)
                pass
            pass
        self.graphics.restore()
        pass



    def unknown_object_labelpos(self,x,y,radius=-1,label_length=0.0):
        r = radius
        if radius <= 0.0:
            r = self.drawingwidth/40.0
            pass
        fh = self.graphics.gi_fontsize
        r/=2**0.5
        label_pos_list = []
        xs = x + r +fh/6.0
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x - r -fh/6.0 - label_length
        ys = y
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y + r +fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])

        xs = x -label_length/2.0
        ys = y - r -fh/2.0
        label_pos_list.append([[xs,ys],[xs+label_length/2.0,ys],[xs+label_length,ys]])
        return label_pos_list


    pass # class SkymapEngine



if __name__ == '__main__':
    import eps
    import pdf
    import star_catalog as sc
    from  fonts import FontMetrics

    stars = sc.StarCatalog('data/tyc2.bin')
    fm = FontMetrics('font-metrics')

    width = 200
    EPS = pdf.PDFDrawing('radec00.pdf',width, width, fm)

    sm = SkymapEngine(EPS)
    sm.set_caption('Probeersel')
    sm.set_field(1.5,1, 0.05)
    sm.make_map(stars)
    EPS.close()

    pass

__all__ = ['EN', 'NL', 'SkymapEngine']
