
import xml.etree.ElementTree as ET


from sw_core_utils import gnc_path_find_localized_html_file

#class HtmlJqplotUtils(object):

if True:

    # we need to force the terminating </script> otherwise we get no displayed plot

    def html_js_include (file):
        jstr = "file://" + gnc_path_find_localized_html_file(file)
        jelm = ET.Element('script', attrib={'language' : "javascript", 'type' : "text/javascript", 'src' : jstr})
        jelm.text  = "\n"
        jelm.tail  = "\n"
        return jelm
    
    def html_css_include (file):
        cssstr = "file://" + gnc_path_find_localized_html_file(file)
        csselm = ET.Element('link', attrib={'rel' : "stylesheet", 'type' : "text/css", 'href' : cssstr})
        csselm.text  = "\n"
        csselm.tail  = "\n"
        return csselm

    def html_jqplot_escape_string (s1):
        #;; Escape single and double quotes and backslashes
        #(set! s1 (regexp-substitute/global #f "\\\\" s1 'pre "\\\\" 'post))
        #(set! s1 (regexp-substitute/global #f "'" s1 'pre "\\'" 'post))
        #(set! s1 (regexp-substitute/global #f "\"" s1 'pre "\\\"" 'post))
        #;; Escape HTML special characters
        #(set! s1 (regexp-substitute/global #f "&" s1 'pre "&amp;" 'post))
        #(set! s1 (regexp-substitute/global #f "<" s1 'pre "&lt;" 'post))
        #(regexp-substitute/global #f ">" s1 'pre "&gt;" 'post))
        pass

