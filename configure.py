#!/usr/bin/python3
import optparse as op
import os
import subprocess
import glob
import re
import sys

def parseOptions():
  """Parses command line options
  """
  
  parser=op.OptionParser(usage="Usage %prog"
    ,version="%prog 1.0",description="")
  return parser.parse_args()
def replaceStrInFile(strMatch,strReplace,fileName,maxOccurs=None):
  """Replace all occurrences of strMatch with strReplace in file fileName
  up to maxOccurs if specified.
  """
  
  file=open(fileName,mode='r')
  fileText=file.read()
  file.close()
  
  #how many occurrences are there
  numMatches=fileText.count(strMatch)
  
  if maxOccurs!=None:
    fileText=fileText.replace(strMatch,strReplace,maxOccurs)
    if numMatches>maxOccurs:
      numMatches=maxOccurs
  else:
    fileText=fileText.replace(strMatch,strReplace)
  file=open(fileName,mode='w')
  file.write(fileText)
  file.close()
  return numMatches
def replaceStrInFileRe(pattern,replacement,fileName,maxOccurs=None):
  """Replace all occurrences of pattern with strReplace in file fileName
  up to maxOccurs if specified. This version uses regular expression matching 
  also
  """
  
  file=open(fileName,mode='r')
  fileText=file.read()
  file.close()
  
  #how many occurrences are there
  numMatches=len(re.findall(pattern,fileText))
  
  if maxOccurs!=None:
    fileText=re.sub(pattern,replacement,fileText,count=maxOccurs)
    if numMatches>maxOccurs:
      numMatches=maxOccurs
  else:
    fileText=re.sub(pattern,replacement,fileText)
  file=open(fileName,mode='w')
  file.write(fileText)
  file.close()
  return numMatches
def commentOutLineMatching(pattern,fileName,maxOccurs=None):
  """
  Adds a # to the begging of any line which matches pattern
  """
  
  file=open(fileName,mode='r')
  pattern=re.compile(pattern)
  fileText=""
  numMatches=0
  if maxOccurs==None:
    maxOccurs=sys.maxsize
    
  for line in file:
    if pattern.match(line) and numMatches<maxOccurs:
      fileText+="#"+line
      numMatches+=1
    else:
      fileText+=line
  file.close()
  file=open(fileName,mode='w')
  file.write(fileText)
  file.close()
  return numMatches
def appendToFile(strsToAppend,fileName):
  """Append multiple string to the end of a file
  """
  
  file=open(fileName,mode='r')
  fileText=file.read()
  file.close()
  for strToAppend in strsToAppend:
    fileText+=strToAppend
  file=open(fileName,mode='w')
  file.write(fileText)
  file.close()
def execute(func,*args,dry=False,**kwargs):
  if not dry:
    return func(*args,**kwargs)
  else:
    commandStr=func.__name__+"("
    firstArg=True
    for arg in args:
      if firstArg:
        commandStr+=str(arg)
        firstArg=False
      else:
        commandStr+=","+str(arg)
    for key in kwargs:
      if firstArg:
        commandStr+=key+"="+str(kwargs[key])
        firstArg=False
      else:
        commandStr+=","+key+"="+str(kwargs[key])
    commandStr+=")"
    print(commandStr)
    return None
def restartApache(dry=False):
  """Restarts apache2
  """
  
  execute(subprocess.call,["service","apache2","restart"],dry=dry)
def main():
  
  #parse command line options
  (options,args)=parseOptions()
  
  #configure gmond.conf on master
  confFileName="/etc/ganglia/gmond.conf"
  replaceStrInFile("mcast_join = 239.2.11.71"
    ,"host = localhost"
    ,confFileName,maxOccurs=1)
  commentOutLineMatching('.*mcast_join = 239.2.11.71'
    ,confFileName)
  commentOutLineMatching('.*bind = 239.2.11.71'
    ,confFileName)
    
  #copy over apache setting file
  subprocess.call(["cp","/etc/ganglia-webfrontend/apache.conf"
    ,"/etc/apache2/sites-enabled/ganglia.conf"])
  restartApache()
  
if __name__ == "__main__":
 main()