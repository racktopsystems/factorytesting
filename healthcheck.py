#!/usr/bin/env python2.7
# -*- coding: utf-8 -*-
#
# CDDL HEADER START
#
# The contents of this file are subject to the terms of the
# Common Development and Distribution License (the "License").
# You may not use this file except in compliance with the License.
#
# You can obtain a copy of the license at usr/src/OPENSOLARIS.LICENSE
# or http://www.opensolaris.org/os/licensing.
# See the License for the specific language governing permissions
# and limitations under the License.
#
# When distributing Covered Code, include this CDDL HEADER in each
# file and include the License file at usr/src/OPENSOLARIS.LICENSE.
# If applicable, add the following below this CDDL HEADER, with the
# fields enclosed by brackets "[]" replaced with your own identifying
# information: Portions Copyright [yyyy] [name of copyright owner]
#
# CDDL HEADER END
#
# Copyright 2018 RackTop Systems.

import datetime
import os
import subprocess
import unittest
import json

os_guid = u"6b7e3683761ee397e78eb688222d8d5a"

# def is_known_drive_vendor(mfg):
#     m = {
#         "hgst": 1,
#         "hitachi": 1,
#         "seagate": 1,
#     }
#     return mfg.lower() in m

class BasicSystemSanity(unittest.TestCase):
    _hwinfo = []
    
    def known_drive_vendor(self, mfg):
        m = {
            "hgst": 1,
            "hitachi": 1,
            "seagate": 1,
        }
        return mfg.lower() in m

    def skip_drive_ok(self, make):
        should_skip = ("ata") # Add others here in the future
        for entry in should_skip:
            if entry in make.lower():
                return True
        return False

    def drive_type_sensible(self, t):
        return t.lower() in ("ssd", "hdd")

    @classmethod
    def hwinfo(cls):
        return cls._hwinfo

    @classmethod
    def setUpClass(cls):
        # We will refer to this information multiple times.
        output = subprocess.check_output(
            ["/usr/racktop/sbin/hwadm", "-j", "ls", "d"]
        )
        cls.hwinfo = json.loads(output)

    @classmethod
    def tearDownClass(cls):
        pass # We don't need this for the time being

    def setUp(self):
        pass # We don't need this for the time being

    def tearDown(self):
        pass # We don't need this for the time being

    def shortDescription(self):
        doc = self._testMethodDoc
        return doc and doc or None

    def test_system_log_no_kernel_msgs(self):
        """ System log does not contain any kernel warnings or errors """
        output = subprocess.check_output(
            ["egrep", 'kern.warn|kern.err',"/var/adm/messages"])
        self.assertEqual(output.rstrip('\n'), "",
            "Expected no output, instead log contains '%d' " \
            "kernel warnings and/or errors" %
            len(output.rstrip('\n').split('\n')))

    def test_smf_is_healthy(self):
        """ SMF should not report anything if all services are online """
        output = subprocess.check_output(["/usr/bin/svcs", "-xv"])
        self.assertEqual(output, "",
            "Expected no output, instead one or more services is not healthy")

    def test_hwd_is_online(self):
        """ hwd service must always be online """
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "hwd"])
        self.assertEqual(output.rstrip('\n'), "online",
            "Expected 'online' got '%s'" % output.rstrip('\n'))

    def test_secured_is_online(self):
        """ secured service must always be online """
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "secured"])
        self.assertEqual(output.rstrip('\n'), "online",
            "Expected 'online' got '%s'" % output.rstrip('\n'))

    def test_dataprotectiond_is_online(self):
        """ dataprotectiond service must always be online """
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "dataprotectiond"])
        self.assertEqual(output.rstrip('\n'), "online",
            "Expected 'online' got '%s'" % output.rstrip('\n'))

    def test_datareplicationd_is_disabled(self):
        """ datareplicationd service must always be disabled """
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "datareplicationd"])
        self.assertEqual(output.rstrip('\n'), "disabled",
            "Expected 'disabled' got '%s'" % output.rstrip('\n'))

    def test_bsrapid_is_online(self):
        """ bsrapid service must always be online """
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "bsrapid"])
        self.assertEqual(output.rstrip('\n'), "online",
            "Expected 'online' got '%s'" % output.rstrip('\n'))

    def test_no_core_files_present(self):
        """ Check that there are no core files present """
        _, _, filenames = os.walk("/var/cores").next()
        self.assertListEqual(filenames, [],
            "Expected to find no core files, instead found '%d' files" \
            % len(filenames))

    def test_license_installed_is_expected(self):
        pass

    def test_domain_name_present(self):
        output = subprocess.check_output(
            ["/usr/racktop/sbin/bsradm", "dns", "domain", "get"]
        )
        self.assertIsNot(output, "")

    def test_only_one_image_installed(self):
        """ Only a single OS image should be loaded """
        output = subprocess.check_output(
            ["/usr/racktop/sbin/bsradm", "-j", "os", "installed"])
        j = json.loads(output.rstrip('\n'))
        self.assertEqual(len(j), 1,
            "Expected to find only a single OS image, " \
            "instead found '%d' images" % len(j))

    def test_os_version_expected(self):
        output = subprocess.check_output(
            ["/usr/racktop/sbin/bsradm", "-j", "os"]
        )
        j = json.loads(output)
        self.assertEqual(j[u'BootGuid'], os_guid)

    def test_fault_state_expected(self):
        """ Check that Fault Management did not detect any faults """
        output = subprocess.check_output(
            ["/usr/sbin/fmadm", "faulty", "-s"]
        )
        self.assertEqual(output.rstrip('\n'), "",
        "Expected to get no results, instead have '%d' faults" \
        % len(output.split('\n')[3:-1]))

    def test_no_fmdump_entries_expected(self):
        pass

    def test_no_device_not_ready_errors_expected(self):
        """ Check that no drives report Device Not Ready """
        errct = 0
        output = subprocess.check_output(
            ["/usr/bin/kstat", "-j", "-p", "sderr:::Device\ Not\ Ready"]
        )
        j = json.loads(output)
        for entry in j:
            errct += entry[u'data'][u'Device Not Ready']
        self.assertEqual(errct, 0,
        "Expected to get 0 errors, instead have '%d' errors" % errct)

    def test_no_hard_errors_expected(self):
        """ Check that no drives report Hard Errors """
        errct = 0
        output = subprocess.check_output(
            ["/usr/bin/kstat", "-j", "-p", "sderr:::Hard\ Errors"]
        )
        j = json.loads(output)
        for entry in j:
            errct += entry[u'data'][u'Hard Errors']
        self.assertEqual(errct, 0,
        "Expected to get 0 errors, instead have '%d' errors" % errct)

    def test_no_media_errors_expected(self):
        """ Check that no drives report Media Errors """
        errct = 0
        output = subprocess.check_output(
            ["/usr/bin/kstat", "-j", "-p", "sderr:::Media\ Error"]
        )
        j = json.loads(output)
        for entry in j:
            errct += entry[u'data'][u'Media Error']
        self.assertEqual(errct, 0,
        "Expected to get 0 errors, instead have '%d' errors" % errct)

    def test_no_no_device_errors_expected(self):
        """ Check that no drives report No Device """
        errct = 0
        output = subprocess.check_output(
            ["/usr/bin/kstat", "-j", "-p", "sderr:::No\ Device"]
        )
        j = json.loads(output)
        for entry in j:
            errct += entry[u'data'][u'No Device']
        self.assertEqual(errct, 0,
        "Expected to get 0 errors, instead have '%d' errors" % errct)

    def test_no_soft_errors_expected(self):
        """ Check that no drives report Soft Errors """
        errct = 0
        output = subprocess.check_output(
            ["/usr/bin/kstat", "-j", "-p", "sderr:::Soft\ Errors"]
        )
        j = json.loads(output)
        for entry in j:
            errct += entry[u'data'][u'Soft Errors']
        self.assertEqual(errct, 0,
        "Expected to get 0 errors, instead have '%d' errors" % errct)

    def test_no_transport_errors_expected(self):
        """ Check that no drives report Transport Errors """
        errct = 0
        output = subprocess.check_output(
            ["/usr/bin/kstat", "-j", "-p", "sderr:::Transport\ Errors"]
        )
        j = json.loads(output)
        for entry in j:
            errct += entry[u'data'][u'Transport Errors']
        self.assertEqual(errct, 0,
        "Expected to get 0 errors, instead have '%d' errors" % errct)

    def test_no_scsi_vhci_errors_expected(self):
        pass

    def test_hwadm_drive_attributes_expected(self):
        """ Check drive count and basic attributes are sensible """
        now = datetime.datetime.now()
        # Check that attributes of device make sense
        self.assertGreaterEqual(len(self.hwinfo), 12)
        for i in self.hwinfo:
            if self.skip_drive_ok(i[u'Make']):
                continue # Skip devices that we don't expect to be used for pool
            self.assertTrue(self.known_drive_vendor(i[u'Make']),
                "Encountered unexpected drive make: '%s'" % i[u'Make'])
            ts = i[u'HWInfo'][u'RegistrationTimestamp'][:-5]
            regts = datetime.datetime.strptime(ts, "%Y-%m-%dT%H:%M:%S")
            reg_stat = i[u'HWInfo'][u'RegistrationStatus']
            ready_stat = i[u'HWInfo'][u'ReadyStatus']

            # We will see how this works with SSDs
            self.assertFalse(reg_stat == u"NotSupported",
                "Registration should be supported on this drive")
            if reg_stat == u"Registered":
                # Nothing should be < 2017
                self.assertGreaterEqual(regts.year, 2017)
                # One years of sway
                self.assertLessEqual(now.year - regts.year, 1)
                # Registration timestamp cannot be later than time now
                self.assertTrue(now > regts,
                    "Registration timestamp cannot be more recent "\
                    "than present time")

            # Device name should be a part of a the device path.
            self.assertEqual(i[u'Path'], "/dev/rdsk/%ss0" % i[u'DeviceName'])
            # Model, Serial cannot be empty
            self.assertIsNot(i[u'Serial'], "")
            self.assertGreaterEqual(i[u'Serial'], 8)
            self.assertIsNot(i[u'Model'], "")
            # Some things have an expected length
            self.assertEqual(len(i[u'StorageUnitId']), 16)
            self.assertEqual(len(i[u'Wwn']), 16)
            # Bay number should be a nonnegative value and 83 is largest
            # possible currently, since largest shelf has 84 bays.
            bay_min_idx, bay_max_idx = 0, 83
            bay_idx = i[u'HWInfo'][u'Bay']
            temp_c = i[u'HWInfo'][u'CelsiusTemperature']
            temp_max_c = i[u'HWInfo'][u'MaxFunctionalTemp']            
            self.assertGreaterEqual(i[u'HWInfo'][u'Bay'], bay_min_idx,
                "Bay number cannot be lower than '%d', " % bay_min_idx)
            self.assertLessEqual(i[u'HWInfo'][u'Bay'], bay_max_idx,
                "Bay number cannot be greater than '%d'" % bay_max_idx)
            # Temperature sensors should be reporting something sensible
            self.assertGreaterEqual(temp_c, 0,
                "Temperature cannot be negative")
            self.assertGreaterEqual(temp_max_c, 0,
                "Maximum operating temperature cannot be negative")
            # Current temp cannot be greater than maximum operating temp
            self.assertLessEqual(temp_c, temp_max_c)
            self.assertTrue(self.drive_type_sensible(i[u'HWInfo'][u'Type']),
                "Only SSDs and HDDs are allowed drive types")


class CustomTextTestResult(unittest.TextTestResult):
    def addSuccess(self, test):
        if self.showAll:
            self.stream.writeln(u'✓')
    
    def addFailure(self, test, err):
        super(unittest.TextTestResult, self).addFailure(test, err)
        if self.showAll:
            self.stream.writeln(u'✗')
        elif self.dots:
            self.stream.write('F')
            self.stream.flush()

    def getDescription(self, test):
        doc_first_line = test.shortDescription()
        if self.descriptions and doc_first_line:
            return doc_first_line
        else:
            return str(test)

    def printErrorList(self, flavour, errors):
        for test, err in errors:
            self.stream.writeln(self.separator1)
            self.stream.writeln("%s: %s" % (flavour,self.getDescription(test)))
            self.stream.writeln(self.separator2)
            self.stream.writeln("%s" % err.split('\n')[3])

if __name__ == '__main__':
    suite = unittest.TestLoader().loadTestsFromTestCase(BasicSystemSanity)
    unittest.TextTestRunner(verbosity=2, resultclass=CustomTextTestResult).run(suite)
