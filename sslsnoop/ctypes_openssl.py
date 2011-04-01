#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2011 Loic Jaquemet loic.jaquemet+python@gmail.com
#

__author__ = "Loic Jaquemet loic.jaquemet+python@gmail.com"

import ctypes
import logging

''' insure ctypes basic types are subverted '''
from haystack import model

from haystack.model import is_valid_address,is_valid_address_value,getaddress,array2bytes,bytes2array
from haystack.model import LoadableMembers,RangeValue,NotNull,CString,EVP_CIPHER_CTX_APP_DATA_PTR

import ctypes_openssl_generated as gen

log=logging.getLogger('openssl.model')

''' hmac.h:69 '''
HMAC_MAX_MD_CBLOCK=128
''' evp.h:91 '''
EVP_MAX_BLOCK_LENGTH=32
EVP_MAX_IV_LENGTH=16
AES_MAXNR=14 # aes.h:66
RIJNDAEL_MAXNR=14


# ============== Internal type defs ==============


class OpenSSLStruct(LoadableMembers):
  ''' defines classRef '''
  pass

BN_ULONG = ctypes.c_ulong

# evp/e_aes.c:66
class EVP_AES_KEY(OpenSSLStruct):
  _fields_ = [
  ('ks', gen.AES_KEY),
	]
  def fromPyObj(self,pyobj):
    self.ks = gen.AES_KEY().fromPyObj(pyobj.ks)
    return self

class EVP_RC4_KEY(OpenSSLStruct): # evp/e_rca.c
  _fields_ = [
  ('ks', gen.RC4_KEY)
  ]




################ START copy generated classes ##########################


import inspect,sys

def copyGeneratedClasses(src, dst, register):
  ''' 
  @param me : dst module
  @param src : src module, generated
  '''
  __root_module_name,__dot,__module_name = dst.__name__.rpartition('.')
  _loaded=0
  _registered=0
  for (name, klass) in inspect.getmembers(src, inspect.isclass):
    if type(klass) == type(ctypes.Structure):
      if klass.__module__.endswith('%s_generated'%(__module_name) ) :
        setattr(dst, name, klass)
        _loaded+=1
    else:
      #log.debug("%s - %s"%(name, klass))
      pass
  log.debug('loaded %d C structs from %s structs'%( _loaded, src.__name__))
  log.debug('registered %d Pointers types'%( _registered))
  log.debug('There is %d members in %s'%(len(src.__dict__), src.__name__))
  return 


copyGeneratedClasses(gen, sys.modules[__name__], OpenSSLStruct )

model.registerModule(sys.modules[__name__])

log.warning('OpenSSLStruct.classRef %d'%len(OpenSSLStruct.classRef) )
log.warning('LoadableMembers.classRef %d'%len(LoadableMembers.classRef) )
log.warning('ctypes.Structure.classRef %d'%len(ctypes.Structure.classRef) )
log.warning('AES_KEY.classRef %d'%len(AES_KEY.classRef) )

log.warning('ctypes.Structure is %s'%ctypes.Structure )

model.createPOPOClasses( sys.modules[__name__] )

#print 'DONE'

################ END   copy generated classes ##########################




############# Start expectedValues and methos override #################



''' aes.h:78 '''
####### AES_KEY #######
def AES_KEY_getKey(self):
  #return array2bytes(self.rd_key)
  return ','.join(["0x%lx"%key for key in self.rd_key])
def AES_KEY_getRounds(self):
  return self.rounds
def AES_KEY_fromPyObj(self,pyobj):
  #copy rd_key
  self.rd_key=bytes2array(pyobj.rd_key,ctypes.c_ulong)
  #copy rounds
  self.rounds=pyobj.rounds
  return self
AES_KEY.getKey = AES_KEY_getKey
AES_KEY.getRounds = AES_KEY_getRounds
AES_KEY.fromPyObj = AES_KEY_fromPyObj
#######


# BIGNUM
BIGNUM.expectedValues={
    "neg": [0,1]
  }
def BIGNUM_loadMembers(self, mappings, maxDepth):
  ''' 
  #self._d = process.readArray(attr_obj_address, ctypes.c_ulong, self.top) 
  ## or    
  #ulong_array= (ctypes.c_ulong * self.top)    
  '''
  if not self.isValid(mappings):
    log.debug('BigNUm tries to load members when its not validated')
    return False
  # Load and memcopy d / BN_ULONG *
  attr_obj_address=getaddress(self.d)
  if not bool(self.d):
    log.debug('BIGNUM has a Null pointer d')
    return True
  memoryMap = is_valid_address_value( attr_obj_address, mappings)
  contents=(BN_ULONG*self.top).from_buffer_copy(memoryMap.readArray(attr_obj_address, BN_ULONG, self.top))
  log.debug('contents acquired %d'%ctypes.sizeof(contents))
  self.d.contents=BN_ULONG.from_address(ctypes.addressof(contents))
  self.d=ctypes.cast(contents, ctypes.POINTER(BN_ULONG) ) 
  return True

def BIGNUM_isValid(self,mappings):
  if ( self.dmax < 0 or self.top < 0 or self.dmax < self.top ):
    return False
  return LoadableMembers.isValid(self,mappings)

def BIGNUM___str__(self):
  d= getaddress(self.d)
  return ("BN { d=0x%lx, top=%d, dmax=%d, neg=%d, flags=%d }"%
              (d, self.top, self.dmax, self.neg, self.flags) )

BIGNUM.loadMembers = BIGNUM_loadMembers
BIGNUM.isValid     = BIGNUM_isValid
BIGNUM.__str__     = BIGNUM___str__
#################


