# -*- coding: utf-8 -*-

"""
Unit test for the Build models
"""

import os
import sys

sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from test_api import InvenTreeTestCase  # noqa: E402

from inventree.base import Attachment  # noqa: E402
from inventree.build import Build  # noqa: E402


class BuildOrderTest(InvenTreeTestCase):
    """
    Unit tests for Build model
    """

    def get_build(self):
        """
        Return a BuildOrder from the database
        If a build does not already exist, create a new one
        """

        builds = Build.list(self.api)

        n = len(builds)

        if n == 0:
            # Create a new build order
            build = Build.create(
                self.api,
                {
                    "title": "Automated test build",
                    "part": 100,
                    "quantity": 100,
                    "reference": f"BO-{n + 1:04d}",
                }
            )
        else:
            build = builds[-1]

        return build

    def test_list_builds(self):

        build = self.get_build()

        self.assertIsNotNone(build)

        builds = Build.list(self.api)

        self.assertGreater(len(builds), 0)

    def test_build_attachment(self):
        """
        Test that we can upload an attachment against a Build
        """

        if self.api.api_version < Attachment.MIN_API_VERSION:
            return

        build = self.get_build()

        n = len(build.getAttachments())

        # Upload *this* file
        fn = os.path.join(os.path.dirname(__file__), 'test_build.py')

        response = build.uploadAttachment(fn, comment='A self referencing upload!')

        self.assertEqual(response['model_type'], 'build')
        self.assertEqual(response['model_id'], build.pk)
        self.assertEqual(response['comment'], 'A self referencing upload!')

        self.assertEqual(len(build.getAttachments()), n + 1)

    def test_build_cancel(self):
        """
        Test cancelling a build order.
        """

        n = len(Build.list(self.api))

        # Create a new build order
        build = Build.create(
            self.api,
            {
                "title": "Automated test build",
                "part": 25,
                "quantity": 100,
                "reference": f"BO-{n + 1:04d}"
            }
        )

        # Cancel
        build.cancel()

        # Check status
        self.assertEqual(build.status, 30)
        self.assertEqual(build.status_text, 'Cancelled')

    def test_build_complete(self):
        """
        Test completing a build order.
        """

        n = len(Build.list(self.api))

        # Create a new build order
        build = Build.create(
            self.api,
            {
                "title": "Automated test build",
                "part": 25,
                "quantity": 100,
                "reference": f"BO-{n + 1:04d}"
            }
        )

        # Check that build status is pending
        self.assertEqual(build.status, 10)

        if self.api.api_version >= 233:
            # Issue the build order
            build.issue()
            self.assertEqual(build.status, 20)

            # Mark build order as "on hold" again
            build.hold()
            self.assertEqual(build.status, 25)

            # Issue again
            build.issue()
            self.assertEqual(build.status, 20)

        # Complete the build, even though it is not completed
        build.complete(accept_unallocated=True, accept_incomplete=True)

        # Check status
        self.assertEqual(build.status, 40)
        self.assertEqual(build.status_text, 'Complete')


class BuildOrderOutputTests(InvenTreeTestCase):
    """ Unit tests for build output functionality """

    def setUp(self):
        """ Ensure we have a base build order to work with """

        super().setUp()

        builds = Build.list(self.api)

        self.build = Build.create(
            self.api,
            {
                "title": "A new build order",
                "part": 25,
                "quantity": 10,
                "reference": f"BO-{len(builds) + 1:04d}"
            }
        )

    def test_create_build_output(self):
        """Test that we can create a build output item"""

        # Initially, there should be no build outputs
        outputs = self.build.getBuildOutputs()
        self.assertEqual(len(outputs), 0)

        # Let's create 3 new outputs (with serial numbers)
        outputs = self.build.createBuildOutput(
            quantity=3,
            batch_code='TEST-BATCH-001',
            serial_numbers='400+'
        )

        self.assertEqual(len(outputs), 3)
        self.assertEqual(len(self.build.getBuildOutputs()), 3)

        for output in outputs:
            self.assertIsNotNone(output)
            self.assertEqual(output.quantity, 1)
            self.assertEqual(output.batch, 'TEST-BATCH-001')
            self.assertEqual(output.build, self.build.pk)
            self.assertEqual(output.part, self.build.part)
            self.assertTrue(output.is_building)

            # Directly delete the build output
            output.delete()

        # There should now be no build outputs again
        self.assertEqual(len(self.build.getBuildOutputs()), 0)

    def test_cancel_build_output(self):
        """ Test that we can cancel a build output item """

        self.assertEqual(len(self.build.getBuildOutputs()), 0)

        # Create a new build output
        output = self.build.createBuildOutput(
            quantity=1,
            batch_code='TEST-BATCH-001',
            serial_numbers='456'
        )[0]

        self.assertEqual(len(self.build.getBuildOutputs()), 1)

        self.build.cancelBuildOutputs(output)
        self.assertEqual(len(self.build.getBuildOutputs()), 0)

    def test_complete_build_output(self):
        """ Test that we can complete a build output item """

        self.assertEqual(len(self.build.getBuildOutputs()), 0)

        # Create a new build output
        output = self.build.createBuildOutput(
            quantity=1,
            batch_code='TEST-BATCH-001',
            serial_numbers='457'
        )[0]

        q = self.build.completed

        self.assertTrue(output.is_building)
        self.assertEqual(len(self.build.getBuildOutputs()), 1)

        # Complete the build output
        self.build.completeBuildOutput(output, location=1)

        self.assertEqual(len(self.build.getBuildOutputs()), 1)
        output.reload()
        self.assertFalse(output.is_building)

        # Remove the output
        output.delete()
        self.assertEqual(len(self.build.getBuildOutputs()), 0)

        # The number of "completed" items should have increased by 1
        self.build.reload()
        self.assertEqual(self.build.completed, q + 1)

    def test_scrap_build_output(self):
        """Test that we can scrap a build output item"""

        self.assertEqual(len(self.build.getBuildOutputs()), 0)

        # Create a new build output
        output = self.build.createBuildOutput(
            quantity=1,
            batch_code='TEST-BATCH-001',
            serial_numbers='468'
        )[0]

        q = self.build.completed

        self.assertTrue(output.is_building)
        self.assertEqual(len(self.build.getBuildOutputs()), 1)

        # Scrap the build output
        self.build.scrapBuildOutput(output, location=1, notes='Test scrap')
        self.assertEqual(len(self.build.getBuildOutputs()), 1)
        self.assertEqual(len(self.build.getBuildOutputs(complete=False)), 0)
        self.assertEqual(len(self.build.getBuildOutputs(complete=True)), 1)

        output.reload()
        self.assertFalse(output.is_building)

        # Remove the build output
        output.delete()

        # The number of "completed" items should not have increased
        self.build.reload()
        self.assertEqual(self.build.completed, q)
