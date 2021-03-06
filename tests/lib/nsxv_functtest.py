# Copyright 2015 The Capirca Project Authors All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""Functional test class for nsxv.py."""

import copy
import optparse
from absl.testing import absltest
from xml.etree import ElementTree as ET

from capirca.lib import naming
from capirca.lib import nsxv
from capirca.lib import policy
from capirca.tests.lib import nsxv_mocktest


class NsxvFunctionalTest(absltest.TestCase):
  """Functional testing for NSXV."""

  def setUp(self):
    """Call before every test case."""
    super().setUp()
    parser = optparse.OptionParser()
    parser.add_option(
        '-d',
        '--def',
        dest='definitions',
        help='definitions directory',
        default='../def')
    (FLAGS, args) = _parser.parse_args()
    self.defs = naming.Naming(FLAGS.definitions)

  def tearDown(self):
    super().tearDown()
    pass

  def runTest(self):
    pass

  def test_nsxv_policy(self):
    pol = policy.ParsePolicy(nsxv_mocktest.POLICY, self.defs)
    exp_info = 2
    nsx = copy.deepcopy(pol)
    fw = nsxv.Nsxv(nsx, exp_info)
    output = str(fw)

    # parse the xml
    root = ET.fromstring(output)
    # check section name
    section_name = {'id': '1007', 'name': 'POLICY_NAME'}
    self.assertEqual(root.attrib, section_name)
    # check name and action
    self.assertEqual(root.find('./rule/name').text, 'reject-imap-requests')
    self.assertEqual(root.find('./rule/action').text, 'reject')

    # check IPV4 destination
    exp_destaddr = ['200.1.1.4/31']

    for destination in root.findall('./rule/destinations/destination'):
      self.assertEqual((destination.find('type').text), 'Ipv4Address')
      value = (destination.find('value').text)
      if value not in exp_destaddr:
        self.fail('IPv4Address destination not found in test_nsxv_str()')

    # check protocol
    protocol = int(root.find('./rule/services/service/protocol').text)
    self.assertEqual(protocol, 6)

    # check destination port
    destination_port = root.find('./rule/services/service/destinationPort').text
    self.assertEqual(destination_port, '143')

  def test_nsxv_nosectiondid(self):
    pol = policy.ParsePolicy(nsxv_mocktest.POLICY_NO_SECTION_ID, self.defs)
    exp_info = 2
    nsx = copy.deepcopy(pol)
    fw = nsxv.Nsxv(nsx, exp_info)
    output = str(fw)
    # parse the xml
    root = ET.fromstring(output)
    # check section name
    section_name = {'name': 'POLICY_NO_SECTION_ID_NAME'}
    self.assertEqual(root.attrib, section_name)
    # check name and action
    self.assertEqual(root.find('./rule/name').text, 'accept-icmp')
    self.assertEqual(root.find('./rule/action').text, 'allow')

    # check protocol
    protocol = int(root.find('./rule/services/service/protocol').text)
    self.assertEqual(protocol, 1)

  def test_nsxv_nofiltertype(self):
    pol = policy.ParsePolicy(nsxv_mocktest.POLICY_NO_FILTERTYPE, self.defs)
    self.assertRaises(nsxv.UnsupportedNsxvAccessListError, nsxv.Nsxv(pol, 2))

  def test_nsxv_incorrectfiltertype(self):
    pol = policy.ParsePolicy(nsxv_mocktest.POLICY_INCORRECT_FILTERTYPE,
                             self.defs)
    self.assertRaises(nsxv.UnsupportedNsxvAccessListError, nsxv.Nsxv(pol, 2))

  def test_nsxv_optionkywd(self):
    pol = policy.ParsePolicy(nsxv_mocktest.POLICY_OPTION_KYWD, self.defs)
    self.assertRaises(nsxv.NsxvAclTermError, str(nsxv.Nsxv(pol, 2)))

  if __name__ == '__main__':
    absltest.main()
