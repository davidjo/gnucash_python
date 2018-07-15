
import random

import xml.etree.ElementTree as ET


import pdb
import traceback


import gnc_jqplot

from gnc_html_document import HtmlDoc
from gnc_html_document import HtmlDocument

# this is a re-coding in python of the scheme version
# in html-scatter.scm


# this is not a subclass of HtmlDocument
# - we need to allow for multiple scatter plots in one HTML document

class HtmlScatter(object):

    def __init__ (self,width=None,height=None,title=None,subtitle=None,x_axis_label=None,y_axis_label=None,data=None,
                   marker=None,marker_color=None):
        self.width = None
        self.height = None
        self.title = None
        self.subtitle = None
        self.x_axis_label = None
        self.y_axis_label = None
        self.data = []
        self.marker = None
        self.markercolor = None

    def add_datapoint (self, newpoint):
        self.data.append(newpoint)

    def render (self):

        pdb.set_trace()

        title = self.title
        subtitle = self.subtitle
        x_label = self.x_axis_label
        y_label = self.y_axis_label
        data = self.data
        marker = self.marker
        markercolor = "#" + self.markercolor
        # Use a unique chart-id for each chart. This prevents chart
        # clashed on multi-column reports
        chart_id = "chart-%d"%random.randint(1,999999)

        if len(self.data) > 0:

           # cant figure the good way of doing this
           # ah - looks like we can nest div elements
           # we probably need to count each scatter plot
           bodydiv = ET.Element('div', attrib={'id' : 'scatter1'})
           bodydiv.text = "\n"

           bodydiv.append(gnc_jqplot.html_js_include("jqplot/jquery.min.js"))
           bodydiv.append(gnc_jqplot.html_js_include("jqplot/jquery.jqplot.js"))
           bodydiv.append(gnc_jqplot.html_css_include("jqplot/jquery.jqplot.css"))

           stylstr = "width:"+str(self.width)+"px;height:"+str(self.height)+"px;"
           divelm = ET.SubElement(bodydiv,'div',attrib={'id' : chart_id, 'style' : stylstr})
           divelm.text = "\n"
           divelm.tail = "\n"
           screlm = ET.Element('script',attrib={'id' : "source"})
           bodydiv.append(screlm)

           txtlst = ["$(function () {\nvar data = [];var series = [];\n"]

           for x_data,y_data in self.data:
              txtlst.append("  data.push([")
              txtlst.append(str(x_data))
              txtlst.append(", ")
              txtlst.append(str(y_data))
              txtlst.append("]);\n")

           txtlst.append("var series = [];\n")
           txtlst.append("""var options = {
                    legend: { show: false, },
                    seriesDefaults: {
                        markerOptions: {
                            style: '""")
           txtlst.append(marker)
           txtlst.append("""',
                            color: '""")
           txtlst.append(markercolor)
           txtlst.append("""', },
                    },
                    series: series,
                    axesDefaults: {
                    },
                    axes: {
                        xaxis: {
                        },
                        yaxis: {
                            autoscale: true,
                        },
                    },
                };\n""")

           if title:
               txtlst.append('  options.title = "')
               txtlst.append(title)
               txtlst.append('";\n')

           if subtitle:
               txtlst.append('  options.title += " (')
               txtlst.append(subtitle)
               txtlst.append(')";\n')

           if x_label:
               txtlst.append('  options.axes.xaxis.label = "')
               txtlst.append(x_label)
               txtlst.append('";\n')

           if y_label:
               txtlst.append('  options.axes.yaxis.label = "')
               txtlst.append(y_label)
               txtlst.append('";\n')

           txtlst.append("$.jqplot.config.enablePlugins = true;\n")
           txtlst.append("var plot = $.jqplot('"+chart_id+"', [data], options);\n")
           txtlst.append("});\n")

           screlm.text = "".join(txtlst)

           stdelm = ET.Element('p')
           bodydiv.append(stdelm)

           return bodydiv

        else:

           #(gnc:warn "Scatter chart has no non-zero data")

           # we need to return a non-null ET document

           #bodydiv = ET.Element('div', attrib={'id' : 'scatter1'})
           #bodydiv.text = "\n"

           #stdelm = ET.Element('p')
           #bodydiv.append(stdelm)

           bodydiv = ET.Element('p')

           return bodydiv


# and a new version which will do multiple lines in a plot

