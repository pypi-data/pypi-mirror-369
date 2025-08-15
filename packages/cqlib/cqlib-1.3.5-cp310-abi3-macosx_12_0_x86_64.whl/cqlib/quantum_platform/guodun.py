# This code is part of cqlib.
#
# Copyright (C) 2024 China Telecom Quantum Group, QuantumCTek Co., Ltd.,
# Center for Excellence in Quantum Information and Quantum Physics.
#
# This code is licensed under the Apache License, Version 2.0. You may
# obtain a copy of this license in the LICENSE file in the root directory
# of this source tree or at http://www.apache.org/licenses/LICENSE-2.0.
#
# Any modifications or derivative works of this code must retain this
# copyright notice, and modified files need to carry a notice indicating
# that they have been altered from the originals.

"""
GuoDun quantum platform
"""
from typing import Optional
from .base import BasePlatform
from cqlib.exceptions import CqlibInputParaError


class GuoDunPlatform(BasePlatform):
    """
    GuoDun quantum platform test case
    """
    # scheme
    SCHEME = 'https'
    # domain
    DOMAIN = 'quantumctek-cloud.com'
    # login path
    LOGIN_PATH = '/api-uaa/oauth/token'
    # machine list path
    MACHINE_LIST_PATH = '/experiment/sdk/quantumComputer/list'
    # machine config path
    MACHINE_CONFIG_PATH = '/experiment/sdk/quantumComputer/config'
    # create lab path
    CREATE_LAB_PATH = '/experiment/sdk/experiment/save'
    # save exp path
    SAVE_EXP_PATH = '/experiment/sdk/experiment/detail/save'
    # query exp path
    QUERY_EXP_PATH = '/experiment/sdk/experiment/result/find'
    # download config path
    DOWNLOAD_CONFIG_PATH = '/experiment/sdk/experiment/download/config/'
    # qcis check regular path
    QCIS_CHECK_REGULAR_PATH = '/experiment/sdk/experiment/qcis/rule/verify'
    # get exp circuit path
    GET_EXP_CIRCUIT_PATH = '/experiment/sdk/experiment/getQcis/by/taskIds'
    # re execute path
    RE_EXECUTE_TASK_PATH = '/experiment/sdk/experiment/resubmit'
    # stop running exp path
    STOP_RUNNING_EXP_PATH = '/experiment/sdk/experiment/discontinue'
    # create exp and run path
    CREATE_EXP_AND_RUN_PATH = '/experiment/sdk/experiment/temporary/save'

    def re_execute_task(
            self,
            query_id: Optional[str] = None,
            lab_id: Optional[str] = None,
    ):
        """
        Re-execute the experiment that has been run previously.

        Args:
            query_id: query id
            lab_id: resubmit all exp tasks in this lab set.

        Returns
            the query id for resubmitting the experiment
        """
        if not lab_id and not query_id:
            raise CqlibInputParaError("Please provide lab_id or query_id.")
        # need to transform to int before sending requests
        try:
            lab_id = int(lab_id)
        except TypeError:
            pass
        try:
            query_id = int(query_id)
        except TypeError:
            pass

        data = {
            "lab_id": lab_id,
            "query_id": query_id
        }
        result = self._send_request(self.RE_EXECUTE_TASK_PATH, method='POST', data=data)
        return result.get('data')

    def stop_running_experiments(
            self,
            lab_id: Optional[str] = None,
            query_id: Optional[str] = None
    ):
        """
        Terminate recently running experiments

        Args:
            query_id: query id
            lab_id: Terminate all exp tasks in this lab set.

        Returns:
            the query id for stopped the experiment
        """
        if not lab_id and not query_id:
            raise CqlibInputParaError("Please provide lab_id or query_id.")
            # need to transform to int before sending requests
        try:
            lab_id = int(lab_id)
        except TypeError:
            pass
        try:
            query_id = int(query_id)
        except TypeError:
            pass
        data = {
            "lab_id": lab_id,
            "query_id": query_id
        }
        result = self._send_request(self.STOP_RUNNING_EXP_PATH, method='POST', data=data)
        return result.get('data')
