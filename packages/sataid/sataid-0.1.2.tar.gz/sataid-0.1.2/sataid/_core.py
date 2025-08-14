import numpy as np
from struct import unpack
import re
from ._array import SataidArray

def _header_parser(_stream):
    """Internal function to parse the Sataid file header."""
    _h_block = {}
    _h_block['recl'] = unpack('I', _stream.read(4))
    _h_block['chan'] = unpack('c'*8, _stream.read(8))
    _h_block['sate'] = unpack('c'*8, _stream.read(8))
    _stream.read(4*1) # skip
    _h_block['ftim'] = unpack('I'*8, _stream.read(4*8))
    _h_block['etim'] = unpack('I'*8, _stream.read(4*8))
    _h_block['calb'] = unpack('I'*1, _stream.read(4*1))
    _h_block['fint'] = unpack('I'*2, _stream.read(4*2))
    _h_block['eres'] = unpack('f'*2, _stream.read(4*2))
    _h_block['eint'] = unpack('I'*2, _stream.read(4*2))
    _h_block['nrec'] = unpack('I'*2, _stream.read(4*2))
    _h_block['cord'] = unpack('f'*8, _stream.read(4*8))
    _h_block['ncal'] = unpack('I'*3, _stream.read(4*3))
    _stream.read(1*24) # skip
    _h_block['asat'] = unpack('f'*6, _stream.read(4*6))
    _stream.read(1*32) # skip
    _h_block['vers'] = unpack('c'*4, _stream.read(1*4))
    _stream.read(4*1) # recl
    return _h_block

def _calibration_parser(_stream):
    """Internal function to parse the calibration lookup table."""
    _n_bytes_info = unpack('I'*1, _stream.read(4*1))
    _num_elements = int(_n_bytes_info[0]/4-2)
    _cal_lut = np.array(unpack('f'*_num_elements, _stream.read(4*_num_elements)))
    _stream.read(4*1)
    return _cal_lut

def _data_block_reader(_stream, _rec_info, _dims):
    """Internal function to read the main image data blocks."""
    _img_data = []
    if _rec_info[1] == 2: # 2 Byte data
        for _ in range(_dims[1]):
            _n_bytes_in_rec = unpack('I'*1, _stream.read(4*1))
            _line_buffer = unpack('H'*(_dims[0]), _stream.read(_dims[0]*2))
            _img_data.append(_line_buffer[0:_dims[0]])
            _stream.read(_n_bytes_in_rec[0]-_dims[0]*2-8) # skip padding
            _stream.read(4*1)
    elif _rec_info[1] == 1: # 1 Byte data
        for _ in range(_dims[1]):
            _n_bytes_in_rec = unpack('I'*1, _stream.read(4*1))
            _line_buffer = unpack('B'*((_n_bytes_in_rec[0]-8)), _stream.read(((_n_bytes_in_rec[0]-8))))
            _img_data.append(_line_buffer[0:_dims[0]])
            _stream.read(4*1)
    return np.asarray(_img_data)

def _apply_calibration(_raw_data, _geo_box, _dims, _cal_lut):
    """Internal function to apply calibration and generate coordinates."""
    _y_coords = np.linspace(_geo_box[4], _geo_box[0], _dims[1])
    _x_coords = np.linspace(_geo_box[1], _geo_box[3], _dims[0])
    _calibrated_data = _cal_lut[_raw_data.astype(np.int64) - 1]
    return _y_coords, _x_coords, _calibrated_data

def read_sataid(_fpath):
    """
    Reads a Sataid binary file and returns a SataidArray object.
    The internal logic is complex and optimized for binary stream parsing.
    
    Args:
        _fpath (str): The file path to the Sataid binary file.
        
    Returns:
        SataidArray: An object containing the processed data and metadata.
    """
    with open(_fpath, 'rb') as _stream:
        _header = _header_parser(_stream)
        _cal_table = _calibration_parser(_stream)
        _raw_img = _data_block_reader(_stream, _header['nrec'], _header['eint'])

    _lats, _lons, _data = _apply_calibration(_raw_img, _header['cord'], _header['eint'], _cal_table)

    _channel_name_raw = b"".join(_header['chan']).decode(errors='ignore')
    _channel_match = re.match(r'^[A-Za-z]+', _channel_name_raw)
    _channel_name = _channel_match.group(0) if _channel_match else ''
    
    _units = 'unknown'
    try:
        _idx = SataidArray.ShortName.index(_channel_name)
        if 0 <= _idx <= 6:
            _units = 'Reflectance'
        elif 7 <= _idx <= 15:
            _data = _data - 273.15  # Convert from Kelvin to Celsius
            _units = '°C'
    except ValueError:
        pass

    return SataidArray(
        lats=_lats, lons=_lons, data=_data, sate=_header['sate'], chan=_header['chan'], etim=_header['etim'],
        fint=_header['fint'], asat=_header['asat'], vers=_header['vers'], eint=_header['eint'], 
        cord=_header['cord'], eres=_header['eres'], fname=_fpath, units=_units
    )