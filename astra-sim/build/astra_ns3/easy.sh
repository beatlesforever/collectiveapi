#!/bin/bash

# 设置 Comm_ 数值的范围（使用新值）
COMM_VALUES=(1024 2048 4096 8192 16384 32768 65536 131072 262144 524288 1048576 2097152 4194304 8388608 16777216 33554432 67108864 134217728 268435456 536870912)

# 绝对路径
SCRIPT_DIR=$(dirname "$(realpath $0)")
NS3_DIR="${SCRIPT_DIR}/../../extern/network_backend/ns-3"

# 其他固定参数
SYSTEM="${SCRIPT_DIR}/../../inputs/system/Switch.json"
MEMORY="${SCRIPT_DIR}/../../inputs/remote_memory/analytical/no_memory_expansion.json"
LOGICAL_TOPOLOGY="${SCRIPT_DIR}/../../inputs/network/ns3/sample_8nodes_1D.json"
NETWORK="${NS3_DIR}/scratch/config/config.txt"  # 修正 config.txt 绝对路径

# 结果存储目录
RESULT_DIR="${SCRIPT_DIR}/result"
mkdir -p "${RESULT_DIR}"  # 创建 result 目录（如果不存在）

# 生成时间戳
TIMESTAMP=$(date +"%Y%m%d_%H%M%S")
RESULT_FILE="${RESULT_DIR}/result_${TIMESTAMP}.txt"

# 解析 TOPOLOGY_FILE 绝对路径
RELATIVE_TOPOLOGY_FILE=$(grep -oP '(?<=^TOPOLOGY_FILE )\S+' "${NETWORK}")
TOPOLOGY_FILE="$(dirname "${NETWORK}")/${RELATIVE_TOPOLOGY_FILE}"  # 拼接 config.txt 目录和相对路径，得到绝对路径

# 在结果文件中记录 SYSTEM、MEMORY、LOGICAL_TOPOLOGY、TOPOLOGY_FILE 的内容（不包含 config.txt）
{
    echo "===================="
    echo " SYSTEM CONFIGURATION "
    echo "===================="
    cat "${SYSTEM}"
    echo -e "\n"

    echo "===================="
    echo " MEMORY CONFIGURATION "
    echo "===================="
    cat "${MEMORY}"
    echo -e "\n"

    echo "===================="
    echo " LOGICAL TOPOLOGY CONFIGURATION "
    echo "===================="
    cat "${LOGICAL_TOPOLOGY}"
    echo -e "\n"

    echo "===================="
    echo " TOPOLOGY FILE (${TOPOLOGY_FILE}) "
    echo "===================="
    if [[ -f "${TOPOLOGY_FILE}" ]]; then
        cat "${TOPOLOGY_FILE}"
    else
        echo "Topology file not found: ${TOPOLOGY_FILE}"
    fi
    echo -e "\n"
} >> "${RESULT_FILE}"

# 存储结果的数组
declare -A RESULTS
PREV_TIMEOUT=60  # 记录上一轮成功的超时时间，初始为 60s
MAX_TIMEOUT=3600  # 最大超时时间 1 小时

# 运行循环
for COMM in "${COMM_VALUES[@]}"; do
    TIMEOUT_DURATION=$PREV_TIMEOUT  # 继承上一次的超时设定

    # 更新 WORKLOAD 变量
    WORKLOAD="${SCRIPT_DIR}/../../extern/graph_frontend/output/NPU_8_Dim_2_Runtime_5_Tensor_1024_Comm_${COMM}/one_comm_coll_node_allreduce"

    echo "Running simulation with Comm_${COMM}, initial timeout: ${TIMEOUT_DURATION}s..."

    while true; do
        # 进入工作目录
        cd "${NS3_DIR}/build/scratch"

        # 运行 `ns3-dev-AstraSimNetwork-default` 并限制超时时间
        timeout "${TIMEOUT_DURATION}" stdbuf -oL ./ns3-dev-AstraSimNetwork-default \
            --workload-configuration="${WORKLOAD}" \
            --system-configuration="${SYSTEM}" \
            --network-configuration="${NETWORK}" \
            --remote-memory-configuration="${MEMORY}" \
            --logical-topology-configuration="${LOGICAL_TOPOLOGY}" \
            --comm-group-configuration="empty" > output.log 2>&1

        # 提取所有 GPU 的 cycles 结果
        CYCLES=$(grep -oP 'sys\[\d+\] finished, \K\d+ cycles' output.log)

        # 如果 `sys[...] finished, XXXX cycles` 存在，则记录每个 GPU 的结果并退出循环
        if [[ -n "$CYCLES" ]]; then
            echo "Comm_${COMM}:" | tee -a "${RESULT_FILE}"
            echo "$CYCLES" | tee -a "${RESULT_FILE}"
            RESULTS["$COMM"]="$CYCLES"
            PREV_TIMEOUT=$TIMEOUT_DURATION  # 记录当前成功的超时时间
            break
        else
            echo "WARNING: No cycle results found for Comm_${COMM} after ${TIMEOUT_DURATION}s!" | tee -a "${RESULT_FILE}"
            if [[ "$TIMEOUT_DURATION" -ge "$MAX_TIMEOUT" ]]; then
                echo "ERROR: Maximum timeout reached for Comm_${COMM}, aborting this simulation." | tee -a "${RESULT_FILE}"
                RESULTS["$COMM"]="ERROR: No results after max timeout"
                break
            fi
            # 翻倍超时时间，最多到 `MAX_TIMEOUT`
            TIMEOUT_DURATION=$(( TIMEOUT_DURATION * 2 ))
            if [[ "$TIMEOUT_DURATION" -gt "$MAX_TIMEOUT" ]]; then
                TIMEOUT_DURATION="$MAX_TIMEOUT"
            fi
            echo "Increasing timeout to ${TIMEOUT_DURATION}s for Comm_${COMM}..."
        fi
    done

    # 返回原目录
    cd "${SCRIPT_DIR}"

    echo "--------------------------------------" | tee -a "${RESULT_FILE}"

    # 等待 2 秒（可选），防止系统过载
    sleep 2
done

# 输出最终结果并排序
echo "All simulations completed! Sorting results by message size..." | tee -a "${RESULT_FILE}"

# 重新排序并写入文件
{
    echo "Final sorted results:"
    for COMM in $(echo "${!RESULTS[@]}" | tr ' ' '\n' | sort -n); do
        echo "Comm_${COMM}:"
        echo "${RESULTS[$COMM]}"
    done
} | tee -a "${RESULT_FILE}"

echo "Results saved to: ${RESULT_FILE}"
