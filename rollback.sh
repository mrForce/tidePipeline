#!/bin/bash

if [ -e EL4Project/backup.tar.gz ]
   then
       mkdir backup
       tar -xvzf EL4Project/backup.tar.gz -C backup
       rm -r EL4Project
       mv backup EL4Project
fi

