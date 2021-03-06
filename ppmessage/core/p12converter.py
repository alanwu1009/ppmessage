# -*- coding: utf-8 -*-
#
# Copyright (C) 2010-2016 PPMessage.
# Guijin Ding, dingguijin@gmail.com
# All rights reserved
#
# core/p12converter.py
#

from tempfile import mkstemp
from os import unlink, close, write

import time
import base64
import logging
import subprocess

def _randomFileWithData(_data, _suffix):
    _prefix = str(time.time())
    (_handle, _name) = mkstemp(suffix=_suffix, prefix=_prefix)
    write(_handle, _data)
    close(_handle)
    return _name

def _randomFile(_suffix):
    _prefix = str(time.time())
    (_handle, _name) = mkstemp(suffix=_suffix, prefix=_prefix)
    close(_handle)
    return _name

def der2pem(_data, _pass):
    _p12 = _randomFileWithData(_data, ".p12")
    _cert = _randomFile(".pem")
    _key = _randomFile(".pem")
    _key_np = _randomFile(".pem")
    _tp = _pass
    
    _command = "openssl pkcs12 -clcerts -nokeys -out %s -in %s -passin pass:%s" % (_cert, _p12, _tp)
    _command = _command.split(" ")

    _p = subprocess.Popen(_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    _r = _p.wait()
    _s = _p.stdout.read()
    logging.info(_s)
    if "error:" in _s:
        return None

    _command = "openssl pkcs12 -nocerts -out %s -in %s -passin pass:%s -passout pass:%s" % (_key, _p12, _tp, _tp)
    _command = _command.split(" ")

    _p = subprocess.Popen(_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    _r = _p.wait()
    _s = _p.stdout.read()

    logging.info(_s)
    if "error:" in _s:
        return None
    
    _command = "openssl rsa -out %s -in %s -passin pass:%s" % (_key_np, _key, _tp)
    _command = _command.split(" ")

    _p = subprocess.Popen(_command, shell=False, stdout=subprocess.PIPE, stderr=subprocess.STDOUT)
    _r = _p.wait()
    _s = _p.stdout.read()

    logging.info(_s)
    if "error:" in _s or "unable" in _s:
        return None
    
    _d_cert = None
    _d_key = None
    with open(_cert, "rb") as _f:
        _d_cert = _f.read()
    with open(_key_np, "rb") as _f:
        _d_key = _f.read()
    
    unlink(_cert)
    unlink(_key)
    unlink(_key_np)
    
    return _d_key + _d_cert
    
