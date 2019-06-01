import RPi.GPIO as GPIO
import smbus
import math
import sys
import time
from QRPosition import qr_extractor as Position
import cv2
import pi_code

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)


# GPIO pin number
# DC_Motor pins
pin_dc1 = 23	# DC_Motor_A pin1
pin_dc2 = 24    # DC_Motor_A pin2
pin_dc3 = 22    # DC_Motor_B pin3
pin_dc4 = 27    # DC_Motor_B pin4

# Ultra_Sensor pins
pin_ultra_trig = 2   # trig pin (GPIO 2)
pin_ultra_echo = 3   # echo pin (GPIO 3)

# Set DC_Motor pins as OUTPUT
GPIO.setup(pin_dc1, GPIO.OUT)
GPIO.setup(pin_dc2, GPIO.OUT)
GPIO.setup(pin_dc3, GPIO.OUT)
GPIO.setup(pin_dc4, GPIO.OUT)

# Set Ultra_Sensor pins
GPIO.setup(pin_ultra_trig, GPIO.OUT)
GPIO.setup(pin_ultra_echo. GPIO.IN)

# Set Power Management registers
power_mgmt_1 = 0x6b
power_mgmt_2 = 0x6c

######### Settings for DC_Motor #########

pwm1 = GPIO.PWM(pin_dc1, 100)		# GPIO.PWM([pin],[frequency])
pwm2 = GPIO.PWM(pin_dc2, 100)		# GPIO.PWM([pin],[frequency])
pwm3 = GPIO.PWM(pin_dc3, 100)		# GPIO.PWM([pin],[frequency])
pwm4 = GPIO.PWM(pin_dc4, 100)		# GPIO.PWM([pin],[frequency])

#########################################


######## Setting for IMU Sensors ########

bus = smbus.SMBus(1)    # or bus = smbus.SMBus(1) for Revision 2 boards
address = 0x68          # This is the address value read via the i2cdetect command
                        # To detect the address value, execute command below in terminal
                        # $ sudo i2cdetect -y 1

# Now make the 6050 up as it starts in sleep mode
# bus.write_byte_data(address, power_mgmt_1, 0)

################################################
BUSY = False
READY = True
FORWARD = 2
ROTATE = 3
WAIT = 4
ROTATE_FORWARD = 5
ROTATE_FORWARD_PUTDOWN = 6

def read_word(adr):
    high = bus.read_byte_data(address, adr)
    low = bus.read_byte_data(address, adr+1)
    val = (high << 8) + low
    return val

def read_word_2c(adr):
    val = read_word(adr)
    if (val >= 0x8000):
        return -((65535 - val) + 1)
    else:
        return val

def get_y_rotation(x,y,z):
    radians = math.atan2(x, dist(y,z))
    return -math.degrees(radians)

def get_x_rotation(x,y,z):
    radians = math.atan2(y, dist(x,z))
    return math.degrees(radians)

#########################################



###### Functions to control RC_CAR ######

