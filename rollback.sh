#!/bin/bash

if [ -e testProject/backup.tar.gz ]
   then
       mkdir backup
       tar -xvzf testProject/backup.tar.gz -C backup
       rm -r testProject
       mv backup testProject
fi

