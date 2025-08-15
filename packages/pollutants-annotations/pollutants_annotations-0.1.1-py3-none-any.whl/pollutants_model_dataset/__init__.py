import os
import pandas as pd

# 获取数据目录路径
PACKAGE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(PACKAGE_DIR, 'data')


def load_data():
    """
    加载污染物标注数据集

    返回:
        pandas.DataFrame: 包含text和entities列的数据集
    """
    data_path = os.path.join(DATA_DIR, 'pollutants_annotations.csv')
    if not os.path.exists(data_path):
        raise FileNotFoundError(f"数据文件未找到: {data_path}")

    return pd.read_csv(data_path)


__version__ = "0.1.0"
__all__ = ["load_data", "__version__"]