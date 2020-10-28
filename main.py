from input_data import input_net_args
from NL_iteration import NL_Iteration

# Tips ：
# 序号PQ节点在前，PV节点在后
# 输入参数为标幺值

# 1.数据输入
Line_arg = [
#   导线首端    导线末端    串联电阻    串联电抗    并联电导    并联电纳
    [1 , 2 , 0.02 , 0.06 , 0 , 0],
    [1 , 3 , 0.08 , 0.24 , 0 , 0],
    [2 , 3 , 0.06 , 0.18 , 0 , 0],
    [2 , 4 , 0.06 , 0.18 , 0 , 0],
    [2 , 5 , 0.04 , 0.12 , 0 , 0],
    [3 , 4 , 0.01 , 0.03 , 0 , 0],
    [4 , 5 , 0.08 , 0.24 , 0 , 0]
]

Node_args = [
#       节点序号    类型    参数
    [1, "slack" , {"V":1.06, "Theta":0}],
    [2, "pq"    , {"P":0.2, "Q":0.2} ],
    [3, "pq"    , {"P":-0.45, "Q":-0.15} ],
    [4, "pq"    , {"P":-0.40, "Q":-0.05} ],
    [5, "pq"    , {"P":-0.60, "Q":-0.10} ]
]

Init_val = [
    #       节点序号    参数
    [1, {"e":1.06, "f":0}],
    [2, {"e":1, "f":0}],
    [3, {"e":1, "f":0}],
    [4, {"e":1, "f":0}],
    [5, {"e":1, "f":0}]
]

# 数据处理
args = input_net_args(Line_arg, Node_args, Init_val)
args.gen_node_admittance_matrix()
args.gen_node_infos()
args.gen_init_values()
# 迭代
nl = NL_Iteration(args)
nl.start_iteration()