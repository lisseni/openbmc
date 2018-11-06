#!/bin/bash
#
# Copyright 2018-present Facebook. All Rights Reserved.
#
# This program file is free software; you can redistribute it and/or modify it
# under the terms of the GNU General Public License as published by the
# Free Software Foundation; version 2 of the License.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or
# FITNESS FOR A PARTICULAR PURPOSE.  See the GNU General Public License
# for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program in a file named COPYING; if not, write to the
# Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor,
# Boston, MA 02110-1301 USA
#

for index in 1 2 3 4 5 6 7 8
do
    if [ ! -f /tmp/pim${index}_serial.txt ]; then
        /usr/bin/weutil lc${index} |grep Product|grep Serial|cut -d ' ' -f 4 > /tmp/pim${index}_serial.txt
    fi
    serial=`cat /tmp/pim${index}_serial.txt`
    echo PIM${index} : ${serial}
done

