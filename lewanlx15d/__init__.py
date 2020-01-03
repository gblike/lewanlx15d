from typing import TypeVar, Generic, List, Union, Tuple

def byte_split(i: int) -> Tuple[int, int]:
    lower = i & 0xff
    upper = i >> 8
    return (lower, upper)

R = TypeVar('R')
class Command():
    def message(self) -> List[int]:
        pass

class ServoAngle:
    servo: int
    angle: int

    def __init__(self, servo: int, angle: int):
        if angle > 65560 or 0 > angle:
            raise "Angle value out of bounds [0,65560]"
        self.servo = servo
        self.angle = angle

class Move(Command):
    COMMAND_CODE = 3
    moves: List[ServoAngle]
    time: int
    def __init__(self, time, *moves: List[ServoAngle]):
        if time > 65560 or 0 > time:
            raise "Time value out of bounds [0,65560]"
        self.time = time
        self.moves = moves

    def message(self):
        params = [[move.servo, *byte_split(move.angle)] for move in self.moves]
        flattened = [byte for group in params for byte in group]
        return [Move.COMMAND_CODE, len(self.moves), *byte_split(self.time), *flattened]


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
        message = [ServosController.HEADER, ServosController.HEADER,
                   len(command_message)+1,
                   command_message]
        self._port.write(message)
