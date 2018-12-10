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

import os
import subprocess
import unittest
import json

os_guid = u"6b7e3683761ee397e78eb688222d8d5a"

class BasicSystemSanity(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        pass # We don't need this for the time being
    
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
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "hwd"])
        self.assertEqual(output.rstrip('\n'), "online",
            "Output must match string 'online'")

    def test_dataprotectiond_is_online(self):
        pass

    def test_datareplicationd_is_online(self):
        pass

    def test_secured_is_online(self):
        """ Check if secured service is online """
        output = subprocess.check_output(
            ["/usr/bin/svcs", "-H", "-o", "state", "secured"])
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
