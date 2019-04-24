from Crypto.Cipher import AES
from binascii import b2a_hex, a2b_hex


class prpcrypt():
    '''
    用于通过密钥进行重要数据的加密解密
    '''

    def __init__(self):
        self.key = "okeqwnk2987#$%ql"
        # 这里密钥key 长度必须为16（AES-128）,
        # 24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前AES-128 足够目前使用
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不足18位就用空格补足为18位，
    # 如果大于16当时不是18的倍数，那就补足为18的倍数。
    def encrypt(self, text):
        cryptor = AES.new(bytes(self.key, "utf8"), self.mode, b'0000000000000000')

        length = 16
        count = len(text)
        if count < length:
            add = (length - count)
            text = text + ('\0' * add)
        elif count > length:
            add = (length - (count % length))
            text = text + ('\0' * add)
        self.ciphertext = cryptor.encrypt(bytes(text, "utf8"))
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return b2a_hex(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        cryptor = AES.new(bytes(self.key, encoding="utf8"), self.mode, b'0000000000000000')
        plain_text = cryptor.decrypt(a2b_hex(text))
        return plain_text
