import struct

_GROUP_TO_USER_AND_MSG_FORMAT = '<hl'

def writeMessage(groupId, userId, text):
    with open('../noDb/groups/' + str(groupId) + '.groupToUserAndMsgAddr', 'ab') as gf:
        with open('../noDb/groups/' + str(groupId) + '.msgAddrToText', 'ab') as mf:
            addr = mf.tell()
            for escapedChar in range(33):
                text = text.replace(chr(escapedChar), chr(0xe000 + escapedChar))
            mf.write(text.encode('utf-8'))
            mf.write(b'\n') # Mozna bo UTF-8 nie uzywa pierwszych 127 kodow w kolejnych bajtach
        gf.write(struct.pack(_GROUP_TO_USER_AND_MSG_FORMAT, userId, addr))

def readMessages(groupId, num):
    messages = []
    size = struct.calcsize(_GROUP_TO_USER_AND_MSG_FORMAT)
    with open('../noDb/groups/' + str(groupId) + '.groupToUserAndMsgAddr', 'rb') as gf:
        gf.seek(-num * size, 2)
        for i in range(num):
            print(size)
            buf = gf.read(size)
            print(buf)
            userId, addr = struct.unpack(_GROUP_TO_USER_AND_MSG_FORMAT, buf)
            with open('../noDb/groups/' + str(groupId) + '.msgAddrToText', 'rb') as mf:
                mf.seek(addr)
                text = mf.readline()[:-1].decode('utf-8')
            for escapedChar in range(33):
                text = text.replace(chr(0xe000 + escapedChar), chr(escapedChar))
            messages.append((userId, text))
    return messages

if __name__ == '__main__':
    pass