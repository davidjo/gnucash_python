
import random

import pdb
import traceback


import gnc_jqplot

from gnc_html_document import HtmlDoc
from gnc_html_document import HtmlDocument



class HtmlScatter(HtmlDocument):

    def __init__ (self,width=None,height=None,title=None,subtitle=None,x_axis_label=None,y_axis_label=None,data=None,
                   marker=None,marker_color=None):
        super(HtmlScatter,self).__init__()
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

           self.doc.push(gnc_jqplot.html_js_include("jqplot/jquery.min.js"))
           self.doc.push(gnc_jqplot.html_js_include("jqplot/jquery.jqplot.js"))
           self.doc.push(gnc_jqplot.html_css_include("jqplot/jquery.jqplot.css"))

           self.doc.push('<div id="'+chart_id+'" style="width:')
           self.doc.push(str(self.width))
           self.doc.push("px;height:")
           self.doc.push(str(self.height))
           self.doc.push('px;"></div>\n')
           self.doc.push('<script id="source">\n$(function () {')

           self.doc.push("var data = [];")
           self.doc.push("var series = [];\n")

           for x_data,y_data in self.data:
              self.doc.push("  data.push([")
              self.doc.push(str(x_data))
              self.doc.push(", ")
              self.doc.push(str(y_data))
              self.doc.push("]);\n")

           self.doc.push("var series = [];\n")
           self.doc.push("""var options = {
                    legend: { show: false, },
                    seriesDefaults: {
                        markerOptions: {
                            style: '""")
           self.doc.push(marker)
           self.doc.push("""',
                            color: '""")
           self.doc.push(markercolor)
           self.doc.push("""', },
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
               self.doc.push('  options.title = "')
               self.doc.push(title)
               self.doc.push('";\n')

           if subtitle:
               self.doc.push('  options.title += " (')
               self.doc.push(subtitle)
               self.doc.push(')";\n')

           if x_label:
               self.doc.push('  options.axes.xaxis.label = "')
               self.doc.push(x_label)
               self.doc.push('";\n')

           if y_label:
               self.doc.push('  options.axes.yaxis.label = "')
               self.doc.push(y_label)
               self.doc.push('";\n')

           self.doc.push("$.jqplot.config.enablePlugins = true;\n")
           self.doc.push("var plot = $.jqplot('"+chart_id+"', [data], options);\n")
           self.doc.push("});\n</script>\n")

        else:

           #(gnc:warn "Scatter chart has no non-zero data")
           pass

