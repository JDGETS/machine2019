import math as m
import numpy as np


class MachineIK:
    def __init__(self):
        '''Set dimension of the arm'''
        self.l1 = 47.18629
        self.l2 = 203.2
        self.l3 = 203.2
        self.l4 = 0
        self.j_offset = m.atan(22.5044 / 201.9554)

    def direct_kinematics(self, j):
        '''Does the direct kinematics of the chain of machine 2018 arm.

        Input :     j: Joint angles of the arm '[j1, j2, j3, j4]'

        Output :    dh: Homogen matrix of the arm
        '''
        '''Rotation and translation for X axis'''
        nx = m.cos(j[0]) * m.cos(j[1] + j[2] + j[3])
        ox = -m.cos(j[0]) * m.cos(j[1] + j[2] + j[3])
        ax = m.sin(j[0])
        px = -m.cos(j[0]) * (self.l2 * m.sin(j[1]) - self.l3 * m.cos(j[1] + j[2]) - self.l4 * m.cos(j[1] + j[2] + j[3]))
        '''Rotation and translation for Y axis'''
        ny = m.sin(j[0]) * m.cos(j[1] + j[2] + j[3])
        oy = -m.sin(j[0]) * m.sin(j[1] + j[2] + j[3])
        ay = -m.cos(j[0])
        py = -m.sin(j[0]) * (self.l2 * m.sin(j[1]) - self.l3 * m.cos(j[1] + j[2]) - self.l4 * m.cos(j[1] + j[2] + j[3]))
        '''Rotation and translation for Z axis'''
        nz = m.sin(j[1] + j[2] + j[3])
        oz = m.cos(j[1] + j[2] + j[3])
        az = 0
        pz = self.l1 + self.l2 * m.cos(j[1]) + self.l3 * m.sin(j[1] + j[2]) + self.l4 * m.sin(j[1] + j[2] + j[3])
        '''Assemble dh matrix'''
        dh = [[nx, ox, ax, px],
              [ny, oy, ay, py],
              [nz, oz, az, pz],
              [0, 0, 0, 1]]

        return dh

    def inverse_kinematics(self, mat):
        '''Does the inverse kinematics of the chain of machine 2018 arm.
        Input:  dh: matrix of desired position      [[nx, ox, ax, px],
                                                     [ny, oy, ay, py],
                                                     [nz, oz, az, pz],
                                                     [0,   0,  0,  1]]

        Output: j: Joints angles of the arm'[j1, j2, j3, j4]'
        '''
        j = [0, 0, 0, 0]
        h_outil = np.array([[1, 0, 0, 0],
                            [0, 1, 0, 0],
                            [0, 0, 1, 0],
                            [0, 0, 0, 1]])
        mat = np.array(mat)
        mat = np.dot(mat, np.linalg.inv(h_outil))
        nx = mat[0][0]
        ny = mat[1][0]
        nz = mat[2][0]
        ox = mat[0][1]
        oy = mat[1][1]
        oz = mat[2][1]
        px = mat[0][3]
        py = mat[1][3]
        pz = mat[2][3]

        j234 = round(m.atan2(nz, oz), 6)

        '''Theta 1'''
        j[0] = m.atan2(py, px)
        '''Theta 3'''
        d = m.sqrt(m.pow(px, 2) + m.pow(py, 2) + m.pow(pz - self.l1, 2))
        phi = m.acos((m.pow(self.l2, 2) + m.pow(self.l3, 2) - m.pow(d, 2)) / (2 * self.l2 * self.l3))
        j[2] = round(phi - m.pi / 2, 6)
        '''Theta 2'''
        phi2 = m.acos((m.pow(self.l2, 2) + m.pow(d, 2) - m.pow(self.l3, 2)) / (2 * self.l2 * d))
        phi3 = m.asin((pz - self.l1) / d)
        j[1] = round(phi2 + phi3 - m.pi / 2, 6)
        '''Theta 4'''
        j[3] = j234 - j[1] - j[2]

        return j

    def jacobian(self, t, j):
        '''Does the jacobian matrix of the chain of machine 2018 arm
        Input:  t: Speed vector [x, y, z, wx, wy, wz]
                    [x, y, z] is translation speed (mm/s)
                    [wx, wy, wz] is rotation speed (rad/s)
                j: starting joints angles of the arm'[j1, j2, j3, j4]'

        Output: Rotational speed for the 4 joints '[q1, q2, q3, q4] (rad/s)
        '''
        '''Linear contribution of joints #1'''
        jl10 = m.sin(j[0]) * (
            self.l2 * m.sin(j[1]) - self.l3 * m.cos(j[1] + j[2]) - self.l4 * m.cos(j[1] + j[2] + j[3]))
        jl11 = -m.cos(j[0]) * (
            self.l2 * m.sin(j[1]) - self.l3 * m.cos(j[1] + j[2]) - self.l4 * m.cos(j[1] + j[2] + j[3]))
        jl12 = 0
        '''Linear contribution of joints #2'''
        jl20 = -m.cos(j[0]) * (
            self.l2 * m.cos(j[1]) + self.l3 * m.sin(j[1] + j[2]) + self.l4 * m.sin(j[1] + j[2] + j[3]))
        jl21 = -m.sin(j[0]) * (
            self.l2 * m.cos(j[1]) + self.l3 * m.sin(j[1] + j[2]) + self.l4 * m.sin(j[1] + j[2] + j[3]))
        jl22 = -(self.l2 * m.sin(j[1]) - self.l3 * m.cos(j[1] + j[2]) - self.l4 * m.cos(j[1] + j[2] + j[3]))
        '''Linear contribution of joints #3'''
        jl30 = -m.cos(j[0]) * (self.l3 * m.sin(j[1] + j[2]) + self.l4 * m.sin(j[1] + j[2] + j[3]))
        jl31 = -m.sin(j[0]) * (self.l3 * m.sin(j[1] + j[2]) + self.l4 * m.sin(j[1] + j[2] + j[3]))
        jl32 = self.l3 * m.cos(j[1] + j[2]) + self.l4 * m.cos(j[1] + j[2] + j[3])
        '''Linear contribution of joints #4'''
        jl40 = -self.l4 * m.sin(j[1] + j[2] + j[3]) * m.cos(j[0])
        jl41 = -self.l4 * m.sin(j[1] + j[2] + j[3]) * m.sin(j[0])
        jl42 = self.l4 * m.cos(j[1] + j[2] + j[3])
        '''Angle contribution of joints #1'''
        ja10 = 0
        ja11 = 0
        ja12 = 1
        '''Angle contribution of joints #2'''
        ja20 = m.sin(j[0])
        ja21 = -m.cos(j[0])
        ja22 = 0
        '''Angle contribution of joints #3'''
        ja30 = m.sin(j[0])
        ja31 = -m.cos(j[0])
        ja32 = 0
        '''Angle contribution of joints #4'''
        ja40 = m.sin(j[0])
        ja41 = -m.cos(j[0])
        ja42 = 0
        '''Jacobian matrix of all rotation and translation contributions of all axis'''
        ja = np.array([[jl10, jl20, jl30, jl40],
                       [jl11, jl21, jl31, jl41],
                       [jl12, jl22, jl32, jl42],
                       [ja10, ja20, ja30, ja40],
                       [ja11, ja21, ja31, ja41],
                       [ja12, ja22, ja32, ja42]])
        '''Transpose t matrix'''
        t = np.transpose(np.array(t))
        '''Multiply pseudo inverse of <ja> to <t>'''
        q = np.dot(np.linalg.pinv(ja), t)

        return abs(q)

    def get_spd_lin(self, start_pos, end_pos, spd):
        '''Get speed vector for linear move with no specific angular speed
        Input:
                start_pos: starting position of the movement (DH)
                end_pos: end position of the movement (DH)
                spd: linear speed required

        Output: Speed vector [vx, vy, vz, wx = 0, wy = 0, wz = 0]
        '''
        '''get unit vector'''
        dx = end_pos[0] - start_pos[0]
        dy = end_pos[1] - start_pos[1]
        dz = end_pos[2] - start_pos[2]
        dp = m.sqrt(m.pow(dx, 2) + m.pow(dy, 2) + m.pow(dz, 2))
        ux = dx / dp
        uy = dy / dp
        uz = dz / dp
        '''get speed vector'''
        vx = ux * spd
        vy = uy * spd
        vz = uz * spd

        j_spd = self.jacobian([vx, vy, vz, 0, 0, 0], self.inverse_kinematics(self.pos_to_dh(start_pos)))

        return [1 if s < 1 else s for s in j_spd]

    def get_spd_joint(self, start_joint, end_joint, spd):
        '''Get angular speed of all joints for a synchronous joint movement
        Input:
                start_pos: starting position of the movement (joints)
                end_pos: end position of the movement (joints)
                spd: max angular speed (rad/s)

        Output: Rotational speed for the 4 joints '[q1, q2, q3, q4] (rad/s)
        '''
        '''get max angle difference'''
        angle_max = float(max(
            [abs(end_joint[0] - start_joint[0]), abs(end_joint[1] - start_joint[1]), abs(end_joint[2] - start_joint[2]),
             abs(end_joint[3] - start_joint[3])]))
        '''get joints speed'''
        j1_spd = (abs(end_joint[0] - start_joint[0]) / angle_max) * spd
        j2_spd = (abs(end_joint[1] - start_joint[1]) / angle_max) * spd
        j3_spd = (abs(end_joint[2] - start_joint[2]) / angle_max) * spd
        j4_spd = (abs(end_joint[3] - start_joint[3]) / angle_max) * spd

        j_spd = [j1_spd, j2_spd, j3_spd, j4_spd]

        return j_spd

    def pos_to_dh(self, pos):
        r11 = m.cos(pos[5]) * m.cos(pos[4])
        r12 = m.cos(pos[5]) * m.sin(pos[4]) * m.sin(pos[3]) - m.sin(pos[5]) * m.cos(pos[3])
        r13 = m.cos(pos[5]) * m.sin(pos[4]) * m.cos(pos[3]) + m.sin(pos[5]) * m.sin(pos[3])

        r21 = m.sin(pos[5]) * m.cos(pos[4])
        r22 = m.sin(pos[5]) * m.sin(pos[4]) * m.sin(pos[3]) + m.cos(pos[5]) * m.cos(pos[3])
        r23 = m.sin(pos[5]) * m.sin(pos[4]) * m.cos(pos[3]) - m.cos(pos[5]) * m.sin(pos[3])

        r31 = -m.sin(pos[4])
        r32 = m.cos(pos[4]) * m.sin(pos[3])
        r33 = m.cos(pos[4]) * m.cos(pos[3])

        return [[r11, r12, r13, pos[0]],
                [r21, r22, r23, pos[1]],
                [r31, r32, r33, pos[2]],
                [0, 0, 0, 1]]

    def dh_to_pos(self, dh):
        roll = m.atan2(dh[1][2], dh[2][2])
        pitch = m.atan2(-dh[0][2], m.sqrt(m.pow(dh[1][2], 2) + m.pow(dh[2][2], 2)))
        yaw = m.atan2(dh[0][1], dh[0][0])

        return [dh[0][3], dh[1][3], dh[2][3], roll, pitch, yaw]

    def radchain_to_motor(self, rad, offset=True):
        offset = m.pi if offset is True else 0
        newrad = rad - offset
        if newrad < 0:
            newrad += m.pi * 2
        elif newrad > m.pi * 2:
            newrad -= m.pi * 2
        return newrad

    def motor_to_chain(self, j):
        i = [0, 0, 0, 0]
        b_off = 147.0 / 360.0 * 2.0 * m.pi
        '''Substract offset for j2 and j3'''
        i[0] = self.radmotor_to_chain(j[0] - b_off, offset=False)
        i[1] = self.radmotor_to_chain(j[1] - self.j_offset)
        i[2] = self.radmotor_to_chain(j[2] + self.j_offset)
        i[3] = self.radmotor_to_chain(j[3])

        return i

    def radmotor_to_chain(self, rad, offset=True):
        offset = m.pi if offset is True else 0
        newrad = rad + offset
        if newrad < 0:
            newrad += m.pi * 2
        elif newrad > m.pi * 2:
            newrad -= m.pi * 2
        return newrad

    def chain_to_motor(self, j):
        i = [0, 0, 0, 0]
        '''Substract offset for j2 and j3'''
        b_off = 147.0 / 360.0 * 2.0 * m.pi
        i[0] = self.radchain_to_motor(j[0] + b_off, offset=False)
        i[1] = self.radchain_to_motor(j[1] + self.j_offset)
        i[2] = self.radchain_to_motor(j[2] - self.j_offset)
        i[3] = self.radchain_to_motor(j[3])

        return i


if __name__ == "__main__":
    mik = MachineIK()

    mik.jacobian([0, 0, 30, 0, 0, 0], [0.578, 0.3, 0.1, m.pi / 4])

    mik.get_spd_lin([200, 0, 40, 0, 0, 0], [200, 0, 60, 0, 0, 0], 30)

    target2 = mik.direct_kinematics([0, 0, -m.pi / 4, 0])

    mik.inverse_kinematics(target2)
