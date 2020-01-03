from lewanlx15d import *
import unittest

# Protocol from LSC Series Servo Controller Communication Protocol V1.2.pdf
# Obtained from http://www.lewansoul.com/uploads/attachment/20180703/0f87f15dc7088edb4e18f755ad61de6f.zip

class TestLewanlx15d(unittest.TestCase):
    def test_header(self):
        pass
        #message = [0x01,0x01]
        #self.assertEqual(message[0:2], [0x55,0x55])

    def test_move_message(self):
        # Control the No.1 servo to turn to 2000 position within 1000ms
        move = Move(1000, ServoAngle(1, 2000))
        self.assertEqual([0x03,0x01,0xE8,0x03,0x01,0xD0,0x07], move.message())


    def test_bulk_move_message(self):
        # Control No. 2 servo turn to 1200 position,
        # and No. 9 servo turn to 2300 position within 800ms
        move = Move(800, ServoAngle(2, 1200), ServoAngle(9, 2300))
        expected = [0x03, 0x02, 0x20, 0x03, 0x02, 0xB0, 0x04, 0x09, 0xFC, 0x08]
        self.assertEqual(expected, move.message())

    def test_action_group_run(self):
        # Control the No. 8 action group to run once
        expected = [0x55, 0x55, 0x05, 0x06, 0x08, 0x01, 0x00]
        # Control the No. 2 action group to run unlimited times
        expected = [0x55, 0x55, 0x05, 0x06, 0x02, 0x00, 0x00]

    def test_action_stop(self):
        # Stop the running action group
        expected = [0x55, 0x55, 0x02, 0x07]

    def test_action_speed(self):
        # Control No. 8 action group runs at 50% speed
        expected = [0x55, 0x55, 0x05, 0x0B, 0x08, 0x32, 0x00]

        # The servo controller has downloaded several action groups,
        # and wants to adjust the speed of all the action groups to 3
        # times the original, this is 300%
        expected = [0x55, 0x55, 0x05, 0x0B, 0xFF, 0x2C, 0x01]

    def test_get_battery_voltage(self):
        # Get servo controller's battery voltage in unit millivolts.
        expected = [0x55, 0x55, 0x02, 0x0F]

        # Returns 7500mV 0x4c | (0x1d << 8)
        returned = [0x55, 0x55, 0x04, 0x0F, 0x4C, 0x1D]

    def test_multiple_servo_unload(self):
        # Power off servo No. 1, No. 2, No. 3 and their motors
        expected = [0x55, 0x55, 0x06, 0x14, 0x03, 0x01, 0x02, 0x03]

        # Power off servo No. 1, No. 2, No. 3, No. 4, No. 5, No. 6 and their motors
        expected = [0x55, 0x55, 0x09, 0x14, 0x06, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]

    def test_multiple_servo_read_pos(self):
        # Read the angle position values of servo No. 1, No. 2, No. 3, No. 4, No. 5, No. 6
        expected = [0x55, 0x55, 0x09, 0x15, 0x06, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06]

        # All returned angle position values are 500
        returned = [0x55, 0x55, 0x15, 0x15, 0x06,
                    0x01, 0x01, 0x0F4,
                    0x02, 0x02, 0x0F4,
                    0x03, 0x02, 0x0F4,
                    0x04, 0x02, 0x0F4,
                    0x05, 0x02, 0x0F4,
                    0x06, 0x02, 0x0F4]

    def test_action_group_run_response(self):
        # When the No. 8 action group is running and the number of times is 1
        response = [0x55, 0x55, 0x05, 0x06, 0x08, 0x01, 0x00]
        # the number of the running action group
        # the lower 8 bits of running times of action group
        # the higher 8 bits

    def test_action_group_stop_response(self):
        # The data is returned when a running action is forced to terminate
        response = [0x55, 0x55, 0x02, 0x07]

    def test_action_group_complete_response(self):
        # When running times of No. 8 action group is 1, after the end
        # of the natural running, the data returned by the servo controller
        # to the user is
        response = [0x55, 0x55, 0x05, 0x08, 0x08, 0x01, 0x00]
