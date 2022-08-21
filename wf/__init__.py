"""
Run InterProScan on multiple sequences
"""

from latch import small_task, workflow, message
from latch.types import LatchFile, LatchDir
from optparse import OptionParser
from xmltramp2 import xmltramp
from datetime import datetime
from Bio import SeqIO
import requests
import platform
import time
import json
import os

try:
    from urllib.parse import urlparse, urlencode
    from urllib.request import urlopen, Request
    from urllib.error import HTTPError
    from urllib.request import __version__ as urllib_version
except ImportError:
    from urlparse import urlparse
    from urllib import urlencode
    from urllib2 import urlopen, Request, HTTPError
    from urllib2 import __version__ as urllib_version

# allow unicode(str) to be used in python 3
try:
    unicode('')
except NameError:
    unicode = str


@small_task
def interproscan_task(
    email_addr: str, 
    input_file: LatchFile,
) -> LatchDir:
    
    # Base URL for service
    baseUrl = u'https://www.ebi.ac.uk/Tools/services/rest/iprscan5'
    version = u'2021-04-08 10:44'
    pollFreq = 3
    
    # User-agent for request (see RFC2616).
    def getUserAgent():
        urllib_agent = u'Python-urllib/%s' % urllib_version
        clientRevision = version
        try:
            pythonversion = platform.python_version()
            pythonsys = platform.system()
        except ValueError:
            pythonversion, pythonsys = "Unknown", "Unknown"
        user_agent = u'EBI-Sample-Client/%s (%s; Python %s; %s) %s' % (
            clientRevision, os.path.basename(__file__),
            pythonversion, pythonsys, urllib_agent)
        return user_agent

    # Wrapper for a REST (HTTP GET) request
    def restRequest(url):
        try:
            # Set the User-agent.
            user_agent = getUserAgent()
            http_headers = {u'User-Agent': user_agent}
            req = Request(url, None, http_headers)
            # Make the request (HTTP GET).
            reqH = urlopen(req)
            resp = reqH.read()
            contenttype = reqH.info()

            if (len(resp) > 0 and contenttype != u"image/png;charset=UTF-8"
                    and contenttype != u"image/jpeg;charset=UTF-8"
                    and contenttype != u"application/gzip;charset=UTF-8"):
                try:
                    result = unicode(resp, u'utf-8')
                except UnicodeDecodeError:
                    result = resp
            else:
                result = resp
            reqH.close()
        # Errors are indicated by HTTP status codes.
        except HTTPError as ex:
            result = requests.get(url).content
        return result

    # Get input parameters list
    def serviceGetParameters():
        requestUrl = baseUrl + u'/parameters'
        xmlDoc = restRequest(requestUrl)
        doc = xmltramp.parse(xmlDoc)
        return doc[u'id':]

    # Get input parameter information
    def serviceGetParameterDetails(paramName):
        requestUrl = baseUrl + u'/parameterdetails/' + paramName
        xmlDoc = restRequest(requestUrl)
        doc = xmltramp.parse(xmlDoc)
        return doc

    # Submit job
    def serviceRun(email, title, params):
        # Insert e-mail and title into params
        params[u'email'] = email
        if title:
            params[u'title'] = title
        requestUrl = baseUrl + u'/run/'
        # Get the data for the other options
        requestData = urlencode(params)
        # Errors are indicated by HTTP status codes.
        try:
            # Set the HTTP User-agent.
            user_agent = getUserAgent()
            http_headers = {u'User-Agent': user_agent}
            req = Request(requestUrl, None, http_headers)
            # Make the submission (HTTP POST).
            reqH = urlopen(req, requestData.encode(encoding=u'utf_8', errors=u'strict'))
            jobId = unicode(reqH.read(), u'utf-8')
            reqH.close()
        except HTTPError as ex:
            print(xmltramp.parse(unicode(ex.read(), u'utf-8'))[0][0])
            quit()
        return jobId

    # Get job status
    def serviceGetStatus(jobId):
        requestUrl = baseUrl + u'/status/' + jobId
        status = restRequest(requestUrl)
        return status

    # Get available result types for job
    def serviceGetResultTypes(jobId):
        requestUrl = baseUrl + u'/resulttypes/' + jobId
        xmlDoc = restRequest(requestUrl)
        doc = xmltramp.parse(xmlDoc)
        return doc[u'type':]

    # Get result
    def serviceGetResult(jobId, type_):
        requestUrl = baseUrl + u'/result/' + jobId + u'/' + type_
        result = restRequest(requestUrl)
        return result

    # Client-side poll
    def clientPoll(jobId):
        result = u'PENDING'
        while result == u'RUNNING' or result == u'PENDING':
            result = serviceGetStatus(jobId)
            if result == u'RUNNING' or result == u'PENDING':
                time.sleep(pollFreq)

    # Get result for a jobid
    # Allows more than one output file written when 'outformat' is defined.
    def getResult(jobId, outfile, outformat):
        # Check status and wait if necessary
        clientPoll(jobId)
        # Get available result types
        resultTypes = serviceGetResultTypes(jobId)

        for resultType in resultTypes:
            # Derive the filename for the result
            if outfile:
                filename = (outfile + u'.' + unicode(resultType[u'identifier']) +
                            u'.' + unicode(resultType[u'fileSuffix']))
            else:
                filename = (jobId + u'.' + unicode(resultType[u'identifier']) +
                            u'.' + unicode(resultType[u'fileSuffix']))
            # Write a result file

            outformat_parm = str(outformat).split(',')
            for outformat_type in outformat_parm:
                outformat_type = outformat_type.replace(' ', '')

                if outformat_type == 'None':
                    outformat_type = None

                if not outformat_type or outformat_type == unicode(resultType[u'identifier']):
                    # Get the result
                    result = serviceGetResult(jobId, unicode(resultType[u'identifier']))
                    if (unicode(resultType[u'mediaType']) == u"image/png"
                            or unicode(resultType[u'mediaType']) == u"image/jpeg"
                            or unicode(resultType[u'mediaType']) == u"application/gzip"):
                        fmode = 'wb'
                    else:
                        fmode = 'w'

                    try:
                        fh = open(filename, fmode)
                        fh.write(result)
                        fh.close()
                    except TypeError:
                        fh.close()
                        fh = open(filename, "wb")
                        fh.write(result)
                        fh.close()


    # Check if fasta file is valid
    def is_fasta(local_path: str) -> bool:
        with open(local_path, "r") as handle:
            fasta = SeqIO.parse(handle, "fasta")
            return any(fasta)

    # Create batches of 30 sequences
    def batch(iterable, n=1):
        l = len(iterable)
        for ndx in range(0, l, n):
            yield iterable[ndx:min(ndx + n, l)]
    
    # Get timestamp        
    def get_timestamp():
        format_str = "%d %b %Y %H:%M:%S %p"
        result = datetime.now().strftime(format_str)
        return result

    
    # Start main
    assert is_fasta(local_path=input_file.local_path) == True
    CHUNK_SIZE = 30
    job_ids = []
    batch_num = 0
    
    curr_timestamp = "".join([x if x.isalnum() else "_" for x in get_timestamp()])
    out_dir = f"InterPro_{curr_timestamp}"
    os.system(command=f"mkdir -p {out_dir}")

    with open(input_file.local_path, "r") as fh:
        fasta = SeqIO.parse(fh, "fasta")
        batches = batch(list(fasta), CHUNK_SIZE)
        for batch in batches:
            batch_num += 1
            message("info", {"title": f"SUBMITTING JOBS", "body": f"Batch {batch_num}"})
            for record in batch:
                params = {}
                params['sequence'] = str(record.seq.ungap("-"))
                params['goterms'] = False
                params['pathways'] = False
                job_id = serviceRun(email=str(email_addr), title=str(record.description), params=params)
                info = { 'description': record.description, 'job_id': job_id }
                job_ids.append(info)
                message("info", {"title": f"Batch {batch_num} sequence: {record.description}", "body": info})
                
            message("info", {"title": f"GETTING RESULTS", "body": f"Batch {batch_num}"})
            curr_file_count = len(os.listdir(out_dir))
            
            while curr_file_count < len(job_ids):
                selected = job_ids[curr_file_count:]
                for job in selected:
                    jobid = job['job_id']
                    description = job['description']
                    filename = "".join([x if x.isalnum() else "_" for x in description])
                    filepath = f"{out_dir}/{filename}"
                    result_info = {
                        'description': description,
                        'job_id': jobid,
                        'filename': f"{filename}.tsv.tsv"
                    }
                    message("info", {"title": f"Batch {batch_num} result: {description}", "body": result_info})
                    getResult(jobId=jobid, outfile=filepath, outformat="tsv")
                if len(os.listdir(out_dir)) == len(job_ids):
                    break
        
    return LatchDir(path=str(out_dir), remote_path=f"latch:///{out_dir}/")


@workflow
def interproscan(
    email_addr: str, 
    input_file: LatchFile,
) -> LatchDir:
    """Run InterProScan on multiple sequences

    InterProScan
    ----

    Run InterProScan on multiple protein sequences

    __metadata__:
        display_name: InterProScan
        author:
            name: Abdullah Al Nahid
            email:
            github:
        repository:
        license:
            id: MIT

    Args:

        email_addr:
          Your Email Address

          __metadata__:
            display_name: Email

        input_file:
           Input Fasta file of all Protein Sequences

          __metadata__:
            display_name: Input Fasta (All Protein Sequences)
    """
    return interproscan_task(
        email_addr=email_addr, 
        input_file=input_file,
    )
