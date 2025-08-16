'''
this module is responsible for the creation and reading of kisa-tokens

each token follows the following structure

[head]
    signature [4 bytes]
    expiry [seconds since epoch, 5 bytes, big endian]
    random seed [8 bytes]
    length of the serialized-payload [4 bytes, big endian]
[body]
    JSON-serialized data/payload
[checksum] 
    2 bytes, big endian
'''
import time
import os
from typing import Any

from kisa_utils.storage import encodeJSON, decodeJSON
from kisa_utils.encryption import xor

__VERSIONS = {
    'v1': {
        'signature': bytearray([95, 254, 215, 210]),
    }
}

def __calculateNewCheckSumFromToken(data: bytearray) -> int:
    '''
        takes in the full token including the checksum it has but has to calculate
        the new checksum without including the checksum it already has
    '''
    checksum = 0
    for index in range(len(data)-2):
        checksum += data[index] * (index**2)

    return (checksum % 0xffff)

def __calculateCheckSum(data: bytearray) -> int:
    '''
        Parameters:
            data (bytearray): the bytearray containing the head, payload
        Returns:
            checksum (int): this is the result of the mathematical calculation 
        Calculate the checksum by finding the total sumation of multiplying the byte
            value by the position sqaured
        The function calculates the checksum of the head, payload without a checksum value included
    '''
    checksum = 0
    for index in range(len(data)):
        checksum += data[index] * (index**2)

    return (checksum % 0xffff)

def __encrypt(data: bytearray, version:str) -> None:
    '''
    this function attempts to encrypt the data bytearray IN-PLACE

    @param data: the byte array to be encrypted
    @param `version`: the token version to use. leave this the fuck alone if you dont know what you're doing
    '''

    assert version in __VERSIONS,f'unknown version {version}'

    if 'v1'==version:
        keyStartIndex = 9
        key = data[keyStartIndex : keyStartIndex+8]

        xor(data,key,0, keyStartIndex-1)
        xor(data,key,keyStartIndex+len(key), -1)

def __decrypt(data: bytearray, version:str) -> None:
    '''
    this function attempts to decrypt the data bytearray IN-PLACE

    @param data: the byte array to be encrypted
    @param `version`: the token version to use. leave this the fuck alone if you dont know what you're doing
    '''

    assert version in __VERSIONS,f'unknown version {version}'

    if 'v1'==version:
        keyStartIndex = 9
        key = data[keyStartIndex : keyStartIndex+8]

        xor(data,key,0, keyStartIndex-1)
        xor(data,key,keyStartIndex+len(key), -1)

def __createByteArrayFromPayload(jsonString: str) -> bytearray:
    '''
    This function takes in a serialzed json string and returns a byte array 
    of the serialized json object
    Args:
        jsonString (str) : searialized string of the json payload
    '''
    _byteArray = bytearray()
    _byteArray.extend(jsonString.encode('utf-8'))
    return _byteArray

def __create(jsonString: str, signature: bytearray, expiryTime: int) -> bytearray:
    '''
        Args:
            jsonString (str): json serialized string of the payload
            signature (bytearray): bytearray
            expiryTime (int): time in seconds how long the tokken should last
        Returns:
            bytearray

        The function takes in a json string, a signature which is a byte array 
            and expiry time in seconds returns a token from the json payload and head
    '''

    byte_array = bytearray()

    randomSeed = bytearray(os.urandom(8))

    payloadLength = len(jsonString)
    _payloadLengthInBytes = payloadLength.to_bytes(4, 'big')

    expiryTime = int(time.time())+expiryTime
    _expiryTimeInBytes = expiryTime.to_bytes(5, 'big')

    payloadByteArray = __createByteArrayFromPayload(jsonString)

    byte_array.extend(signature)
    byte_array.extend(_expiryTimeInBytes)
    byte_array.extend(randomSeed)
    byte_array.extend(_payloadLengthInBytes)
    byte_array.extend(payloadByteArray)

    sampleCheckSum = __calculateCheckSum(byte_array)
    _sampleCheckSum = sampleCheckSum.to_bytes(2, 'big')
    byte_array.extend(_sampleCheckSum)

    return byte_array

