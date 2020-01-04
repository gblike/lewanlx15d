from typing import TypeVar, Generic, List, Union, Tuple, Sequence, Any, Iterable

def byte_split(i: int) -> Tuple[int, int]:
    lower = i & 0xff
    upper = i >> 8
    return (lower, upper)

def byte_merge(lower: int, upper: int) -> int:
    return lower | (upper << 8)

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

    def __repr__(self):
        return f"Servo({self.servo}, {self.angle})"

    def __eq__(self, other):
        return self.servo == other.servo and self.angle == other.angle

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

class ReadServoPositions(Command):
    COMMAND_CODE = 21
    servos: List[int]
    def __init__(self, *servos: List[int]):
        self.servos = servos

    def message(self):
        return [ReadServoPositions.COMMAND_CODE, len(self.servos), *self.servos]

def parse_output(input_stream: Iterable[Any]) -> Sequence[Any]:
    header_seek = [0, 0]
    stream = iter(input_stream)
    while True:
        byte = next(stream)
        if header_seek == [ServosController.HEADER, ServosController.HEADER]:
            length = byte
            command_buffer = []
            for i in range(length - 1):
                command_buffer.append(next(stream))
            yield read_command(command_buffer)
            header_seek = [0, 0]
        else:
            header_seek.pop(0)
            header_seek.append(byte)

def read_serial(dev):
    buf = b''
    while True:
        # magic 23 just to read all the servos' positions
        # todo properly stream in the data
        datum = dev.read(23, 10)
        if datum == b'':
            return buf
        else:
           buf += datum

def read_command(command_buffer):
    command = command_buffer[0]
    length = command_buffer[1]
    params = command_buffer[2:]
    if command == 0x15: # Multiple Servo Read Position
        output = []
        for i in range(length):
            servo, lower, higher = params[i * 3: (i * 3) + 3]
            output.append(ServoAngle(servo, byte_merge(lower, higher)))
        return output
    else:
        raise ValueError(f"Command not recognized {command}")


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
                   *command_message]

        return message
