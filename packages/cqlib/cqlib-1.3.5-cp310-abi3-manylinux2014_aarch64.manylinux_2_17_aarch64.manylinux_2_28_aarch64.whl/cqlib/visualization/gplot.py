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

from typing import Optional
import matplotlib.pyplot as plt
from matplotlib.cm import ScalarMappable
from matplotlib.patches import Circle, FancyBboxPatch
from matplotlib import colormaps

from cqlib import GuoDunPlatform
from ..exceptions import VisualizationError

"""
Topology visualization
"""


def draw_gplot(
        machine_name: Optional[str],
        info: Optional[str] = None,
        file_name: Optional[str] = None,
        interactive: Optional[bool] = False,
        scale: Optional[float] = 1.0,
):
    """Draw a topology diagram of a quantum computer

    Args:
        machine_name: name of quantum computer.
        info: Quantum computer information,Only one of ['T1', 'T2', 'gate_error', 'two_gate_error', 'Readout_Error'] can be selected.Default to 'None'
        file_name: The address to save the image.Default to 'None'
        interactive: Displays the created image.Default to 'False'
        scale: Scale of image to draw .The value must be greater than 0,if it is greater than 1.0, it is enlarged, and if it is less than 1.0, it is shrunk. Default to '1.0'

    Returns:
        matplotlib.figure.Figure: a matplotlib figure object for the gplot diagram

    Raises:
        VisualizationError: The failure to query the topology data of the quantum computer may be due to network reasons,
                   or the input 'machine_name' parameter is incorrect
        ValueError: 'info' parameter error
    """
    if scale <= 0:
        raise ValueError("scale参数值不能小于等于0")
    param_list = None
    qubit_used = None
    unit = None
    update_time = None
    # 0 :标准拓扑图   1：获取bit相关值的拓扑图   2：获取双比特门相关值的拓扑图
    draw_type = 0
    # 颜色集合
    sm = None
    if info is not None:
        if info not in ["T1", "T2", "gate_error", "two_gate_error", "Readout_Error"]:
            raise ValueError(
                "参数必须是'T1', 'T2', 'gate_error', 'two_gate_error', 'Readout_Error'中的一个"
            )
        if info == "T1":
            draw_type = 1
            detail_params = {
                "type": "qubit",
                "computerCode": machine_name,
                "label": "relatime-T1",
            }
            detail_data = _get_computer_data(detail_params)
        elif info == "T2":
            draw_type = 1
            detail_params = {
                "type": "qubit",
                "computerCode": machine_name,
                "label": "relatime-T2",
            }
            detail_data = _get_computer_data(detail_params)
        elif info == "two_gate_error":
            draw_type = 2
            detail_params = {
                "type": "two-qubit gate",
                "computerCode": machine_name,
                "label": "czGate-gate error",
            }
            detail_data = _get_computer_data(detail_params)
        elif info == "gate_error":
            draw_type = 1
            detail_params = {
                "type": "qubit",
                "computerCode": machine_name,
                "label": "singleQubit-gate error",
            }
            detail_data = _get_computer_data(detail_params)
        elif info == "Readout_Error":
            draw_type = 1
            detail_params = {
                "type": "readout",
                "computerCode": machine_name,
                "label": "readoutArray-Readout Error",
            }
            detail_data = _get_computer_data(detail_params)
        else:
            detail_data = None
        if detail_data and detail_data != 0:
            computer_detail = info.replace("_", " ")
            if "gate error" in computer_detail:
                start_index = computer_detail.find("gate error")
                computer_detail = computer_detail[start_index:]

            param_list = detail_data.get(computer_detail).get("param_list")
            qubit_used = detail_data.get(computer_detail).get("qubit_used")
            unit = detail_data.get(computer_detail).get("unit")
            update_time = detail_data.get(computer_detail).get("update_time")
            # 创建颜色映射对象，指定颜色映射的范围和颜色映射名称
            cmap = colormaps.get_cmap("viridis")
            sm = ScalarMappable(cmap=cmap)
            sm.set_clim(vmin=min(param_list), vmax=max(param_list))
        else:
            raise VisualizationError("获取量子计算机拓扑图数据失败")
    gplot_params = {
        "type": "overview",
        "computerCode": machine_name,
        "label": "qpu_coordinate,coupler_map,disabled_couplers,disabled_qubits",
    }
    gplot_data = _get_computer_data(gplot_params)
    if gplot_data == 0:
        raise VisualizationError("获取量子计算机拓扑图数据失败")
    qpu_coordinate = gplot_data.get("qpu_coordinate")
    coupler_map = gplot_data.get("coupler_map")
    disabled_qubits = gplot_data.get("disabled_qubits").split(",")
    disabled_couplers = gplot_data.get("disabled_couplers").split(",")
    x_len = 0
    y_len = 0
    for value in qpu_coordinate.values():
        if x_len < value[0]:
            x_len = value[0]
        if y_len < value[1]:
            y_len = value[1]
    # 创建画布
    plt.figure(figsize=(x_len, y_len - 1), dpi=90 * scale)
    plt.xlim(0, x_len)
    plt.ylim(y_len, 0)
    # 画圆
    for key, value in qpu_coordinate.items():
        if "Q" in key:
            # 如果用户输入了computer_detail参数，且查询成功
            if draw_type == 1 and key not in disabled_qubits:
                index = qubit_used.index(key)
                if key in disabled_qubits:
                    circle = Circle(
                        (value[1], value[0]),
                        0.3,
                        color=sm.to_rgba(param_list[index]),
                        alpha=1,
                        zorder=3,
                    )
                else:
                    circle = Circle(
                        (value[1], value[0]),
                        0.3,
                        color=sm.to_rgba(param_list[index]),
                        alpha=1,
                        zorder=3,
                    )
                plt.gca().add_patch(circle)
                # 设置颜色 如果大于平均值 则为黑色， 如果小于平均值 ，则为白色， 保证用户能够看清楚数据
                if param_list[index] > sum(param_list) / len(param_list):
                    annotate_color = "black"
                else:
                    annotate_color = "white"
                plt.annotate(
                    key,
                    (value[1], value[0] - 0.1),
                    color=annotate_color,
                    fontsize=7,
                    ha="center",
                    va="center",
                )
                plt.annotate(
                    param_list[index],
                    (value[1], value[0] + 0.1),
                    color=annotate_color,
                    fontsize=7,
                    ha="center",
                    va="center",
                )
            else:
                if key in disabled_qubits:
                    circle = Circle(
                        (value[1], value[0]), 0.3, color="#A09AA0", alpha=1, zorder=3
                    )
                else:
                    circle = Circle(
                        (value[1], value[0]), 0.3, color="#DAB1B3", alpha=1, zorder=3
                    )
                plt.gca().add_patch(circle)
                plt.annotate(
                    key,
                    (value[1], value[0]),
                    color="white",
                    fontsize=13,
                    ha="center",
                    va="center",
                )
    # 画线
    for key, value in coupler_map.items():
        q1 = qpu_coordinate.get(value[0])
        q2 = qpu_coordinate.get(value[1])

        if key in disabled_couplers:
            color = "#A09AA0"
        else:
            color = "#DAB1B3"
        if draw_type == 2 and key not in disabled_couplers:
            index = qubit_used.index(key)
            plt.plot(
                [q1[1], q2[1]],
                [q1[0], q2[0]],
                linewidth=10,
                color=sm.to_rgba(param_list[index]),
                zorder=1,
            )
            # 创建圆角矩形
            rect = FancyBboxPatch(
                ((q1[1] + q2[1]) / 2 - 0.13, (q1[0] + q2[0]) / 2 - 0.07),
                0.3,
                0.10,
                boxstyle="round,pad=0.1",
                linewidth=1,
                edgecolor=color,
                facecolor="white",
                alpha=1,
                zorder=2,
            )
            plt.gca().add_patch(rect)
            plt.text(
                (q1[1] + q2[1]) / 2,
                (q1[0] + q2[0]) / 2 - 0.07,
                key,
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=6,
                color=color,
                zorder=3,
            )
            plt.text(
                (q1[1] + q2[1]) / 2,
                (q1[0] + q2[0]) / 2 + 0.05,
                param_list[index],
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=8,
                color="black",
                zorder=3,
            )
        else:
            plt.plot([q1[1], q2[1]], [q1[0], q2[0]], linewidth=4, color=color, zorder=1)
            # 创建圆角矩形
            rect = FancyBboxPatch(
                ((q1[1] + q2[1]) / 2 - 0.15, (q1[0] + q2[0]) / 2),
                0.3,
                0.04,
                boxstyle="round,pad=0.1",
                linewidth=1,
                edgecolor=color,
                facecolor="white",
                alpha=1,
                zorder=2,
            )
            plt.gca().add_patch(rect)
            plt.text(
                (q1[1] + q2[1]) / 2,
                (q1[0] + q2[0]) / 2 + 0.025,
                key,
                horizontalalignment="center",
                verticalalignment="center",
                fontsize=8,
                color=color,
                zorder=3,
            )

    plt.axis("equal")
    plt.axis("off")
    if param_list is None:
        plt.subplots_adjust(top=1, bottom=0, left=0, right=1)
        # 抬头
        plt.text(
            0.5,
            -0.125,
            f"machine_name:{machine_name}",
            fontsize=13,
            color="red",
            ha="left",
            va="top",
        )
        plt.text(
            10,
            -0.125,
            f"Calibration time:{update_time}",
            fontsize=13,
            color="#D6271D",
            ha="left",
            va="top",
        )
    else:
        plt.subplots_adjust(top=1, bottom=-0.05, left=0, right=1)
        # 颜色条
        plt.colorbar(sm, ax=plt.gca(), fraction=0.1, pad=-0.01, shrink=0.6)
        # 抬头
        plt.text(
            7,
            -0.05,
            f"min={min(param_list)},avg={round(sum(param_list) / len(param_list), 3)},max={max(param_list)};unit:{unit}",
            fontsize=18,
            ha="center",
            va="center",
        )
        plt.text(
            0.5,
            -1,
            f"machine_name:{machine_name}",
            fontsize=13,
            color="#D6271D",
            ha="left",
            va="top",
        )
        plt.text(
            0.5, -0.5, f"info:{info}", fontsize=13, color="#D6271D", ha="left", va="top"
        )
        plt.text(
            9.5,
            -1,
            f"Calibration time:{update_time}",
            fontsize=13,
            color="#D6271D",
            ha="left",
            va="top",
        )
    if file_name is not None:
        plt.savefig(f"{file_name}.png")
    fig = plt.gcf()
    if interactive:
        plt.show()
    return fig


def _get_computer_data(params):
    """
    Query information about the topology of a quantum computer。
    """
    return GuoDunPlatform(login_key='', auto_login=False).get_machine_config(params)
