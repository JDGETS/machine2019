from threading import Thread

class TyroManager(Thread):
    DETENDRE_SPEED = 700
    TENDRE_SPEED = 600

    def __init__(self, chain, motor_id=8):
        Thread.__init__(self)
        self.state = 'detendre'
        self.running = True
        self.chain = chain
        self.motor_id = motor_id
        self.speed = 512
        self.moving = False
        self.start_time = 0


    def run(self):
        self.chain.set_reg(self.motor_id, 'cw_angle_limit', 0)
        self.chain.set_reg(self.motor_id, 'ccw_angle_limit', 0)

        while self.running:
            if self.state == 'detendre':
                self.detendre()
            elif self.state == 'tendre':
                self.tendre()
            else:
                pass

            time.sleep(0.1)

    def detendre(self):
        load = self.chain.get_reg(self.motor_id, 'present_load')
        direction = load >> 10
        load = load % 1023

        if load >= 10:
            self.chain.set_reg(self.motor_id, 'moving_speed', self.DETENDRE_SPEED)
            time.sleep(1)

            self.chain.set_reg(self.motor_id, 'moving_speed', 0)
            time.sleep(0.2)

    def tendre(self):
        speed = self.chain.get_reg(self.motor_id, 'present_speed')
        direction = (speed >> 10) & 1
        speed = speed & 1023
        speed = (2 * direction - 1) * speed * 0.111

        if not self.moving:
            self.start_time = time.time()
            self.moving = True
            self.chain.set_reg(self.motor_id, 'moving_speed', self.TENDRE_SPEED + 1024)

        if (time.time() - self.start_time) > 0.2 and speed <= 40:
            self.state = 'manuel'
            self.moving = False
            self.chain.set_reg(self.motor_id, 'moving_speed', 0)
