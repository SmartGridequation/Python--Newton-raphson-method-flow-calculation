import numpy as np
import copy

class NL_Iteration(object):
    def __init__(self, infos):
        self.infos = infos
        self.init_value = self.infos.Init_val
        self._delta_P_PQ = []
        self._delta_Q_PQ = []
        self._delta_P_PV = []
        self._delta_U_PV = []
        self.delta_left = []
        self.J = []
        

    def __calc_delta_val(self):
        self._delta_P_PQ = []
        self._delta_Q_PQ = []
        self._delta_P_PV = []
        self._delta_U_PV = []
        for i, node in enumerate(self.infos.Node_infos):
            if node["node_type"] == "SLACK":
                continue
            e_i = 0
            f_i = 0
            P_i = 0
            Q_i = 0
            for item in self.init_value:
                if item[0] == (i+1):
                    e_i = item[1]["e"]
                    f_i = item[1]["f"]
                    break            
            
            if node["node_type"] == "PQ":
                P_i = node["P"]
                Q_i = node["Q"]

                temp = 0
                for j, init_val in enumerate(self.init_value):
                    temp += e_i * (self.infos.G[i][j] * init_val[1]["e"] - self.infos.B[i][j] * init_val[1]["f"]) + f_i * (self.infos.G[i][j] * init_val[1]["f"] + self.infos.B[i][j] * init_val[1]["e"])
                self._delta_P_PQ.append(P_i - temp)

                temp = 0
                for j, init_val in enumerate(self.init_value):
                    temp += f_i * (self.infos.G[i][j] * init_val[1]["e"] - self.infos.B[i][j] * init_val[1]["f"]) - e_i * (self.infos.G[i][j] * init_val[1]["f"] + self.infos.B[i][j] * init_val[1]["e"])
                self._delta_Q_PQ.append(Q_i - temp)


            if node["node_type"] == "PV":
                P_i = node["P"]

                temp = 0
                for j, init_val in enumerate(self.init_value):
                    temp += e_i * (self.infos.G[i][j] * init_val[1]["e"] - self.infos.B[i][j] * init_val[1]["f"]) + f_i * (self.infos.G[i][j] * init_val[1]["f"] + self.infos.B[i][j] * init_val[1]["e"])
                self._delta_P_PV.append(P_i - temp)

                temp = node["V"]**2 - (self.init_value[i][1]["e"]**2 + self.init_value[i][1]["f"]**2)
                self._delta_U_PV.append(temp)

        # 
        self.delta_left = []
        for i in range(0, len(self._delta_P_PQ)):
            self.delta_left.append(self._delta_P_PQ[i])
            self.delta_left.append(self._delta_Q_PQ[i])
        for i in range(0, len(self._delta_P_PV)):
            self.delta_left.append(self._delta_P_PV[i])
            self.delta_left.append(self._delta_U_PV[i])


        

    def __gen_J_mat(self):
        self.J = []
        for i, node_i in enumerate(self.infos.Node_infos):
            if node_i["node_type"] == "SLACK":
                continue
            e_i, f_i = 0, 0
            for item in self.init_value:
                if item[0] == (i+1):
                    e_i = item[1]["e"]
                    f_i = item[1]["f"]
                    break
            t1, t2 = [], []
            for j, node_j in enumerate(self.infos.Node_infos):
                if node_j["node_type"] == "SLACK":
                    continue

                H_ii, N_ii, J_ii, L_ii, R_ii, S_ii = 0, 0, 0, 0, 0, 0
                H_ij, N_ij, J_ij, L_ij, R_ij, S_ij = 0, 0, 0, 0, 0, 0
                
                if i == j :
                    for k, item in enumerate(self.init_value):
                        H_ii += self.infos.G[i][k] * item[1]["f"] + self.infos.B[i][k] * item[1]["e"]
                        N_ii += self.infos.G[i][k] * item[1]["e"] - self.infos.B[i][k] * item[1]["f"]
                    J_ii +=  N_ii - self.infos.B[i][i] * self.init_value[i][1]["f"] - self.infos.G[i][i] * self.init_value[i][1]["e"]
                    L_ii += -H_ii + self.infos.G[i][i] * self.init_value[i][1]["f"] - self.infos.B[i][i] * self.init_value[i][1]["e"]
                    H_ii += -self.infos.B[i][i] * self.init_value[i][1]["e"] + self.infos.G[i][i] * self.init_value[i][1]["f"]
                    N_ii +=  self.infos.G[i][i] * self.init_value[i][1]["e"] + self.infos.B[i][i] * self.init_value[i][1]["f"]
                    
                    t1.extend([H_ii, N_ii])
                    
                    if node_i["node_type"] == "PV":
                        R_ii = 2 * self.init_value[i][1]["f"]
                        S_ii = 2 * self.init_value[i][1]["e"]
                        t2.extend([R_ii, S_ii])
                    else:
                        t2.extend([J_ii, L_ii])
                    
                else:
                    H_ij = -self.infos.B[i][j] * e_i + self.infos.G[i][j] * f_i
                    N_ij =  self.infos.G[i][j] * e_i + self.infos.B[i][j] * f_i
                    J_ij = -N_ij
                    L_ij =  H_ij
                    R_ij = 0
                    S_ij = 0

                    t1.extend([H_ij, N_ij])

                    if node_i["node_type"] == "PV":
                        t2.extend([R_ij, S_ij])
                    else:
                        t2.extend([J_ij, L_ij])
            
            self.J.append(t1)
            self.J.append(t2)

    def __correction(self, correction_matrix):
        correction_list = correction_matrix.T.getA()[0]
        precision = 10**-3
        for item in correction_list:
            if abs(item) > precision :
                break
            return True


        slack_node_num = 0
        for i, node in enumerate(self.infos.Node_infos):
            if node["node_type"] == "SLACK":
                slack_node_num = i + 1
                break
        temp = copy.deepcopy(self.init_value)
        flag_slack = False
        for i, item in enumerate(temp):
            if item[0] == slack_node_num:
                flag_slack = True
                continue
            if flag_slack :
                item[1]["f"] += correction_list[2* (i - 1)]
                item[1]["e"] += correction_list[2* (i - 1) + 1]
            else:
                item[1]["f"] += correction_list[2* i]
                item[1]["e"] += correction_list[2* i + 1]
        self.init_value = copy.deepcopy(temp)

        return False


    def start_iteration(self):

        stop_flag = False
        iteration_time = 0

        while not stop_flag:
            iteration_time += 1
            self.__calc_delta_val()
            self.__gen_J_mat()
            J = np.matrix(self.J).I
            dt = np.transpose(np.matrix(self.delta_left))
            correction_value = J * dt
            stop_flag = self.__correction(correction_value)

            if iteration_time > 100000 :
                print("不收敛")
                break

        print("迭代完毕：次数", iteration_time, end="\n")
        for item in self.init_value:
            print("节点: ", item[0], "   电压: ", item[1]["e"], " + j", item[1]["f"], end="\n")
        
        