class HtmlMultiScatter(object):

    def __init__ (self,width=None,height=None,title=None,subtitle=None,x_axis_label=None,y_axis_label=None,data=None,
                   marker=None,marker_color=None):
        self.width = None
        self.height = None
        self.title = None
        self.subtitle = None
        self.x_axis_label = None
        self.y_axis_label = None
        self.data = []
        self.marker = []
        self.markercolor = []
        self.labels = []

    # lets not use this - we will prepare the data (a list of lists) and pass it once
    # this only works for a single line
    #def add_datapoint (self, newpoint):
    #    self.data.append(newpoint)

    # what we will do is use an add function to add each lines data block
    def add_data (self, newlist, marker, marker_color, label=None):
        self.data.append(newlist)
        self.marker.append(marker)
        self.markercolor.append(marker_color)
        self.labels.append(label)

    def render (self):

        #pdb.set_trace()

        title = self.title
        subtitle = self.subtitle
        x_label = self.x_axis_label
        y_label = self.y_axis_label
        # Use a unique chart-id for each chart. This prevents chart
        # clashed on multi-column reports
        chart_id = "chart-%d"%random.randint(1,999999)

        if len(self.data) > 0:

           # cant figure the good way of doing this
           # ah - looks like we can nest div elements
           # we probably need to count each scatter plot
           bodydiv = ET.Element('div', attrib={'id' : 'scatter1'})
           bodydiv.text = "\n"

           bodydiv.append(gnc_jqplot.html_js_include("jqplot/jquery.min.js"))
           bodydiv.append(gnc_jqplot.html_js_include("jqplot/jquery.jqplot.js"))
           bodydiv.append(gnc_jqplot.html_css_include("jqplot/jquery.jqplot.css"))

           stylstr = "width:"+str(self.width)+"px;height:"+str(self.height)+"px;"
           divelm = ET.SubElement(bodydiv,'div',attrib={'id' : chart_id, 'style' : stylstr})
           divelm.text = "\n"
           divelm.tail = "\n"
           screlm = ET.Element('script',attrib={'id' : "source"})
           bodydiv.append(screlm)

           txtlst = ["$(function () {\nvar data = [];\n"]

           for idata,data_block in enumerate(self.data):

               txtlst.append("  var data_%d = [];\n"%idata)

               for x_data,y_data in data_block:
                   txtlst.append("    data_%d.push(["%idata)
                   txtlst.append(str(x_data))
                   txtlst.append(", ")
                   txtlst.append(str(y_data))
                   txtlst.append("]);\n")

               txtlst.append("\n  data.push(data_%d);\n\n"%idata)

           txtlst.append("var series = [];")
           txtlst.append("""
                    series = [""")

           for idata,marker in enumerate(self.marker):

               markercolor = "#" + self.markercolor[idata]

               txtlst.append("""
                        {
                        markerOptions: {
                            style: '""")
               txtlst.append(marker)
               txtlst.append("""',
                            color: '""")
               txtlst.append(markercolor)
               txtlst.append("""',
                        },
                        label: '""")
               if self.labels[idata] != None:
                   txtlst.append(self.labels[idata])
               else:
                   txtlst.append("line %d"%(idata+1))
               txtlst.append("""',
                        },""")

           txtlst.append("""
                    ]\n""")

           #txtlst.append("""var options = {
           #         legend: { show: false, },
           #         seriesDefaults: {
           #             markerOptions: {
           #                 style: '""")
           #txtlst.append(marker)
           #txtlst.append("""',
           #                 color: '""")
           #txtlst.append(markercolor)
           #txtlst.append("""', },
           #         },
           txtlst.append("""var options = {
                    legend: {
                        show: true,
                        placement: "outsideGrid",
                    },
                    seriesDefaults: {
                        showMarker: false
                    },
                    series: series,
                    axesDefaults: {
                    },
                    axes: {
                        xaxis: {
                        },
                        yaxis: {
                            autoscale: true,
                        },
                    },
            };\n""")

           if title:
               txtlst.append('  options.title = "')
               txtlst.append(title)
               txtlst.append('";\n')

           if subtitle:
               txtlst.append('  options.title += " (')
               txtlst.append(subtitle)
               txtlst.append(')";\n')

           if x_label:
               txtlst.append('  options.axes.xaxis.label = "')
               txtlst.append(x_label)
               txtlst.append('";\n')

           if y_label:
               txtlst.append('  options.axes.yaxis.label = "')
               txtlst.append(y_label)
               txtlst.append('";\n')

           txtlst.append("$.jqplot.config.enablePlugins = true;\n")
           txtlst.append("var plot = $.jqplot('"+chart_id+"', data, options);\n")
           txtlst.append("});\n")

           screlm.text = "".join(txtlst)

           stdelm = ET.Element('p')
           bodydiv.append(stdelm)

           return bodydiv

        else:

           #(gnc:warn "Scatter chart has no non-zero data")
           pass

