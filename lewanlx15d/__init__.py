from typing import TypeVar, Generic, List, Union, Tuple

def byte_split(i: int) -> Tuple[int, int]:
    lower = i & 0xff
    upper = i >> 8
    return (lower, upper)

R = TypeVar('R')
class Command():
    def message(self) -> List[int]:
        pass

class BulkMove(Command):
    pass

class Move(Command):
    COMMAND_CODE = 3
    "number of servos, lower 8 bits time, upper 8 bits time,servo id,lower angle, higher angle"

    def __init__(self, servo: int, time: int, angle_pos: int):
        if time > 65560 or 0 > time:
            raise "Time value out of bounds [0,65560]"
        if angle_pos > 65560 or 0 > angle_pos:
            raise "Angle value out of bounds [0,65560]"
        self.angle_pos = angle_pos
        pass

    def message(self) -> List[int]:
        return [Move.COMMAND_CODE, 1, *byte_split(self.time), self.servo, *byte_split(self.angle_pos)]


class SerialLike():
    def write(data: bytes) -> None:
        pass
    def read() -> bytes:
        pass

class ServosController():
    HEADER = 0x55
    _port: SerialLike

    def __init__(self, serial: SerialLike):
        self._port = serial

    def run(self, command: Command):
        command_message = command.message()
        message = [Servo.HEADER, Servo.HEADER, len(command_message)+1, command_message]
        self._port.write(message)
