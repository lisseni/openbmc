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
from fsc_util import Logger
from subprocess import Popen, PIPE
import time

# Overrides the functions that need to do HW dependent
# actions, such as LED control, PWM full boost and
# emergency shutdown

def yamp_set_fan_led(fan, color='led_blue'):
    # YAMP LED has only green and LED
    # So, blue (fan good) will turn on green
    FCM_CPLD = "/sys/bus/i2c/drivers/fancpld/13-0060/"
    for fan in fan.split():
        # YAMP fans are all named as number
        if not fan.isdigit():
            break
        fan = int(fan)
        if fan > 5 or fan < 1:
            break;
        # 1 means off
        green_value = 1
        red_value = 1
        green_key = FCM_CPLD + "fan" + str(fan) + "_led_green"
        red_key = FCM_CPLD + "fan" + str(fan) + "_led_red"

        # 0 means on
        if "red" in color:
            red_value = 0
        elif "blue" in color or "green" in color:
            # We don't have blue, but have green
            green_value = 0
        else:
            return 0  # error
        cmd_green = "echo " + str(green_value) + " > " + green_key
        cmd_red = "echo " + str(red_value) + " > " + red_key
        # Logger.debug("Using cmd=%s for led" % str(cmd))
        # Do the best effort. When LED setting commands fail, move on,
        # as this failure alone will not damage or take down hardware
        response1 = Popen(cmd_green, shell=True, stdout=PIPE).stdout.read()
        response2 = Popen(cmd_red, shell=True, stdout=PIPE).stdout.read()
    return 0

def board_fan_actions(fan, action='None'):
    if "led" in action:
        yamp_set_fan_led(fan.label, color=action)
    else:
        Logger.warn("fscd: %s has no action %s" % (fan.label, str(action),))
    pass

def yamp_set_all_pwm(boost):
    # The script name is same as Minipack.
    # Note that, the argument to this script is in range [0,100]
    # and the script will scale the value to [0,255]
    cmd = ('/usr/local/bin/set_fan_speed.sh %d' % (boost))
    response = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    return response

def board_callout(callout='None', **kwargs):
    if 'init_fans' in callout:
        boost = 100
        if 'boost' in kwargs:
            boost = kwargs['boost']
        Logger.info("FSC init fans to boost=%s " % str(boost))
        return yamp_set_all_pwm(boost)
    else:
        Logger.warn("Need to perform callout action %s" % callout)
    pass

def yamp_host_shutdown():
    # Do the best effort by :
    # 1. Turn off CPU
    # 2. Then turn off SCD
    # 3. Then turn off all PSU
    # We do this because, if any one of CPLD/FPGA is already
    # malfunctioning, we still want to turn off as much part of
    # the system as possible.
    SCD_POWER_REG = "/sys/bus/i2c/drivers/scdcpld/4-0023/scd_power_en"
    CPU_OFF = "/usr/local/bin/wedge_power.sh off"
    SCD_OFF = "echo 0 > " + SCD_POWER_REG
    # First, turn off most of the switch board
    Logger.info("host_shutdown() executing {}".format(SCD_OFF))
    response = Popen(SCD_OFF, shell=True, stdout=PIPE).stdout.read()
    time.sleep(3)
    # Then, turn off X86 CPU
    Logger.info("host_shutdown() executing {}".format(CPU_OFF))
    response = Popen(CPU_OFF, shell=True, stdout=PIPE).stdout.read()
    time.sleep(3)
    # Finally, turn all PSU one by one, on bus 5,6,7,8
    for bus in range(5,9):
       # We don't have DPS1900 driver, so we use raw i2c cmd
       # there is no other process using this bus, so this should be safe
       cmd='i2cset -f -y ' + str(bus) + ' 0x58 0x1 0x40'
       Logger.info("host_shutdown() executing {}".format(cmd))
       response = Popen(cmd, shell=True, stdout=PIPE).stdout.read()
    return 0

def board_host_actions(action='None', cause='None'):
    if "host_shutdown" in action:
        Logger.crit("Host is shutdown due to cause %s" % (str(cause),))
        return yamp_host_shutdown()
    Logger.warn("Host needs action '%s' and cause '%s'" %
                (str(action), str(cause),))
    pass

