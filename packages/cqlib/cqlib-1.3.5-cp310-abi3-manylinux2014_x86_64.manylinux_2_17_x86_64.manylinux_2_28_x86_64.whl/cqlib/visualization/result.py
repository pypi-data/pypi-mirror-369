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

from typing import Optional, Union, List

from matplotlib import pyplot as plt

"""
Visualization of experimental results
"""


def draw_histogram(
        histogram_data: Optional[Union[dict, List[dict]]],
        title: Optional[str] = None,
        bar_value_show: Optional[str] = True,
        file_name: Optional[str] = None,
        axis_label: Optional[list] = None,
        interactive: Optional[bool] = False,
        fig_size: Optional[tuple] = (6.4, 4.8),
        legend: Optional[list] = None,
):
    """draw histogram of experiment results

     Args:
         histogram_data: histogram data
         title: histogram title. Default to 'None'
         bar_value_show: Whether to display bar chart values。Default to 'True'
         file_name: file_name: The address to save the image.Default to 'None'
         axis_label: List of axis labels,size 2. one element is the X-axis label and the second element is the Y-axis label. e.g.:["Categories","value"]).Default to 'None'
         interactive:Displays the created image.Default to 'False'
         fig_size: Figure size.  Default to  '(6.4,4.8)'
         legend : The length of the data label must be the same as the number of data

    Returns:
         matplotlib.figure.Figure: a matplotlib figure object for the histogram

    """
    plt.figure(figsize=fig_size)
    new_figure_size = fig_size
    default_figure_size = (6.4, 4.8)
    width_ratio = new_figure_size[0] / default_figure_size[0]
    height_ratio = new_figure_size[1] / default_figure_size[1]
    # 计算总的比例
    total_ratio = (width_ratio + height_ratio) / 2
    if isinstance(histogram_data, dict):
        x_data = list(histogram_data.keys())
        y_data = [histogram_data[key] for key in x_data]

        # 创建柱状图
        bars = plt.bar(x_data, y_data, color="#D6271D")

        if bar_value_show:
            # 添加数值标签
            for bar, value in zip(bars, y_data):
                plt.text(
                    bar.get_x() + bar.get_width() / 2,
                    bar.get_height(),
                    f"{value:.2f}",
                    ha="center",
                    va="bottom",
                )

    elif isinstance(histogram_data, list):
        keys_set = set()  # 初始化一个空集合
        for d in histogram_data:
            for key in d.keys():
                keys_set.add(key)
        keys = sorted(keys_set)
        x_data = range(len(keys))

        # 创建一个字典来存储每个key对应的所有值
        values_by_key = {key: [] for key in keys}
        for d in histogram_data:
            for key in keys:
                values_by_key[key].append(d.get(key, 0))

        # 确定每个组中柱子的宽度
        total_width = 0.88
        num_dicts = len(histogram_data)
        width = total_width / num_dicts
        if legend:
            if len(legend) != num_dicts:
                raise ValueError(
                    f"legend 标签数为{len(legend)}个,数据个数为{num_dicts}个,不匹配"
                )

        # 绘制每个组的柱状图
        for i in range(num_dicts):
            y_data = [
                values_by_key[key][i] if i < len(values_by_key[key]) else 0
                for key in keys
            ]
            x_positions = [
                (x - total_width / 2 + width / 2) + i * width for x in x_data
            ]
            if legend:
                label = legend[i]
            else:
                label = f"data{i + 1}"
            bars = plt.bar(x_positions, y_data, width=width, label=label)
            if bar_value_show:
                # 添加数值标签
                for bar, value in zip(bars, y_data):
                    width = bar.get_width()
                    plt.text(
                        bar.get_x() + bar.get_width() / 2,
                        bar.get_height(),
                        f"{value:.2f}",
                        ha="center",
                        va="bottom",
                    )

        plt.xticks(x_data, keys)
        plt.legend(loc="upper left", bbox_to_anchor=(1, 1))

    if title:
        # 添加标题
        plt.title(title, fontsize=10 * total_ratio)

    if axis_label:
        # 添加轴标签
        plt.xlabel(axis_label[0])
        plt.ylabel(axis_label[1])

    if file_name is not None:
        # 保存图像
        plt.savefig(f"{file_name}.png")

    fig = plt.gcf()

    # 显示图形
    if interactive:
        plt.show()

    return fig
