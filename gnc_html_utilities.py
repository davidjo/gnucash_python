

import pdb


# defined in html-utilities.scm


import gnc_html_ctypes

import sw_engine

import engine_ctypes

#import gnucash


def register_guid (type_text, guid):
   return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_REGISTER,type_text+guid,"")

def account_anchor_text (acct):
   return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_REGISTER,"acct-guid="+acct.GetGUID().to_string(),"")

def split_anchor_text (split):
   return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_REGISTER,"split-guid="+split.GetGUID().to_string(),"")

def transaction_anchor_text (trans):
   return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_REGISTER,"trans-guid="+trans.GetGUID().to_string(),"")

def report_anchor_text (report_id):
   return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_REPORT,"id="+report_id,"")

def price_anchor_text (price):
   # annoyingly gnc_price_get_guid is a macro to qof_entity_get_guid (or qof_instance_get_guid)
   # dont want to pollute gnucash_ext with ctypes
   # so do the call here
   # this is annoying - SWIG is giving me issues with GncPrice * versus GncPrice const *
   # punting and using a ctypes wrap for the moment
   #pdb.set_trace()
   guid_inst = sw_engine.gncPriceGetGUID(price.instance)
   #guid = gnucash.GUID(instance=guid_inst)
   guidstr = engine_ctypes.guid_inst_to_string(guid_inst)
   #return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_PRICE,"price-guid="+price.GetGUID(),"")
   return gnc_html_ctypes.build_url(gnc_html_ctypes.URLTypes.URL_TYPE_PRICE,"price-guid="+guidstr,"")

