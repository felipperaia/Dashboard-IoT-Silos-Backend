#!/usr/bin/env python3
"""
scripts/generate_vapid.py
Gera um par de chaves VAPID (public/private) em formato base64url (compatível com web-push).
Uso:
  python scripts/generate_vapid.py
  python scripts/generate_vapid.py --out-file ../backend/.env  # anexa chaves ao .env (atenção para não commitar)
Dependências: cryptography
"""
import argparse
import json
from base64 import urlsafe_b64encode

from cryptography.hazmat.primitives.asymmetric import ec

def generate_keys():
    # Gera chave EC P-256 (secp256r1) e converte para o formato esperado pelo web-push (base64url)
    key = ec.generate_private_key(ec.SECP256R1())
    priv_num = key.private_numbers().private_value
    priv_bytes = priv_num.to_bytes(32, "big")  # 32 bytes para P-256

    pub = key.public_key().public_numbers()
    x = pub.x.to_bytes(32, "big")
    y = pub.y.to_bytes(32, "big")
    uncompressed = b"\x04" + x + y  # formato uncompressed point

    public_key = urlsafe_b64encode(uncompressed).rstrip(b"=").decode("utf-8")
    private_key = urlsafe_b64encode(priv_bytes).rstrip(b"=").decode("utf-8")
    return public_key, private_key

def main():
    parser = argparse.ArgumentParser(description="Gerador VAPID keys (base64url)")
    parser.add_argument("--out-file", help="Anexa VAPID keys a um arquivo (ex: backend/.env)")
    args = parser.parse_args()

    pub, priv = generate_keys()
    payload = {"VAPID_PUBLIC_KEY": pub, "VAPID_PRIVATE_KEY": priv}
    print(json.dumps(payload, indent=2))

    if args.out_file:
        with open(args.out_file, "a", encoding="utf-8") as f:
            f.write(f'\nVAPID_PUBLIC_KEY={pub}\nVAPID_PRIVATE_KEY={priv}\n')
        print(f"Chaves anexadas ao arquivo: {args.out_file} (não comite este arquivo)")

if __name__ == "__main__":
    main()