# CRYPTO_EX_DATA crypto.h:158:
def CRYPTO_EX_DATA_loadMembers(self, mappings, maxDepth):
  ''' erase self.sk'''
  #self.sk=ctypes.POINTER(STACK)()
  return LoadableMembers.loadMembers(self, mappings, maxDepth)
def CRYPTO_EX_DATA_isValid(self,mappings):
  ''' erase self.sk'''
  # TODO why ?
  #self.sk=ctypes.POINTER(STACK)()
  return LoadableMembers.isValid(self,mappings)

CRYPTO_EX_DATA.loadMembers = CRYPTO_EX_DATA_loadMembers 
CRYPTO_EX_DATA.isValid     = CRYPTO_EX_DATA_isValid 
#################


######## RSA key
RSA.expectedValues={
    "pad": [0], 
    "version": [0], 
    "references": RangeValue(0,0xfff),
    "n": [NotNull],
    "e": [NotNull],
    "d": [NotNull],
    "p": [NotNull],
    "q": [NotNull],
    "dmp1": [NotNull],
    "dmq1": [NotNull],
    "iqmp": [NotNull]
  }
def RSA_printValid(self,mappings):
  log.debug( '----------------------- LOADED: %s'%self.loaded)
  log.debug('pad: %d version %d ref %d'%(self.pad,self.version,self.references) )
  log.debug(is_valid_address( self.n, mappings)    )
  log.debug(is_valid_address( self.e, mappings)    )
  log.debug(is_valid_address( self.d, mappings)    )
  log.debug(is_valid_address( self.p, mappings)    )
  log.debug(is_valid_address( self.q, mappings)    )
  log.debug(is_valid_address( self.dmp1, mappings) ) 
  log.debug(is_valid_address( self.dmq1, mappings) )
  log.debug(is_valid_address( self.iqmp, mappings) )
  return
def RSA_loadMembers(self, mappings, maxDepth):
  #self.meth = 0 # from_address(0)
  # ignore bignum_data.
  #self.bignum_data = 0
  self.bignum_data.ptr.value = 0
  #self.blinding = 0
  #self.mt_blinding = 0

  if not LoadableMembers.loadMembers(self, mappings, maxDepth):
    log.debug('RSA not loaded')
    return False
  return True

RSA.printValid  = RSA_printValid
RSA.loadMembers = RSA_loadMembers



########## DSA Key
DSA.expectedValues={
    "pad": [0], 
    "version": [0], 
    "references": RangeValue(0,0xfff),
    "p": [NotNull],
    "q": [NotNull],
    "g": [NotNull],
    "pub_key": [NotNull],
    "priv_key": [NotNull]
  }
def DSA_printValid(self,mappings):
  log.debug( '----------------------- \npad: %d version %d ref %d'%(self.pad,self.version,self.write_params) )
  log.debug(is_valid_address( self.p, mappings)    )
  log.debug(is_valid_address( self.q, mappings)    )
  log.debug(is_valid_address( self.g, mappings)    )
  log.debug(is_valid_address( self.pub_key, mappings)    )
  log.debug(is_valid_address( self.priv_key, mappings)    )
  return
def DSA_loadMembers(self, mappings, maxDepth):
  # clean other structs
  # r and kinv can be null
  self.meth = None
  self._method_mod_p = None
  #self.engine = None
  
  if not LoadableMembers.loadMembers(self, mappings, maxDepth):
    log.debug('DSA not loaded')
    return False

  return True

DSA.printValid  = DSA_printValid
DSA.loadMembers = DSA_loadMembers

######### EP_CIPHER
EVP_CIPHER.expectedValues={
    "key_len": RangeValue(1,0xff), # key_len *8 bits ..2040 bits for a key is enought ? 
                                   # Default value for variable length ciphers 
    "iv_len": RangeValue(1,0xff), #  
    "init": [NotNull], 
    "do_cipher": [NotNull], 
    #"cleanup": [NotNull], # aes-cbc ?
    "ctx_size": RangeValue(0,0xffff), #  app_data struct should not be too big
  }


########### EVP_CIPHER_CTX
EVP_CIPHER_CTX.expectedValues={
    "cipher": [NotNull], 
    "encrypt": [0,1], 
    "buf_len": RangeValue(0,EVP_MAX_BLOCK_LENGTH), ## number we have left, so must be less than buffer_size
    #"engine": , # can be null
    #"app_data": , # can be null if cipher_data is not
    #"cipher_data": , # can be null if app_data is not
    "key_len": RangeValue(1,0xff), # key_len *8 bits ..2040 bits for a key is enought ? 
  }
  
def EVP_CIPHER_CTX_getOIV(self):
  return array2bytes(self.oiv)
def EVP_CIPHER_CTX_getIV(self):
  return array2bytes(self.iv)

EVP_CIPHER_CTX.getOIV = EVP_CIPHER_CTX_getOIV
EVP_CIPHER_CTX.getIV  = EVP_CIPHER_CTX_getIV

##########


# checkks
'''
src=sys.modules[__name__]
for (name, klass) in inspect.getmembers(src, inspect.isclass):
  if klass.__module__ == src.__name__ or klass.__module__.endswith('%s_generated'%(src.__name__) ) :
    if not klass.__name__.endswith('_py'):
      print klass, len(klass.classRef)
'''

def printSizeof(mini=-1):
  for (name,klass) in inspect.getmembers(sys.modules[__name__], inspect.isclass):
    if type(klass) == type(ctypes.Structure) and klass.__module__.endswith('%s_generated'%(__name__) ) :
      if ctypes.sizeof(klass) > mini:
        print '%s:'%name,ctypes.sizeof(klass)
  #print 'SSLCipherSuiteInfo:',ctypes.sizeof(SSLCipherSuiteInfo)
  #print 'SSLChannelInfo:',ctypes.sizeof(SSLChannelInfo)


if __name__ == '__main__':
  printSizeof()

