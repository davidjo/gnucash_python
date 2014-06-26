
import random

import xml.etree.ElementTree as ET


import pdb
import traceback


import gnc_jqplot

from gnc_html_document import HtmlDoc
from gnc_html_document import HtmlDocument


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

        #pdb.set_trace()

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
           pass

