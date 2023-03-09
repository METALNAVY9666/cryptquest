"""module de test"""

from Crypto.Cipher import AES
from typing import Any

# init

class CrypteurPair:
    """classe de gestion des couples crypteur/décrypteurs"""
    def __init__(self, clef: str) -> None:
        key = clef.encode()
        if len(key) != 16:
            raise ValueError

        self.crypter: Any = AES.new(key, AES.MODE_EAX, nonce= key)
        self.decrypteur = AES.new(key, AES.MODE_EAX, nonce=self.crypter.nonce)

    def code_AES(self, chc: str):
        """crypte le texte en utilisant AES"""
        texte, _ = self.crypter.encrypt_and_digest(chc.encode())
        return texte

    def decode_AES(self, cryptexte: bytes):
        return self.decrypteur.decrypt(cryptexte).decode()

    def code_file(self, file_nom: str):
        """crypte un fichier"""
        with open(file_nom, "r", encoding="utf-8") as file:
            texte = self.code_AES(file.read())
        return texte

    def decode_file(self, file_nom: str):
        """décrypte un fichier"""
        with open(file_nom, "rb", encoding="utf-8") as file:
            texte = self.decode_AES(file.read())
        return texte


crypteurpair = CrypteurPair('qwertyuiop123456')

messagec = crypteurpair.code_file('idees/sn.txt')
print(messagec)
