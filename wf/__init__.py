"""
Run InterProScan on multiple sequences
"""

import subprocess
from pathlib import Path

from latch.types import LatchFile, LatchDir, file_glob
from latch import small_task, workflow
from typing import List
from time import sleep
from Bio import SeqIO
import platform, os, sys, time, re, urllib
from optparse import OptionParser
from xmltramp2 import xmltramp
import urllib.request as urllib2

@small_task
def interproscan_task(
    email_addr: str, 
    input_file: LatchFile,
    output_dir: LatchDir,
    goterms: bool,
    pathways: bool,
) -> LatchFile:

    # # User-agent for request (see RFC2616).
    # def getUserAgent():
    #     # #printDebugMessage('getUserAgent', 'Begin', 11)
    #     # Agent string for urllib2 library.
    #     urllib_agent = 'Python-urllib/%s' % urllib2.__version__
    #     clientRevision = '$Revision: 2106 $'
    #     clientVersion = '0'
    #     if len(clientRevision) > 11:
    #         clientVersion = clientRevision[11:-2]
    #     # Prepend client specific agent string.
    #     user_agent = 'EBI-Sample-Client/%s (%s; Python %s; %s) %s' % (
    #         clientVersion, os.path.basename( __file__ ),
    #         platform.python_version(), platform.system(),
    #         urllib_agent
    #     )
    #     # #printDebugMessage('getUserAgent', 'user_agent: ' + user_agent, 12)
    #     # #printDebugMessage('getUserAgent', 'End', 11)
    #     return user_agent

    # def restRequest(url):
    #     #printDebugMessage('restRequest', 'Begin', 11)
    #     #printDebugMessage('restRequest', 'url: ' + url, 11)
    #     # Errors are indicated by HTTP status codes.
    #     try:
    #         # Set the User-agent.
    #         user_agent = getUserAgent()
    #         http_headers = { 'User-Agent' : user_agent }
    #         req = urllib2.Request(url, None, http_headers)
    #         # Make the request (HTTP GET).
    #         reqH = urllib2.urlopen(req)
    #         resp = reqH.read();
    #         contenttype = reqH.getheader("Content-Type")
                    
    #         if(len(resp)>0 and contenttype!="image/png;charset=UTF-8"
    #             and contenttype!="image/jpeg;charset=UTF-8"
    #             and contenttype!="application/gzip;charset=UTF-8"):
    #             result = str(resp, 'utf-8')
    #         else:
    #             result = resp;
    #         reqH.close()
    #     # Errors are indicated by HTTP status codes.
    #     except urllib2.HTTPError as ex:
    #         # Trap exception and output the document to get error message.
    #         print (ex.read(), file=sys.stderr)
    #         raise
    #     #printDebugMessage('restRequest', 'End', 11)
    #     return result

    # # Get input parameters list
    # def serviceGetParameters():
    #     #printDebugMessage('serviceGetParameters', 'Begin', 1)
    #     requestUrl = baseUrl + '/parameters'
    #     #printDebugMessage('serviceGetParameters', 'requestUrl: ' + requestUrl, 2)
    #     xmlDoc = restRequest(requestUrl)
    #     doc = xmltramp.parse(xmlDoc)
    #     #printDebugMessage('serviceGetParameters', 'End', 1)
    #     return doc['id':]

    # # Print list of parameters
    # def printGetParameters():
    #     #printDebugMessage('printGetParameters', 'Begin', 1)
    #     idList = serviceGetParameters()
    #     for id_ in idList:
    #         print (id_)
    #     #printDebugMessage('printGetParameters', 'End', 1)    

    # # Get input parameter information
    # def serviceGetParameterDetails(paramName):
    #     #printDebugMessage('serviceGetParameterDetails', 'Begin', 1)
    #     #printDebugMessage('serviceGetParameterDetails', 'paramName: ' + paramName, 2)
    #     requestUrl = baseUrl + '/parameterdetails/' + paramName
    #     #printDebugMessage('serviceGetParameterDetails', 'requestUrl: ' + requestUrl, 2)
    #     xmlDoc = restRequest(requestUrl)
    #     doc = xmltramp.parse(xmlDoc)
    #     #printDebugMessage('serviceGetParameterDetails', 'End', 1)
    #     return doc

    # # Print description of a parameter
    # def printGetParameterDetails(paramName):
    #     #printDebugMessage('printGetParameterDetails', 'Begin', 1)
    #     doc = serviceGetParameterDetails(paramName)
    #     print (str(doc.name) + "\t" + str(doc.type))
    #     print (doc.description)
    #     for value in doc.values:
    #         print (value.value,end=" ")
    #         if str(value.defaultValue) == 'true':
    #             print ('default', end=" ")
    #         print
    #         print ("\t" + str(value.label))
    #         if(hasattr(value, 'properties')):
    #             for wsProperty in value.properties:
    #                 print  ("\t" + str(wsProperty.key) + "\t" + str(wsProperty.value))
    #     #print doc
    #     #printDebugMessage('printGetParameterDetails', 'End', 1)

    # # Submit job
    # def serviceRun(email, title, params):
    #     #printDebugMessage('serviceRun', 'Begin', 1)
    #     # Insert e-mail and title into params
    #     params['email'] = email
    #     if title:
    #         params['title'] = title
    #     requestUrl = baseUrl + '/run/'
    #     #printDebugMessage('serviceRun', 'requestUrl: ' + requestUrl, 2)
    #     # Signature methods requires special handling (list)
    #     applData = ''
    #     if 'appl' in params:
    #         # So extract from params
    #         applList = params['appl']
    #         del params['appl']
    #         # Build the method data options
    #         for appl in applList:
    #             applData += '&appl=' + appl
    #     # Get the data for the other options
    #     requestData = urllib.parse.urlencode(params);
        
    #     requestData += applData;
    #     #printDebugMessage('serviceRun', 'requestData: ' + requestData, 2)
    #     # Errors are indicated by HTTP status codes.
    #     try:
    #         # Set the HTTP User-agent.
    #         user_agent = getUserAgent()
    #         http_headers = { 'User-Agent' : user_agent }
    #         req = urllib2.Request(requestUrl, None, http_headers)
    #         # Make the submission (HTTP POST).
    #         reqH = urllib2.urlopen(req, requestData.encode(encoding='utf_8', errors='strict'))
    #         jobId = str(reqH.read(), 'utf-8')
    #         reqH.close()
    #     except urllib2.HTTPError as ex:
    #         # Trap exception and output the document to get error message.
    #         print (ex.read(), file=sys.stderr)
    #         raise
    #     #printDebugMessage('serviceRun', 'jobId: ' + jobId, 2)
    #     #printDebugMessage('serviceRun', 'End', 1)
    #     return jobId

    # # Get job status
    # def serviceGetStatus(jobId):
    #     #printDebugMessage('serviceGetStatus', 'Begin', 1)
    #     #printDebugMessage('serviceGetStatus', 'jobId: ' + jobId, 2)
    #     requestUrl = baseUrl + '/status/' + jobId
    #     #printDebugMessage('serviceGetStatus', 'requestUrl: ' + requestUrl, 2)
    #     status = restRequest(requestUrl)
    #     #printDebugMessage('serviceGetStatus', 'status: ' + status, 2)
    #     #printDebugMessage('serviceGetStatus', 'End', 1)
    #     return status

    # # Print the status of a job
    # def printGetStatus(jobId):
    #     #printDebugMessage('printGetStatus', 'Begin', 1)
    #     status = serviceGetStatus(jobId)
    #     print (status)
    #     #printDebugMessage('printGetStatus', 'End', 1)
    

    # # Get available result types for job
    # def serviceGetResultTypes(jobId):
    #     #printDebugMessage('serviceGetResultTypes', 'Begin', 1)
    #     #printDebugMessage('serviceGetResultTypes', 'jobId: ' + jobId, 2)
    #     requestUrl = baseUrl + '/resulttypes/' + jobId
    #     #printDebugMessage('serviceGetResultTypes', 'requestUrl: ' + requestUrl, 2)
    #     xmlDoc = restRequest(requestUrl)
    #     doc = xmltramp.parse(xmlDoc)
    #     #printDebugMessage('serviceGetResultTypes', 'End', 1)
    #     return doc['type':]

    # # Print list of available result types for a job.
    # def printGetResultTypes(jobId):
    #     #printDebugMessage('printGetResultTypes', 'Begin', 1)
    #     resultTypeList = serviceGetResultTypes(jobId)
    #     for resultType in resultTypeList:
    #         print (resultType['identifier'])
    #         if(hasattr(resultType, 'label')):
    #             print ("\t", resultType['label'])
    #         if(hasattr(resultType, 'description')):
    #             print ("\t", resultType['description'])
    #         if(hasattr(resultType, 'mediaType')):
    #             print ("\t", resultType['mediaType'])
    #         if(hasattr(resultType, 'fileSuffix')):
    #             print ("\t", resultType['fileSuffix'])
    #     #printDebugMessage('printGetResultTypes', 'End', 1)

    # # Get result
    # def serviceGetResult(jobId, type_):
    #     #printDebugMessage('serviceGetResult', 'Begin', 1)
    #     #printDebugMessage('serviceGetResult', 'jobId: ' + jobId, 2)
    #     #printDebugMessage('serviceGetResult', 'type_: ' + type_, 2)
    #     requestUrl = baseUrl + '/result/' + jobId + '/' + type_
    #     result = restRequest(requestUrl)
    #     #printDebugMessage('serviceGetResult', 'End', 1)
    #     return result

    # # Client-side poll
    # def clientPoll(jobId):
    #     #printDebugMessage('clientPoll', 'Begin', 1)
    #     result = 'PENDING'
    #     while result == 'RUNNING' or result == 'PENDING':
    #         result = serviceGetStatus(jobId)
    #         print (result, file=sys.stderr)
    #         if result == 'RUNNING' or result == 'PENDING':
    #             time.sleep(checkInterval)
    #     #printDebugMessage('clientPoll', 'End', 1)

    # # Get result for a jobid
    # def getResult(jobId):
    #     #printDebugMessage('getResult', 'Begin', 1)
    #     #printDebugMessage('getResult', 'jobId: ' + jobId, 1)
    #     # Check status and wait if necessary
    #     clientPoll(jobId)
    #     # Get available result types
    #     resultTypes = serviceGetResultTypes(jobId)
    #     for resultType in resultTypes:
    #         # Derive the filename for the result
    #         if options.outfile:
    #             filename = options.outfile + '.' + str(resultType['identifier']) + '.' + str(resultType['fileSuffix'])
    #         else:
    #             filename = jobId + '.' + str(resultType['identifier']) + '.' + str(resultType['fileSuffix'])
    #         # Write a result file
    #         if not options.outformat or options.outformat == str(resultType['identifier']):
    #             # Get the result
    #             result = serviceGetResult(jobId, str(resultType['identifier']))
    #             if(str(resultType['mediaType']) == "image/png"
    #                 or str(resultType['mediaType']) == "image/jpeg"
    #                 or str(resultType['mediaType']) == "application/gzip"):
    #                 fmode= 'wb'
    #             else:
    #                 fmode='w'
    #             with open(file=filename, mode=fmode) as fh:
    #                 fh.write(result)
    #             print(filename)
    #     #printDebugMessage('getResult', 'End', 1)

    # def readFile(filename):
    #     with open(file=filename, mode='r') as fh:
    #         data = fh.read()
    #     return data 

    def is_fasta(local_path: str) -> bool:
        with open(local_path, "r") as handle:
            fasta = SeqIO.parse(handle, "fasta")
            return any(fasta)

    def remote_output_dir(remote_path: str) -> str:
        assert remote_path is not None
        if remote_path[-1] != "/":
            remote_path += "/"
        return remote_path

    
    assert is_fasta(local_path=input_file.local_path) == True
    
    file_name = "inter_out.txt"
    out_file = str(Path(file_name))
    remote_file = f"{remote_output_dir(remote_path=output_dir.remote_path)}{file_name}"
    
    
    with open(out_file, "w") as handle:
        with open(input_file.local_path, "r") as fh:
            fasta = SeqIO.parse(fh, "fasta")
            for record in fasta:
                handle.write(f">{record.id}\n")

    return LatchFile(path=out_file, remote_path=remote_file)

@workflow
def interproscan(
    email_addr: str, 
    input_file: LatchFile,
    output_dir: LatchDir,
    goterms: bool = False,
    pathways: bool = False,
) -> LatchFile:
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

        output_dir:
           Output Directory of Results

          __metadata__:
            display_name: Output Directory

        goterms:
           GO Terms from InterProScan

          __metadata__:
            display_name: Include GO Terms

        pathways:
           Pathways from InterProScan

          __metadata__:
            display_name: Include Pathways

    """
    return interproscan_task(
        email_addr=email_addr, 
        input_file=input_file,
        output_dir=output_dir,
        goterms=goterms,
        pathways=pathways,
    )
