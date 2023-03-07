"""module de test"""

from Crypto.Cipher import AES
from typing import Any

# init

class CrypteurPair:
    """classe de gestion des couples crypteur/décrypteurs"""
    def __init__(self, clef) -> None:
        key: str = clef.encode()
        if len(key) != 16:
            raise ValueError

        self.crypter: Any = AES.new(key, AES.MODE_EAX, nonce= key)
        self.decrypteur = AES.new(key, AES.MODE_EAX, nonce=self.crypter.nonce)

    def code_AES(self, chc: str):
        """crypte le texte en utilisant AES"""
        texte, tag = self.crypter.encrypt_and_digest(chc.encode())
        return texte

    def decode_AES(self, cryptexte: str):
        return self.decrypteur.decrypt(cryptexte).decode()

    def code_file(self, file_nom: str):
        """crypte un fichier"""
        with open(file_nom, "r", encoding="utf-8") as file:
            texte = self.code_AES(file.read())
        return texte

    def decode_file(self, file_nom: str):
        """décrypte un fichier"""
        with open(file_nom, "r", encoding="utf-8") as file:
            texte = self.decode_AES(file.read())
        return texte

crypteurpair = CrypteurPair('qwertyuiop123456')

'''
messagec = crypteurpair.code_file('idees/sn.txt')'''
print(crypteurpair.decode_AES(b'\x06\x01&\x83\xd5\xb9\xebY\xb8\x01\x0eD\xc5 P\xf7\xfc\xafq\xbe\xb1\xf1i\xa3\xc2\xae\xb2\xcf\xdb\xdb\xd1\xabL\x8b\xbc~\xa5"\xf2\xb6\'\xa8B\xee\x96\x06\xbe\xd5\x19\x1cL\xe9\xc9\x0f#\xc4\x7fb\xab\xc93\xdf\xde\xb4"\x8f\xcf\x9c\xe5v\xd3\xed\x8a\x98\x0cM\\\x82\xf8B\xe8q\xf6,\x17\xffl\xca\x9eJ}|\xdb4\xe2HLH\xbb\xe6\x92\xfb\x17\xd6\x0c\xc15\xa9\xeb-\'\xc6\xd8\x11\xd8\xe5\xff\xb7T\x87\xb5\xd5\x9b4\x82!\xd8SU\x11\x14\xd1f\xde\x9f\x9c \x879\x1c\x95\x0fN\x12!\xca\xd2\xf6\xeb%\xb3gVM\x81\xcc\xb5\x1f\xad\xc8\xa9[xK\xb9PuQ7\xa2\xd0Ixt\xc5<v\r\x05\x045\x1d\x9d\xd2Ex9\xb0\xc57\xb8\xdd\x8b\x11vR\x81\xde\xe7\xe2;\xde\x86\xe5\x94\xcc\xe5\xdc\x19\xa3\x12\x1d\xc3\xa1\xd6Z\xfc\xfc\xaa`\x03\xf0/{\x9c\x87\xcf|8\x19+\x1fx`\x8b\xc9\xddK\x14\x95\xa6\xbe10\xf0\x8dd\x82?Ns\xec\xff\xe4\x9bb=\xa1\xa14\xd1\xf9\xda\xc3[g\xfa\xf5\x85f}\xdc\xc4\xb6\xe7\x1f1P\xf1#\x1a\x82"\x1a\xce\x9a\xaf%\x19o\xd5@\xb9=\x97\xf0\xcb\x1dq\xdf]\x7f\xa7\xd0q\xe1\x8e\xd6\x0f\'\xd2W\xe3I# \x93\x95\xdf\x04\x07'))