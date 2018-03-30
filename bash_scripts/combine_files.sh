#!/bin/bash

numargs=$#
cat ${@:1: $#-1} > "${!numargs}"
