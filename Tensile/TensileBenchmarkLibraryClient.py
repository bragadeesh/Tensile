################################################################################
# Copyright (C) 2016 Advanced Micro Devices, Inc. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell cop-
# ies of the Software, and to permit persons to whom the Software is furnished
# to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IM-
# PLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, FITNESS
# FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR
# COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER
# IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNE-
# CTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
################################################################################
import argparse
import sys
import csv
import os
from subprocess import Popen, PIPE

################################################################################
# Benchmark Problem Size
################################################################################
def BenchmarkProblemSize(cmdPrefix, row):
  cmd = cmdPrefix
  output = ""
  for size in row:
    cmd += " "
    cmd += size
  cmd += " 0"
  process = Popen(cmd, stdout=PIPE, shell=True)
  stdout = process.communicate()[0]

  # parse output
  functionIdx = stdout.find("Function[")
  colonIdx = stdout.find(":", functionIdx)
  gflopsIdx = stdout.find("GFlop", colonIdx)
  barIdx = stdout.find("|", colonIdx)
  msIdx = stdout.find("ms", barIdx)

  # print results
  gflops =  float(stdout[colonIdx+1:gflopsIdx])
  ms = float(stdout[barIdx+1:msIdx])
  return (gflops, ms)

################################################################################
# Benchmark Problem Sizes
################################################################################
def TensileBenchmarkLibraryClient(userArgs):
  # parse args
  argParser = argparse.ArgumentParser()
  argParser.add_argument("Executable")
  argParser.add_argument("FunctionIdx")
  argParser.add_argument("ProblemSizesPath")
  argParser.add_argument("NumAverage")
  args = argParser.parse_args(userArgs)
  N = int(args.NumAverage)

  # executable path
  executablePath = os.path.realpath( args.Executable )
  print "ExecutablePath: ", executablePath
  print "FunctionIdx: ", args.FunctionIdx

  # read problem sizes
  problemSizesPath = os.path.realpath( args.ProblemSizesPath )
  print "ProblemSizesPath: ", problemSizesPath
  csvFileRaw = open(problemSizesPath, "r")
  csvFile = csv.reader(csvFileRaw)
  print "NumAverage: ", args.NumAverage

  # print column headers
  numIndices = -1
  for row in csvFile:
    numIndices = len(row)
    break
  output = ""
  for i in range(0, numIndices):
    sizeStr = "size%u" % i
    output += "%6s, " % sizeStr
  output += "%9s, %9s, " % ( "medGF", "medMs" )
  output += "%9s, %9s, " % ( "avgGF", "avgMs" )
  output += "%9s, %9s" % ( "stdGF", "stdMs" )
  print output

  # begin commandString
  cmdPrefix = ""
  cmdPrefix += executablePath
  cmdPrefix += " "
  cmdPrefix += args.FunctionIdx
  cmdPrefix += " "

  # benchmark each problem size
  for row in csvFile:
    gflopList = []
    msList = []
    for i in range(0, N):
      (gflops, ms) = BenchmarkProblemSize(cmdPrefix, row)
      gflopList.append(gflops)
      msList.append(ms)
    meanGFlops = mean(gflopList)
    meanMs = mean(msList)
    medianGFlops = median(gflopList)
    medianMs = median(msList)
    stddevGFlops = stddev(gflopList)
    stddevMs = stddev(msList)

    # format output
    output = ""
    for size in row:
      output += "%6u, " % int(size)
    output += "%9.3f, %9.3f, " % (medianGFlops, medianMs)
    output += "%9.3f, %9.3f, " % (meanGFlops, meanMs)
    output += "%9.3f, %9.3f" % (stddevGFlops, stddevMs)
    print output

def median(lst):
  sortedList = sorted(lst)
  return sortedList[len(sortedList)/2]

def mean(lst):
  total = 0
  for i in range(len(lst)):
    total += lst[i]
  return (total / len(lst))

def stddev(lst):
  total = 0
  mn = mean(lst)
  for i in range(len(lst)):
    total += pow((lst[i]-mn),2)
  return (total/len(lst))**0.5

if __name__ == "__main__":
  TensileBenchmarkLibraryClient(sys.argv[1:])