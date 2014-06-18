
from sw_core_utils import gnc_path_find_localized_html_file

#class HtmlJqplotUtils(object):

if True:

    def html_js_include (file):
        jstr = '<script language="javascript" type="text/javascript" src="file://' \
               + gnc_path_find_localized_html_file(file) + '"></script>\n'
        return jstr
    
    def html_css_include (file):
        cssstr = '<link rel="stylesheet" type="text/css" href="file://' \
                  + gnc_path_find_localized_html_file(file) + '" />\n'
        return cssstr

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

