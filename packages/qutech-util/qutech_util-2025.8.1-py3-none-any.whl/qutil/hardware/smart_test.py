"""This module contains the SmartTest class which you can use to communicate with the leak tester."""
import argparse
import logging
import time
from datetime import datetime

import serial

from qutil.io import CsvLogger

__all__ = ["SmartTest"]

logger = logging.getLogger('smart_test')


class CheckSumError(ValueError):
    pass


def calc_checksum(msg):
    return b'%03i' % (sum(msg)%256)


def to_valid_message(msg: bytes):
    return msg + calc_checksum(msg) + b'\r'


def parse_data(data: bytes, fmt: str):
    if fmt in ('boolean_old', 0):
        assert data in (b'0'*6, b'1'*6)
        return bool(int(data))
    
    if fmt in ('u_integer', 1):
        assert len(data) == 6
        return int(data)
    
    if fmt in ('u_real', 2):
        assert len(data) == 6
        return int(data) / 100
    
    if fmt in ('string', 4):
        assert len(data) == 6
        return data.decode('ascii')
    
    if fmt in ('boolean_new', 6):
        assert len(data) == 1
        return bool(int(data))
    
    if fmt in ('u_short_int', 7):
        assert len(data) == 3
        return int(data)
    
    if fmt in ('u_expo_new', 10):
        assert len(data) == 6
        mantissa = data[:4].decode()
        exponent = str(int(data[4:]) - 20 - 3)
        # use parsing logic for most exact result
        return float(f'{mantissa}E{exponent}')
        
    if fmt in ('string16', 11):
        assert len(data) == 16
        return data.decode()
    
    raise KeyError('unknown format argument for parsing', data, fmt)


def encode_data(value, fmt: str) -> bytes:
    if fmt in ('boolean_old', 0):
        assert value in (True, False, 0, 1)
        return 6*b'1' if value else 6*b'0'
    
    if fmt in ('u_integer', 1):
        assert value < 1000000 and value >= 0
        return b'%06u' % value
    
    if fmt in ('u_real', 2):
        assert value >= 0 and value < 10000
        return (b'%07.2f' % value).replace(b'.', b'')
    
    if fmt in ('string', 4):
        assert len(value) == 4
        return value.encode('ascii')
    
    if fmt in ('boolean_new', 6):
        assert value in (True, False, 0, 1)
        return b'1' if value else b'0'
    
    if fmt in ('u_short_int', 7):
        assert value >= 0 and value < 1000
        return b'%03u' % value
    
    if fmt in ('u_expo_new', 10):
        assert value >= 0
        str_repr = (b'%.3E' % value)
        mantissa, exponent = str_repr.replace(b'.', b'').split(b'E')
        exponent = int(exponent) + 20
        assert exponent >= 0 and exponent < 100
        
        return mantissa + b'%02u' % exponent
        
    if fmt in ('string16', 11):
        assert len(value) == 16
        return value.encode('ascii')
    
    raise KeyError('unknown format argument for parsing', value, fmt)
    

def parse_msg(msg: bytes, fmt: str):
    addr = msg[:3]
    logger.debug('parsing message from %r', addr)
    
    action = msg[3:5]
    param_num = int(msg[5:8])
    data_len = int(msg[8:10])
    
    data = msg[10:10+data_len]
    
    expected_check_sum = calc_checksum(msg[:10+data_len])
    
    check_sum = msg[10+data_len:10+data_len+3]
    
    if expected_check_sum != check_sum:
        raise CheckSumError(msg)
    return action, param_num, parse_data(data, fmt)


class SmartTest:
    """Talk to PfeifferVacuum leak tester via serial interface (USB serial adapter).
    
    Currently only get_leakrate_mbarls is implemented as a method but you can easily extend this to other get methods using
    the parameter number and the value format from the manual. For setting something you need to implement set method with the action b'10'
    """
    def __init__(self, device: str, address: int):
        assert address < 1000
        self.device = device
        self.address = b'%03i' % address

    def query(self, param_number: int, fmt):
        param_b = b'%03i' % param_number
        
        msg = self.address + b'00' + param_b + b'02' + b'=?'
        query = to_valid_message(msg)
        
        with serial.Serial(self.device) as ser:
            ser.write(query)
            answer = ser.read_until(b'\r')
        
        action, param_num, value = parse_msg(answer, fmt)
        logger.info('received: %r', (action, param_num, value))
        assert action == b'10'
        assert param_num == param_number, "%u != %u" % (param_num, param_number)
        return value
    
    def get_leakrate_mbarls(self) -> float:
        return self.query(670, 'u_expo_new')


def periodically_log_leak_rate(filename, period, device, address):
    leak_detector = SmartTest(device, address)
    csv_logger = CsvLogger(filename, ['Time', 'Leakrate(mbar x l/s)'])

    while True:
        leakrate = leak_detector.get_leakrate_mbarls()
        current_time = datetime.now()

        csv_logger.write('%s' % current_time, '%.4e' % leakrate)
    
        print(f'Current leakrate {leakrate:.4e} pausing for {period:f} sec.', end='\r')
        time.sleep(period)


default_prefix = '%Y_%m_%d_%H_%M_%S_'

parser = argparse.ArgumentParser(description='Periodically log the leak rate to the given file as tab-separated values.',
                                 formatter_class=argparse.ArgumentDefaultsHelpFormatter)
parser.add_argument('--filename', default='smart_test_fast.log', help='Filename of log file. By default prefixed by a date/time string.')
parser.add_argument('--period', default=1., type=float, help='Wait time between read-outs')
parser.add_argument('--device', default='/dev/ttyUSB0', help='Device path')
parser.add_argument('--address', default=1, type=int, help='See SmartTester settings')
parser.add_argument('--no-date-prefix', action='store_true', help='Omit the default %s prefix' % default_prefix.replace('%', '%%'))


def main():
    args = vars(parser.parse_args())

    filename = args.pop('filename')
    if not args.pop('no_date_prefix'):
        filename = datetime.now().strftime(default_prefix) + filename
    
    periodically_log_leak_rate(filename=filename, **args)


if __name__ == '__main__':
    main()
