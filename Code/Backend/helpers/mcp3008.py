import spidev


class Mcp3008:
    def __init__(self, bus=0, device=0):
        super().__init__()
        self.__bus = bus
        self.__device = device
        self.spi = spidev.SpiDev()
        self.spi.open(self.bus, self.device)
        self.spi.max_speed_hz = 10 ** 5

    @property
    def bus(self):
        return self.__bus

    @property
    def device(self):
        return self.__device

    def read_channel(self, ch):
        result = 1
        kanaalcode = (((result << 3) | ch) << 4)
        bytes_out = (1, kanaalcode, 0)
        bytes_in = self.spi.xfer2(bytes_out)
        # print(bytes_in)
        resultaat = ((bytes_in[1] & 3) << 8) | bytes_in[2]
        return resultaat

    def close(self):
        self.spi.close()