from Crypto.Cipher import AES
import base64


class prpcrypt:
    '''
    用于通过密钥进行重要数据的加密解密
    key 此处必须要求为16位
    '''

    def __init__(self, key=b'1234567812345678'):
        self.key = key
        # 这里密钥key 长度必须为16（AES-128）,24（AES-192）,或者32 （AES-256）Bytes 长度
        # 目前使用AES-128 足够目前使用
        self.mode = AES.MODE_CBC

    # 加密函数，如果text不是16的倍数【加密文本text必须为16的倍数！】，那就补足为16的倍数
    def encrypt(self, text):
        pad_it = lambda s: bytes(s + (16 - len(s) % 16) * '\0', encoding='utf8')
        cryptor = AES.new(self.key, self.mode, self.key)
        self.ciphertext = cryptor.encrypt(pad_it(text))
        # 因为AES加密时候得到的字符串不一定是ascii字符集的，输出到终端或者保存时候可能存在问题
        # 所以这里统一把加密后的字符串转化为16进制字符串
        return base64.b64encode(self.ciphertext)

    # 解密后，去掉补足的空格用strip() 去掉
    def decrypt(self, text):
        newtext = base64.b64decode(text)
        cryptor = AES.new(self.key, self.mode, self.key)
        plain_text = cryptor.decrypt(newtext)
        return str(plain_text, 'utf-8')
