#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
    This program is free software; you can redistribute it and/or modify
    it under the terms of the Revised BSD License.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    Revised BSD License for more details.

    Copyright 2015-2024 Game Maker 2k - https://github.com/GameMaker2k
    Copyright 2015-2024 Kazuki Przyborowski - https://github.com/KazukiPrzyborowski

    $FileInfo: pywwwget.py - Last Update: 8/14/2025 Ver. 2.1.6 RC 1 - Author: cooldude2k $
'''

from __future__ import absolute_import, division, print_function, unicode_literals, generators, with_statement, nested_scopes
import os
import socket
import shutil
import logging
import platform

# FTP Support
ftpssl = True
try:
    from ftplib import FTP, FTP_TLS
except ImportError:
    ftpssl = False
    from ftplib import FTP

try:
    basestring
except NameError:
    basestring = str

# URL Parsing
try:
    from urllib.parse import urlparse, urlunparse
except ImportError:
    from urlparse import urlparse, urlunparse

# Paramiko support
haveparamiko = False
try:
    import paramiko
    haveparamiko = True
except ImportError:
    pass

# PySFTP support
havepysftp = False
try:
    import pysftp
    havepysftp = True
except ImportError:
    pass

# Add the mechanize import check
havemechanize = False
try:
    import mechanize
    havemechanize = True
except ImportError:
    pass

# Requests support
haverequests = False
try:
    import requests
    haverequests = True
    import urllib3
    logging.getLogger("urllib3").setLevel(logging.WARNING)
except ImportError:
    pass

# HTTPX support
havehttpx = False
try:
    import httpx
    havehttpx = True
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("httpcore").setLevel(logging.WARNING)
except ImportError:
    pass

# HTTP and URL parsing
try:
    from urllib.request import Request, build_opener, HTTPBasicAuthHandler
    from urllib.parse import urlparse
except ImportError:
    from urllib2 import Request, build_opener, HTTPBasicAuthHandler
    from urlparse import urlparse

# StringIO and BytesIO
try:
    from io import StringIO, BytesIO
except ImportError:
    try:
        from cStringIO import StringIO
        from cStringIO import StringIO as BytesIO
    except ImportError:
        from StringIO import StringIO
        from StringIO import StringIO as BytesIO

__use_pysftp__ = False
if(not havepysftp):
    __use_pysftp__ = False
__use_http_lib__ = "httpx"
if(__use_http_lib__ == "httpx" and haverequests and not havehttpx):
    __use_http_lib__ = "requests"
if(__use_http_lib__ == "requests" and havehttpx and not haverequests):
    __use_http_lib__ = "httpx"
if((__use_http_lib__ == "httpx" or __use_http_lib__ == "requests") and not havehttpx and not haverequests):
    __use_http_lib__ = "urllib"

__program_name__ = "PyWWW-Get"
__program_alt_name__ = "PyWWWGet"
__program_small_name__ = "wwwget"
__project__ = __program_name__
__project_url__ = "https://github.com/GameMaker2k/PyWWW-Get"
__version_info__ = (2, 1, 6, "RC 1", 1)
__version_date_info__ = (2025, 8, 14, "RC 1", 1)
__version_date__ = str(__version_date_info__[0])+"."+str(__version_date_info__[
    1]).zfill(2)+"."+str(__version_date_info__[2]).zfill(2)
__revision__ = __version_info__[3]
__revision_id__ = "$Id: 86ae372b8e407bd8d96881b83c7bbc92e95cf9f5 $"
if(__version_info__[4] is not None):
    __version_date_plusrc__ = __version_date__ + \
        "-"+str(__version_date_info__[4])
if(__version_info__[4] is None):
    __version_date_plusrc__ = __version_date__
if(__version_info__[3] is not None):
    __version__ = str(__version_info__[0])+"."+str(__version_info__[1])+"."+str(
        __version_info__[2])+" "+str(__version_info__[3])
if(__version_info__[3] is None):
    __version__ = str(
        __version_info__[0])+"."+str(__version_info__[1])+"."+str(__version_info__[2])

PyBitness = platform.architecture()
if(PyBitness == "32bit" or PyBitness == "32"):
    PyBitness = "32"
elif(PyBitness == "64bit" or PyBitness == "64"):
    PyBitness = "64"
else:
    PyBitness = "32"

geturls_ua_pywwwget_python = "Mozilla/5.0 (compatible; {proname}/{prover}; +{prourl})".format(
    proname=__project__, prover=__version__, prourl=__project_url__)
if(platform.python_implementation() != ""):
    py_implementation = platform.python_implementation()
if(platform.python_implementation() == ""):
    py_implementation = "Python"
geturls_ua_pywwwget_python_alt = "Mozilla/5.0 ({osver}; {archtype}; +{prourl}) {pyimp}/{pyver} (KHTML, like Gecko) {proname}/{prover}".format(osver=platform.system(
)+" "+platform.release(), archtype=platform.machine(), prourl=__project_url__, pyimp=py_implementation, pyver=platform.python_version(), proname=__project__, prover=__version__)
geturls_ua_googlebot_google = "Mozilla/5.0 (compatible; Googlebot/2.1; +http://www.google.com/bot.html)"
geturls_ua_googlebot_google_old = "Googlebot/2.1 (+http://www.google.com/bot.html)"
geturls_headers_pywwwget_python = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_pywwwget_python, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close",
                                    'SEC-CH-UA': "\""+__project__+"\";v=\""+str(__version__)+"\", \"Not;A=Brand\";v=\"8\", \""+py_implementation+"\";v=\""+str(platform.release())+"\"", 'SEC-CH-UA-FULL-VERSION': str(__version__), 'SEC-CH-UA-PLATFORM': ""+py_implementation+"", 'SEC-CH-UA-ARCH': ""+platform.machine()+"", 'SEC-CH-UA-PLATFORM': str(__version__), 'SEC-CH-UA-BITNESS': str(PyBitness)}
geturls_headers_pywwwget_python_alt = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_pywwwget_python_alt, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6", 'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close",
                                        'SEC-CH-UA': "\""+__project__+"\";v=\""+str(__version__)+"\", \"Not;A=Brand\";v=\"8\", \""+py_implementation+"\";v=\""+str(platform.release())+"\"", 'SEC-CH-UA-FULL-VERSION': str(__version__), 'SEC-CH-UA-PLATFORM': ""+py_implementation+"", 'SEC-CH-UA-ARCH': ""+platform.machine()+"", 'SEC-CH-UA-PLATFORM': str(__version__), 'SEC-CH-UA-BITNESS': str(PyBitness)}
geturls_headers_googlebot_google = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_googlebot_google, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6",
                                    'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"}
geturls_headers_googlebot_google_old = {'Referer': "http://google.com/", 'User-Agent': geturls_ua_googlebot_google_old, 'Accept-Encoding': "none", 'Accept-Language': "en-US,en;q=0.8,en-CA,en-GB;q=0.6",
                                        'Accept-Charset': "ISO-8859-1,ISO-8859-15,utf-8;q=0.7,*;q=0.7", 'Accept': "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", 'Connection': "close"}

def download_file_from_ftp_file(url):
    urlparts = urlparse(url)
    file_name = os.path.basename(urlparts.path)
    file_dir = os.path.dirname(urlparts.path)
    if(urlparts.username is not None):
        ftp_username = urlparts.username
    else:
        ftp_username = "anonymous"
    if(urlparts.password is not None):
        ftp_password = urlparts.password
    elif(urlparts.password is None and urlparts.username == "anonymous"):
        ftp_password = "anonymous"
    else:
        ftp_password = ""
    if(urlparts.scheme == "ftp"):
        ftp = FTP()
    elif(urlparts.scheme == "ftps" and ftpssl):
        ftp = FTP_TLS()
    else:
        return False
    if(urlparts.scheme == "sftp"):
        if(__use_pysftp__):
            return download_file_from_pysftp_file(url)
        else:
            return download_file_from_sftp_file(url)
    elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return download_file_from_http_file(url)
    ftp_port = urlparts.port
    if(urlparts.port is None):
        ftp_port = 21
    try:
        ftp.connect(urlparts.hostname, ftp_port)
    except socket.gaierror:
        log.info("Error With URL "+url)
        return False
    except socket.timeout:
        log.info("Error With URL "+url)
        return False
    ftp.login(urlparts.username, urlparts.password)
    if(urlparts.scheme == "ftps"):
        ftp.prot_p()
    ftpfile = BytesIO()
    ftp.retrbinary("RETR "+urlparts.path, ftpfile.write)
    #ftp.storbinary("STOR "+urlparts.path, ftpfile.write);
    ftp.close()
    ftpfile.seek(0, 0)
    return ftpfile


def download_file_from_ftp_string(url):
    ftpfile = download_file_from_ftp_file(url)
    return ftpfile.read()


def upload_file_to_ftp_file(ftpfile, url):
    urlparts = urlparse(url)
    file_name = os.path.basename(urlparts.path)
    file_dir = os.path.dirname(urlparts.path)
    if(urlparts.username is not None):
        ftp_username = urlparts.username
    else:
        ftp_username = "anonymous"
    if(urlparts.password is not None):
        ftp_password = urlparts.password
    elif(urlparts.password is None and urlparts.username == "anonymous"):
        ftp_password = "anonymous"
    else:
        ftp_password = ""
    if(urlparts.scheme == "ftp"):
        ftp = FTP()
    elif(urlparts.scheme == "ftps" and ftpssl):
        ftp = FTP_TLS()
    else:
        return False
    if(urlparts.scheme == "sftp"):
        if(__use_pysftp__):
            return upload_file_to_pysftp_file(url)
        else:
            return upload_file_to_sftp_file(url)
    elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return False
    ftp_port = urlparts.port
    if(urlparts.port is None):
        ftp_port = 21
    try:
        ftp.connect(urlparts.hostname, ftp_port)
    except socket.gaierror:
        log.info("Error With URL "+url)
        return False
    except socket.timeout:
        log.info("Error With URL "+url)
        return False
    ftp.login(urlparts.username, urlparts.password)
    if(urlparts.scheme == "ftps"):
        ftp.prot_p()
    ftp.storbinary("STOR "+urlparts.path, ftpfile)
    ftp.close()
    ftpfile.seek(0, 0)
    return ftpfile


def upload_file_to_ftp_string(ftpstring, url):
    ftpfileo = BytesIO(ftpstring)
    ftpfile = upload_file_to_ftp_file(ftpfileo, url)
    ftpfileo.close()
    return ftpfile


class RawIteratorWrapper:
    def __init__(self, iterator):
        self.iterator = iterator
        self.buffer = b""
        self._iterator_exhausted = False

    def read(self, size=-1):
        if self._iterator_exhausted:
            return b''
        while size < 0 or len(self.buffer) < size:
            try:
                chunk = next(self.iterator)
                self.buffer += chunk
            except StopIteration:
                self._iterator_exhausted = True
                break
        if size < 0:
            size = len(self.buffer)
        result, self.buffer = self.buffer[:size], self.buffer[size:]
        return result


def download_file_from_http_file(url, headers=None, usehttp=__use_http_lib__):
    if headers is None:
        headers = {}
    urlparts = urlparse(url)
    username = urlparts.username
    password = urlparts.password

    # Rebuild URL without username and password
    netloc = urlparts.hostname or ''
    if urlparts.port:
        netloc += ':' + str(urlparts.port)
    rebuilt_url = urlunparse((urlparts.scheme, netloc, urlparts.path,
                              urlparts.params, urlparts.query, urlparts.fragment))

    # Handle SFTP/FTP
    if urlparts.scheme == "sftp":
        if __use_pysftp__:
            return download_file_from_pysftp_file(url)
        else:
            return download_file_from_sftp_file(url)
    elif urlparts.scheme == "ftp" or urlparts.scheme == "ftps":
        return download_file_from_ftp_file(url)

    # Create a temporary file object
    httpfile = BytesIO()

    # 1) Requests branch
    if usehttp == 'requests' and haverequests:
        if username and password:
            response = requests.get(
                rebuilt_url, headers=headers, auth=(username, password), timeout=(5, 30), stream=True
            )
        else:
            response = requests.get(rebuilt_url, headers=headers, timeout=(5, 30)), stream=True)
        response.raw.decode_content = True
        shutil.copyfileobj(response.raw, httpfile)

    # 2) HTTPX branch
    elif usehttp == 'httpx' and havehttpx:
        with httpx.Client(follow_redirects=True) as client:
            if username and password:
                response = client.get(
                    rebuilt_url, headers=headers, auth=(username, password)
                )
            else:
                response = client.get(rebuilt_url, headers=headers)
            raw_wrapper = RawIteratorWrapper(response.iter_bytes())
            shutil.copyfileobj(raw_wrapper, httpfile)

    # 3) Mechanize branch
    elif usehttp == 'mechanize' and havemechanize:
        # Create a mechanize browser
        br = mechanize.Browser()
        # Optional: configure mechanize (disable robots.txt, handle redirects, etc.)
        br.set_handle_robots(False)
        # If you need custom headers, add them as a list of (header_name, header_value)
        if headers:
            br.addheaders = list(headers.items())

        # If you need to handle basic auth:
        if username and password:
            # Mechanize has its own password manager; this is one way to do it:
            br.add_password(rebuilt_url, username, password)

        # Open the URL and copy the response to httpfile
        response = br.open(rebuilt_url)
        shutil.copyfileobj(response, httpfile)

    # 4) Fallback to urllib
    else:
        request = Request(rebuilt_url, headers=headers)
        if username and password:
            password_mgr = HTTPPasswordMgrWithDefaultRealm()
            password_mgr.add_password(None, rebuilt_url, username, password)
            auth_handler = HTTPBasicAuthHandler(password_mgr)
            opener = build_opener(auth_handler)
        else:
            opener = build_opener()
        response = opener.open(request)
        shutil.copyfileobj(response, httpfile)

    # Reset file pointer to the start before returning
    httpfile.seek(0, 0)
    return httpfile


def download_file_from_http_string(url, headers=geturls_headers_pywwwget_python_alt, usehttp=__use_http_lib__):
    httpfile = download_file_from_http_file(url, headers, usehttp)
    return httpfile.read()


if(haveparamiko):
    def download_file_from_sftp_file(url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return download_file_from_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return download_file_from_http_file(url)
        if(urlparts.scheme != "sftp"):
            return False
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(urlparts.hostname, port=sftp_port,
                        username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftpfile = BytesIO()
        sftp.getfo(urlparts.path, sftpfile)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def download_file_from_sftp_file(url):
        return False

if(haveparamiko):
    def download_file_from_sftp_string(url):
        sftpfile = download_file_from_sftp_file(url)
        return sftpfile.read()
else:
    def download_file_from_sftp_string(url):
        return False

if(haveparamiko):
    def upload_file_to_sftp_file(sftpfile, url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return upload_file_to_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return False
        if(urlparts.scheme != "sftp"):
            return False
        ssh = paramiko.SSHClient()
        ssh.load_system_host_keys()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            ssh.connect(urlparts.hostname, port=sftp_port,
                        username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftp.putfo(sftpfile, urlparts.path)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def upload_file_to_sftp_file(sftpfile, url):
        return False

if(haveparamiko):
    def upload_file_to_sftp_string(sftpstring, url):
        sftpfileo = BytesIO(sftpstring)
        sftpfile = upload_file_to_sftp_files(sftpfileo, url)
        sftpfileo.close()
        return sftpfile
else:
    def upload_file_to_sftp_string(url):
        return False

if(havepysftp):
    def download_file_from_pysftp_file(url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return download_file_from_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return download_file_from_http_file(url)
        if(urlparts.scheme != "sftp"):
            return False
        try:
            pysftp.Connection(urlparts.hostname, port=sftp_port,
                              username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftpfile = BytesIO()
        sftp.getfo(urlparts.path, sftpfile)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def download_file_from_pysftp_file(url):
        return False

if(havepysftp):
    def download_file_from_pysftp_string(url):
        sftpfile = download_file_from_pysftp_file(url)
        return sftpfile.read()
else:
    def download_file_from_pyftp_string(url):
        return False

if(havepysftp):
    def upload_file_to_pysftp_file(sftpfile, url):
        urlparts = urlparse(url)
        file_name = os.path.basename(urlparts.path)
        file_dir = os.path.dirname(urlparts.path)
        sftp_port = urlparts.port
        if(urlparts.port is None):
            sftp_port = 22
        else:
            sftp_port = urlparts.port
        if(urlparts.username is not None):
            sftp_username = urlparts.username
        else:
            sftp_username = "anonymous"
        if(urlparts.password is not None):
            sftp_password = urlparts.password
        elif(urlparts.password is None and urlparts.username == "anonymous"):
            sftp_password = "anonymous"
        else:
            sftp_password = ""
        if(urlparts.scheme == "ftp"):
            return upload_file_to_ftp_file(url)
        elif(urlparts.scheme == "http" or urlparts.scheme == "https"):
            return False
        if(urlparts.scheme != "sftp"):
            return False
        try:
            pysftp.Connection(urlparts.hostname, port=sftp_port,
                              username=urlparts.username, password=urlparts.password)
        except paramiko.ssh_exception.SSHException:
            return False
        except socket.gaierror:
            log.info("Error With URL "+url)
            return False
        except socket.timeout:
            log.info("Error With URL "+url)
            return False
        sftp = ssh.open_sftp()
        sftp.putfo(sftpfile, urlparts.path)
        sftp.close()
        ssh.close()
        sftpfile.seek(0, 0)
        return sftpfile
else:
    def upload_file_to_pysftp_file(sftpfile, url):
        return False

if(havepysftp):
    def upload_file_to_pysftp_string(sftpstring, url):
        sftpfileo = BytesIO(sftpstring)
        sftpfile = upload_file_to_pysftp_file(sftpfileo, url)
        sftpfileo.close()
        return sftpfile
else:
    def upload_file_to_pysftp_string(url):
        return False


def download_file_from_internet_file(url, headers=geturls_headers_pywwwget_python_alt, usehttp=__use_http_lib__):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return download_file_from_http_file(url, headers, usehttp)
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return download_file_from_ftp_file(url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return download_file_from_pysftp_file(url)
        else:
            return download_file_from_sftp_file(url)
    else:
        return False
    return False


def download_file_from_internet_string(url, headers=geturls_headers_pywwwget_python_alt, usehttp=__use_http_lib__):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return download_file_from_http_string(url, headers, usehttp)
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return download_file_from_ftp_string(url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return download_file_from_pysftp_string(url)
        else:
            return download_file_from_sftp_string(url)
    else:
        return False
    return False


def upload_file_to_internet_file(ifp, url):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return False
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return upload_file_to_ftp_file(ifp, url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return upload_file_to_pysftp_file(ifp, url)
        else:
            return upload_file_to_sftp_file(ifp, url)
    else:
        return False
    return False


def upload_file_to_internet_string(ifp, url):
    urlparts = urlparse(url)
    if(urlparts.scheme == "http" or urlparts.scheme == "https"):
        return False
    elif(urlparts.scheme == "ftp" or urlparts.scheme == "ftps"):
        return upload_file_to_ftp_string(ifp, url)
    elif(urlparts.scheme == "sftp"):
        if(__use_pysftp__ and havepysftp):
            return upload_file_to_pysftp_string(ifp, url)
        else:
            return upload_file_to_sftp_string(ifp, url)
    else:
        return False
    return False
