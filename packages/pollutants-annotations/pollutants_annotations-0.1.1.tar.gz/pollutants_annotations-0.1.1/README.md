# Pollutants Annotations Dataset

污染物识别神经网络的训练数据集，包含文本和对应的污染物实体标注。\
Pollutants databases which provide for neural network (RNN,Spacy,etc.) 's training.\

Caution: Here only to colum of the databases, which named text and entities. May you have a good time!

Author: Yaolin,Zhang (UG.s)\
Email: zhangyaolin@stu2022.jnu.edu.cn\
Address: Jinan University， College of Environment and Climate\
Latest: 20250813


## 数据集介绍

该数据集包含两列：
- `text`: 包含污染物相关描述的文本
- `entities`: 标注的实体，格式为 `(begin, end, entity_name)`

## 安装

```bash
pip install pollutants-annotations