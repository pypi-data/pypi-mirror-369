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
TianYan quantum platform
"""
import logging

from cqlib.exceptions import CqlibError, CqlibRequestError
from cqlib.utils.laboratory_utils import LaboratoryUtils
from .base import BasePlatform, QuantumLanguage

logger = logging.getLogger('cqlib')


class TianYanPlatform(BasePlatform):
    """
    Tian yan quantum computing cloud quantum_platform
    """
    SCHEME = 'https'
    DOMAIN = 'qc.zdxlz.com'
    LOGIN_PATH = '/qccp-auth/oauth2/sdk/opnId'
    CREATE_LAB_PATH = '/qccp-quantum/sdk/experiment/save'
    SAVE_EXP_PATH = '/qccp-quantum/sdk/experiment/detail/save'
    RUN_EXP_PATH = '/qccp-quantum/sdk/experiment/detail/run'
    SUBMIT_EXP_PATH = '/qccp-quantum/sdk/experiment/submit'
    # create exp and run path
    CREATE_EXP_AND_RUN_PATH = '/qccp-quantum/sdk/experiment/temporary/save'
    QUERY_EXP_PATH = '/qccp-quantum/sdk/experiment/result/find'
    # download config path
    DOWNLOAD_CONFIG_PATH = '/qccp-quantum/sdk/experiment/download/config'
    # qics check regular path
    QCIS_CHECK_REGULAR_PATH = '/qccp-quantum/sdk/experiment/qcis/rule/verify'
    # get exp circuit path
    GET_EXP_CIRCUIT_PATH = '/qccp-quantum/sdk/experiment/getQcis/by/taskIds'
    # machine list path
    MACHINE_LIST_PATH = '/qccp-quantum/sdk/quantumComputer/list'
    # re execute path
    RE_EXECUTE_TASK_PATH = '/qccp-quantum/sdk/experiment/resubmit'
    # stop running exp path
    STOP_RUNNING_EXP_PATH = ''

    def run_experiment(
            self,
            exp_id: str,
            num_shots: int = 12000,
            is_verify: bool = True
    ):
        """
        running the experiment returns the query result id.

        Args:
            exp_id: experimental id. the id returned by the save_experiment interface.
            num_shots: number of repetitions per experiment. Defaults to 12000.
            is_verify: Is the circuit verified.

        Returns:
            experiment task query id.
        """
        data = {
            "exp_id": exp_id,
            "shots": num_shots,
            "is_verify": is_verify,
        }
        result = self._send_request(path=self.RUN_EXP_PATH, data=data, method='post')
        return result.get('data').get('query_id')

    # pylint: disable=too-many-arguments,too-many-positional-arguments
    def submit_experiment(
            self,
            circuit: str | list[str],
            language: QuantumLanguage = QuantumLanguage.QCIS,
            name: str = None,
            parameters: list[list[str]] = None,
            values: list[list[float]] = None,
            lab_id: str = None,
            lab_name: str = None,
            num_shots: int = 12000,
            machine_name: str = None,
            is_verify: bool = True,
            **kwargs
    ):
        """
        running the experiment returns the query result id.

        Args:
            circuit: experimental content, qcis. Defaults to None.
            language: quantum language code. Defaults to qcis.
            name: new experiment collection Name.
            parameters: parameters that need to be assigned in the experimental content.
            values: The values corresponding to the parameters that need to be assigned
                    in the experimental content. Defaults to None.
            lab_id: the result returned by the create_experiment interface, experimental set id.
            lab_name: defined lab name.
            num_shots: number of repetitions per experiment. Defaults to 12000.
            machine_name: specified which machine to use.
            is_verify: Is the circuit verified.

        Returns:
            experiment task query id.
        """
        if isinstance(circuit, str):
            circuit = [circuit]
        if parameters or values:
            assert len(parameters) == len(circuit) == len(values), \
                CqlibError("The length of parameters, circuits, and values must be equal")
            lab_util = LaboratoryUtils()
            circuit = lab_util.assign_parameters(circuit, parameters, values)
            if not circuit:
                raise CqlibError("Unable to assign a value to circuit, please check circuit.")

        data = {
            "circuit": circuit,
            "language": language.value,
            "name": name,
            "lab_id": lab_id,
            "lab_name": lab_name,
            "shots": num_shots,
            "computerCode": machine_name or self.machine_name,
            "is_verify": is_verify,
        }
        if 'noise' in kwargs:
            data['noise'] = kwargs['noise']
        if 'quantum_state' in kwargs:
            data['quantumState'] = kwargs['quantum_state']
        if 'rules' in kwargs:
            data['nm'] = kwargs['rules']
        result = self._send_request(path=self.SUBMIT_EXP_PATH, data=data, method='post')
        return result.get('data').get('query_ids')

    def query_experiment(
            self,
            query_id: str | list[str],
            max_wait_time: int = 3600,
            sleep_time: int = 5,
            readout_calibration: bool = False,
            machine_config: dict = None,
    ):
        """
        query the experiment result.

        Args:
            query_id: experiment task ids. The maximum count is 50.
            max_wait_time: maximum waiting time for querying experiments. Defaults to 3600.
            sleep_time: If query result failed, take a break and start again.
            readout_calibration: readout correction for quantum measurements. Defaults to False.
            machine_config: Optional machine configuration. If not provided, will attempt to
                        download configuration automatically when readout_calibration is True.
        """
        data = super().query_experiment(query_id, max_wait_time, sleep_time)
        if readout_calibration:
            lu = LaboratoryUtils()
            if machine_config is None:
                try:
                    machine_config = self.download_config()
                except CqlibRequestError:
                    logger.warning("Only quantum physics machines can obtain configuration, "
                                   "please check the machine type.")
            if machine_config is not None:
                for item in data:
                    calibration_result = lu.probability_calibration(
                        result=item, laboratory=self, config_json=machine_config
                    )
                    item['probability'] = lu.probability_correction(calibration_result)
        return data