def new(payload:Any, secondsToExpire:int, version:str='v1') -> dict[str, bool|str|str]:
    '''
    attempt to create a kisa-token
    Args:
        payload(Any): the data to embed in the token
        secondsToExpire(int): the time(seconds) from the time of creation in which the token should expire
        version(str): the token version to use. leave this the fuck alone if you dont know what you're doing
    
    Returns:
        dict in form
        ```
        {
            'status': bool,
            'log': str,
            'token': str
        }
        ```
    '''

    reply = {'status':False, 'log':'', 'token':''}
    try:
        payload = encodeJSON(payload)
    except:
        reply['log'] = 'failed to serialize payload into JSON'
        return reply

    if secondsToExpire<=0:
        reply['log'] = 'invalid `secondsToExpire` given for token'
        return reply

    if version not in __VERSIONS:
        reply["log"] = f'unknown version {version}'
        return reply

    _token = __create(payload, signature=__VERSIONS[version]['signature'], expiryTime=secondsToExpire)

    __encrypt(_token,version)

    reply["token"] = _token.hex()

    reply["status"] = True
    return reply

def read(token:str, version:str='v1') -> dict:
    '''
    attempt to read a token
    Args:
        token(str): token to read
        version(str): the token version to use. leave this the fuck alone if you dont know what you're doing

    Returns:
        dict in form
        ```
        {
            'status': bool,
            'log': str,
            'data': Any
        }
        ```
    '''
    reply = {'status':False, 'log':'', 'data':None}

    if not isinstance(token,str):
        reply["log"] = '[ET01] invalid token given'
        return reply

    try: token = bytearray.fromhex(token)
    except:
        reply["log"] = '[ET02] invalid token given'
        return reply

    if version not in __VERSIONS:
        reply["log"] = f'[ET03] unknown version {version}'
        return reply

    if 'v1'==version:
        if len(token) < 21 + 2: # head:21, checksum:2 bytes
            reply["log"] = '[ET03] invalid token given'
            return reply

        __decrypt(token, version)

        _signature = token[:4]
        _timestamp = int.from_bytes(token[4 : 4+5], byteorder='big')
        _payloadLength = int.from_bytes(token[17 : 17+4], byteorder='big')
        _checksum = int.from_bytes(token[-2:], byteorder='big')
        calculatedChecksum = __calculateNewCheckSumFromToken(token)
        currentEpochTime = int(time.time())

        if _signature != __VERSIONS["v1"]['signature']:
            reply['log'] = '[ETV01] invalid token tiven'
            return reply

        if _checksum != calculatedChecksum:
            reply['log'] = '[ETV02] invalid token tiven'
            return reply

        if _timestamp < currentEpochTime:
            reply['log'] = '[ETV03] invalid token tiven'
            return reply

        if _payloadLength != len(token) - 21 - 2:
            print(token[17 : 17+4],_payloadLength,  len(token) - 21 - 2)
            reply['log'] = '[ETV04] invalid token tiven'
            return reply

        _data = token[21:-2].decode('utf-8')

        try:
            reply["data"] = decodeJSON(_data)
        except Exception as e:
            print(e)
            reply["log"] = '[ETV05] invalid token given'
            return reply

    reply["status"] = True
    return reply

if __name__ == "__main__":
    data = {
        "name": "John Doe",
        "age": 30,
        "city": "New York",
        "isStudent": False,
        "grades": [85, 90, 78],
        "address": {
            "street": "123 Main Street",
            "zipCode": "10001"
        }
    }

    print('---data----'); print(data)
    reply = new(data, 10)
    _token = reply['token']
    print('\n---token----'); print(_token)

    reply = read(_token)
    print('\n---decoded token----'); print(reply['data'])

    print('\n---decoded token == data?----'); print(reply['data']==data)