class RC_CAR():

    def __init__(self):
        print('Ready!!')

        """
        self.state = 0
        self.velocity = 0
        self.accel_raw_x = np.zeros([1,10])
        self.accel_raw_y = np.zeros([1,10])
        self.accel_raw_z = np.zeros([1,10])
        self.gyro_raw_x = np.zeros([1,10])
        self.gyro_raw_y = np.zeros([1,10])
        self.gyro_raw_z = np.zeros([1,10])

        self.accel_x = 0
        self.accel_y = 0
        self.accel_z = 0
        self.gyro_x = 0
        self.gyro_y = 0
        self.gyro_z = 0
        """

    def forward(self, speed):

        print('forward')

        pwm2.stop()
        pwm4.stop()
        pwm1.start(speed)
        pwm3.start(speed)

    def stop(self):

        print('stop')

        pwm1.stop()
        pwm2.stop()
        pwm3.stop()
        pwm4.stop()

    def backward(self, speed):

        print('backward')

        pwm1.stop()
        pwm3.stop()
        pwm2.start(speed)
        pwm4.start(speed)

    def right(self):

        print('right')

        pwm2.stop()
        pwm4.stop()
        pwm1.start(50)
        pwm3.start(100)

    def left(self):

        print('left')

        pwm2.stop()
        pwm4.stop()
        pwm1.start(100)
        pwm3.start(50)

    def speed_up(self, speed):

        print('speed up')

        pwm2.stop()
        pwm4.stop()
        pwm1.ChangeDutyCycle(speed)
        pwm3.ChangeDutyCycle(speed)
		
    def slow_down(self, speed):

        print('slow_down')

        pwm2.stop()
        pwm4.stop()
        pwm1.ChangeDutyCycle(speed)
        pwm3.ChangeDutyCycle(speed)

    def ir_detect(self, pin)
        input_state = GPIO.input(pin)
        if input_state == True:
            print("Detected")
            return True

    def ultra_detect(self, pin_ultra_trig, pin_ultra_echo)
        GPIO.output(pin_ultra_trig, False)
        time.sleep(0.5)

        GPIO.output(pin_ultra_trig, True)
        time.sleep(0.0001)
        GPIO.output(pin_ultra_trig, False)

        while GPIO.input(pin_ultra_echo) == 0:
            pulse_start = time.time()

        while GPIO.input(pin_ultra_echo) == 1:
            pulse_end = time.time()

        pulse_duration = pulse_end - pulse_start
        distance = pulse_duration * 17000
        distance = round(distance, 2)

        # print("distance: ", distance, "cm")
        return distance

    def get_imu(self)

        # Get GYRO value
        gyro_raw_xout = read_word_2c(0x43)
        gyro_raw_yout = read_word_2c(0x45)
        gyro_raw_zout = read_word_2c(0x47)
        gyro_xout = gyro_raw_xout / 131
        gyro_yout = gyro_raw_yout / 131
        gyro_zout = gyro_raw_zout / 131


        # Get ACCEL value
        accel_xout = read_word_2c(0x3b)
        accel_yout = read_word_2c(0x3d)
        accel_zout = read_word_2c(0x3f)
        accel_xout_scaled = accel_xout / 16384.0
        accel_yout_scaled = accel_yout / 16384.0
        accel_zout_scaled = accel_zout / 16384.0

        x_rotation = get_x_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)
        y_rotation = get_y_rotation(accel_xout_scaled, accel_yout_scaled, accel_zout_scaled)

        return gyro_xout, gyro_yout, gyro_zout, accel_xout_scaled, accel_yout_scaled, accel_zout_scaled, x_rotation, y_rotation

#########################################

############# MAIN FUNCTION #############

if __name__ == "__main__":

    RC_CAR = RC_CAR()    # Call the class
    cap = cv2.VideoCapture(1)
    AGV = pi_code.pi_car
    try:
        while True:
            _, frame = cap.read()
            angle1, angle2, qrposi = Position.extract(frame, True)
            AGV.receive_cmd()
            ####################  positioning  #######################
            if (angle1, angle2 != 0):

            # forward
            if AGV.cmd == 2 :
                RC_CAR.forward(50)
                time.sleep(1)
                # forward until the qr is not detected
                while (angle1, angle2 != 0):
                    RC_CAR.forward(50)

            """
            if(RC_CAR.ir_detect(pin_ir_left) == True):
                while (RC_CAR.ir_detect(pin_ir_middle) == False):
                    RC_CAR.left()
            elif(RC_CAR.ir_detect(pin_ir_right) == True):
                while (RC_CAR.ir_detect(pin_ir_middle) == False):
                    RC_CAR.right()
            else:
                RC_CAR.forward(50)
                time.sleep(0.01)
            """
    except KeyboardInterrupt:
        GPIO.cleanup()
        sys.exit()

#########################################