#
# Copyright (C) 2016 Red Hat, Inc.
#
#  Licensed under the Apache License, Version 2.0 (the "License"); you may
#  not use this file except in compliance with the License. You may obtain
#  a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#  Unless required by applicable law or agreed to in writing, software
#  distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
#  WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
#  License for the specific language governing permissions and limitations
#  under the License.
#

import mock

from datetime import datetime
from datetime import timedelta

from networking_odl.common import constants as odl_const
from networking_odl.db import db
from networking_odl.db import models

from neutron.db import api as neutron_db_api
from neutron.tests.unit.testlib_api import SqlTestCaseLight
from oslo_db.exception import DBDeadlock
from unittest2.case import TestCase


class DbTestCase(SqlTestCaseLight, TestCase):

    UPDATE_ROW = [odl_const.ODL_NETWORK, 'id', odl_const.ODL_UPDATE,
                  {'test': 'data'}]

    def setUp(self):
        super(DbTestCase, self).setUp()
        self.db_session = neutron_db_api.get_session()
        self.addCleanup(self._db_cleanup)

    def _db_cleanup(self):
        self.db_session.query(models.OpendaylightJournal).delete()
        self.db_session.query(models.OpendaylightMaintenance).delete()

    def _update_row(self, row):
        self.db_session.merge(row)
        self.db_session.flush()

    def _test_validate_updates(self, rows, time_deltas, expected_validations):
        for row in rows:
            db.create_pending_row(self.db_session, *row)

        # update row created_at
        rows = db.get_all_db_rows(self.db_session)
        now = datetime.now()
        for row, time_delta in zip(rows, time_deltas):
            row.created_at = now - timedelta(hours=time_delta)
            self._update_row(row)

        # validate if there are older rows
        for row, expected_valid in zip(rows, expected_validations):
            valid = not db.check_for_older_ops(self.db_session, row)
            self.assertEqual(expected_valid, valid)

    def _test_retry_count(self, retry_num, max_retry,
                          expected_retry_count, expected_state):
        # add new pending row
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)

        # update the row with the requested retry_num
        row = db.get_all_db_rows(self.db_session)[0]
        row.retry_count = retry_num - 1
        db.update_pending_db_row_retry(self.db_session, row, max_retry)

        # validate the state and the retry_count of the row
        row = db.get_all_db_rows(self.db_session)[0]
        self.assertEqual(expected_state, row.state)
        self.assertEqual(expected_retry_count, row.retry_count)

    def _test_update_row_state(self, from_state, to_state):
        # add new pending row
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)

        row = db.get_all_db_rows(self.db_session)[0]
        for state in [from_state, to_state]:
            # update the row state
            db.update_db_row_state(self.db_session, row, state)

            # validate the new state
            row = db.get_all_db_rows(self.db_session)[0]
            self.assertEqual(state, row.state)

    def test_validate_updates_same_object_uuid(self):
        self._test_validate_updates(
            [self.UPDATE_ROW, self.UPDATE_ROW], [1, 0], [True, False])

    def test_validate_updates_same_created_time(self):
        self._test_validate_updates(
            [self.UPDATE_ROW, self.UPDATE_ROW], [0, 0], [True, True])

    def test_validate_updates_different_object_uuid(self):
        other_row = list(self.UPDATE_ROW)
        other_row[1] += 'a'
        self._test_validate_updates(
            [self.UPDATE_ROW, other_row], [1, 0], [True, True])

    def test_validate_updates_different_object_type(self):
        other_row = list(self.UPDATE_ROW)
        other_row[0] = odl_const.ODL_PORT
        other_row[1] += 'a'
        self._test_validate_updates(
            [self.UPDATE_ROW, other_row], [1, 0], [True, True])

    def test_get_oldest_pending_row_none_when_no_rows(self):
        row = db.get_oldest_pending_db_row_with_lock(self.db_session)
        self.assertIsNone(row)

    def _test_get_oldest_pending_row_none(self, state):
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)
        row = db.get_all_db_rows(self.db_session)[0]
        row.state = state
        self._update_row(row)

        row = db.get_oldest_pending_db_row_with_lock(self.db_session)
        self.assertIsNone(row)

    def test_get_oldest_pending_row_none_when_row_processing(self):
        self._test_get_oldest_pending_row_none(odl_const.PROCESSING)

    def test_get_oldest_pending_row_none_when_row_failed(self):
        self._test_get_oldest_pending_row_none(odl_const.FAILED)

    def test_get_oldest_pending_row_none_when_row_completed(self):
        self._test_get_oldest_pending_row_none(odl_const.COMPLETED)

    def test_get_oldest_pending_row(self):
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)
        row = db.get_oldest_pending_db_row_with_lock(self.db_session)
        self.assertIsNotNone(row)
        self.assertEqual(odl_const.PROCESSING, row.state)

    def test_get_oldest_pending_row_order(self):
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)
        older_row = db.get_all_db_rows(self.db_session)[0]
        older_row.last_retried -= timedelta(minutes=1)
        self._update_row(older_row)

        db.create_pending_row(self.db_session, *self.UPDATE_ROW)
        row = db.get_oldest_pending_db_row_with_lock(self.db_session)
        self.assertEqual(older_row, row)

    def test_get_oldest_pending_row_when_deadlock(self):
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)
        update_mock = mock.MagicMock(side_effect=(DBDeadlock, mock.DEFAULT))

        # Mocking is mandatory to achieve a deadlock regardless of the DB
        # backend being used when running the tests
        with mock.patch.object(db, 'update_db_row_state', new=update_mock):
            row = db.get_oldest_pending_db_row_with_lock(self.db_session)
            self.assertIsNotNone(row)

        self.assertEqual(2, update_mock.call_count)

    def _test_delete_rows_by_state_and_time(self, last_retried, row_retention,
                                            state, expected_rows):
        db.create_pending_row(self.db_session, *self.UPDATE_ROW)

        # update state and last retried
        row = db.get_all_db_rows(self.db_session)[0]
        row.state = state
        row.last_retried = row.last_retried - timedelta(seconds=last_retried)
        self._update_row(row)

        db.delete_rows_by_state_and_time(self.db_session,
                                         odl_const.COMPLETED,
                                         timedelta(seconds=row_retention))

        # validate the number of rows in the journal
        rows = db.get_all_db_rows(self.db_session)
        self.assertEqual(expected_rows, len(rows))

    def test_delete_completed_rows_no_new_rows(self):
        self._test_delete_rows_by_state_and_time(0, 10, odl_const.COMPLETED, 1)

    def test_delete_completed_rows_one_new_row(self):
        self._test_delete_rows_by_state_and_time(6, 5, odl_const.COMPLETED, 0)

    def test_delete_completed_rows_wrong_state(self):
        self._test_delete_rows_by_state_and_time(10, 8, odl_const.PENDING, 1)

    def test_valid_retry_count(self):
        self._test_retry_count(1, 1, 1, odl_const.PENDING)

    def test_invalid_retry_count(self):
        self._test_retry_count(2, 1, 1, odl_const.FAILED)

    def test_update_row_state_to_pending(self):
        self._test_update_row_state(odl_const.PROCESSING, odl_const.PENDING)

    def test_update_row_state_to_processing(self):
        self._test_update_row_state(odl_const.PENDING, odl_const.PROCESSING)

    def test_update_row_state_to_failed(self):
        self._test_update_row_state(odl_const.PROCESSING, odl_const.FAILED)

    def test_update_row_state_to_completed(self):
        self._test_update_row_state(odl_const.PROCESSING, odl_const.COMPLETED)

    def _test_maintenance_lock_unlock(self, db_func, existing_state,
                                      expected_state, expected_result):
        row = models.OpendaylightMaintenance(id='test',
                                             state=existing_state)
        self.db_session.add(row)
        self.db_session.flush()

        self.assertEqual(expected_result, db_func(self.db_session))
        row = self.db_session.query(models.OpendaylightMaintenance).one()
        self.assertEqual(expected_state, row['state'])

    def test_lock_maintenance(self):
        self._test_maintenance_lock_unlock(db.lock_maintenance,
                                           odl_const.PENDING,
                                           odl_const.PROCESSING,
                                           True)

    def test_lock_maintenance_fails_when_processing(self):
        self._test_maintenance_lock_unlock(db.lock_maintenance,
                                           odl_const.PROCESSING,
                                           odl_const.PROCESSING,
                                           False)

    def test_unlock_maintenance(self):
        self._test_maintenance_lock_unlock(db.unlock_maintenance,
                                           odl_const.PROCESSING,
                                           odl_const.PENDING,
                                           True)

    def test_unlock_maintenance_fails_when_pending(self):
        self._test_maintenance_lock_unlock(db.unlock_maintenance,
                                           odl_const.PENDING,
                                           odl_const.PENDING,
                                           False)
