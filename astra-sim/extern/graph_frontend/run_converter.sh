#!/bin/bash

# 激活虚拟环境（可选）
source chakra_env/bin/activate

# 设置参数
INPUT_FILENAME="../../inputs/workload/ASTRA-sim-1.0/Resnet50_DataParallel.txt"
OUTPUT_FILENAME="../../extern/graph_frontend/output/output"
NUM_NPUS=8
NUM_DIMS=1
NUM_PASSES=1

# 创建输出目录（如果还没有）
mkdir -p "$(dirname "$OUTPUT_FILENAME")"

# 使用虚拟环境中的 python 执行 chakra 转换器
./chakra_env/bin/python -m chakra.et_converter.et_converter \
  --input_type Text \
  --input_filename "$INPUT_FILENAME" \
  --output_filename "$OUTPUT_FILENAME" \
  --num_npus "$NUM_NPUS" \
  --num_dims "$NUM_DIMS" \
  --num_passes "$NUM_PASSES"
