class input_net_args(object):

    def __init__(self, arg_line, arg_node, arg_init_val):
        self.Line = arg_line
        self.Node = arg_node
        self._Init_val = arg_init_val
        self.Init_val = []
        self.Node_infos = []
        self._line_admittance = []
        self.G = []
        self.B = []
        self.Order = 0
        self._line_args_conv()

    # 复数倒数    
    def _complx_reciprocal(self, real, imag):
        mod = real*real + imag*imag
        return real/mod, imag/mod
    # 阻抗转导纳
    def impedance2admittance(self, R, X):
        return self._complx_reciprocal(R, X)
    # 导纳转阻抗
    def admittance2impedance(self, G, B):
        return self._complx_reciprocal(G, B)

    def _line_args_conv(self):
        for item in self.Line:
            temp = item
            temp[2], temp[3] = self.impedance2admittance(item[2], item[3])
            self._line_admittance.append(temp)


    # 生成导纳矩阵
    def gen_node_admittance_matrix(self):
        temp = []
        for item in self.Line:
            temp.append(item[0])
            temp.append(item[1])

        # 导纳矩阵阶数
        self.Order = max(temp)

        for i in range(0, self.Order):
            temp_1 = []
            temp_2 = []
            for j in range(0, self.Order):
                if i == j:
                    val_real = 0
                    val_imag = 0
                    for item in self.Line:
                        if ( item[0] == (j + 1) or item[1] == (j + 1) ):
                            val_real += item[2] + item[4]
                            val_imag += item[3] + item[5]
                    temp_1.append(val_real)  
                    temp_2.append(-val_imag)                  
                else:
                    val_real = 0
                    val_imag = 0
                    for item in self.Line:
                        if ( item[0] == (i + 1) and item[1] == (j + 1) ) or ( item[1] == (i + 1) and item[0] == (j + 1) ):
                            val_real += -item[2]
                            val_imag += -item[3]
                    temp_1.append(val_real)
                    temp_2.append(-val_imag)                  
            self.G.append(temp_1)
            self.B.append(temp_2)
        return self.G, self.B
            
    def _gen_node_info(self, node_num, node_type, node_info):
        if (not isinstance(node_num, int)) or (node_num <= 0):
            return "argument node_num is not a vaild value.", False
        if (not isinstance(node_type, str)) or (not node_type.isalpha()) or (not ((node_type.upper() == "PQ") or (node_type.upper() == "PV") or (node_type.upper() == "SLACK"))):
            return "argument node_type is not a vaild value.", False

        node_value = {"node_num":node_num, "node_type":node_type.upper()}
        
        if node_type.upper() == "PQ":
            for k in node_info:
                if k.upper() == "P":
                    node_value.update({"P":node_info[k]})
                elif k.upper() == "Q":
                    node_value.update({"Q":node_info[k]})
          

        if node_type.upper() == "PV":
            for k in node_info:
                if k.upper() == "P":
                    node_value.update({"P":node_info[k]})
                elif k.upper() == "V":
                    node_value.update({"V":node_info[k]})

        if node_type.upper() == "SLACK":
            for k in node_info:
                if k.upper() == "V":
                    node_value.update({"V":node_info[k]})
                elif k.upper() == "THETA":
                    node_value.update({"THETA":node_info[k]})
        return node_value

    def gen_node_infos(self):
        for i in range(0, len(self.Node)):
            for node_info in self.Node:
                if node_info[0] == (i+1):
                    self.Node_infos.append(self._gen_node_info(node_info[0], node_info[1], node_info[2]))
                    break
    def gen_init_values(self):
        for i in range(0, len(self._Init_val)):
            for val in self._Init_val:
                if val[0] == (i+1):
                    self.Init_val.append(val)
                    break

        



if __name__ == "__main__":
    
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
        [1, "slack" , {"V":0.98, "Theta":0}],
        [2, "pq"    , {"P":0.22, "Q":0.13} ],
        [4, "pv"    , {"P":0.22, "V":0.99} ],
        [3, "pq"    , {"P":0.12, "Q":0.13} ],
        [5, "pq"    , {"P":-0.22, "Q":0.13} ]
    ]

    Init_val = [
        #       节点序号    参数
        [3, {"e":1, "f":0}],
        [1, {"e":1, "f":0}],
        [4, {"e":1, "f":0}],
        [2, {"e":1, "f":0}],
        [5, {"e":1, "f":0}]
    ]

    # 数据处理
    test_args = input_net_args(Line_arg, Node_args, Init_val)
    G, B = test_args.gen_node_admittance_matrix()
    # print(G, "\n", B, "\n\n")    
    test_args.gen_node_infos()
    # print(test_args.Node_infos)
    test_args.gen_init_values()
    # print(test_args.Init_val)