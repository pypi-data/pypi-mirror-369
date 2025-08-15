"""
Developer utility for Ed25519 license key management.

Usage examples:
  # Generate a new keypair (DO NOT commit private keys)
  python -m tools.license_keygen --gen-keypair

  # Sign a Pro license (expires 2030-12-31)
  python -m tools.license_keygen --sign --private-key-b64 <SK_B64> \
      --tier PRO --expires 20301231 --name ACME

Outputs a base64-encoded JSON license key suitable for activation via:
  python -m cameleon_dp.cli license activate --key <BASE64_JSON_KEY>

Set CAMELEON_PUBKEY_B64 env var (public key) on the runtime to enable verification.
"""
import argparse
import json
from base64 import b64encode, b64decode

try:
    from nacl.signing import SigningKey  # type: ignore
except Exception as e:  # pragma: no cover
    raise SystemExit("PyNaCl is required. Install with: pip install PyNaCl") from e


def gen_keypair():
    sk = SigningKey.generate()
    vk = sk.verify_key
    return b64encode(bytes(sk)).decode("utf-8"), b64encode(bytes(vk)).decode("utf-8")


def sign_license(private_key_b64: str, tier: str, expires: str, name: str) -> str:
    payload = json.dumps({"tier": tier, "expires": expires, "name": name}, separators=(",", ":")).encode("utf-8")
    sk = SigningKey(b64decode(private_key_b64))
    sig = sk.sign(payload).signature
    key_obj = {"tier": tier, "expires": expires, "name": name, "sig": b64encode(sig).decode("utf-8")}
    return b64encode(json.dumps(key_obj, separators=(",", ":")).encode("utf-8")).decode("utf-8")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--gen-keypair", action="store_true", help="Generate an Ed25519 keypair (base64)")
    ap.add_argument("--sign", action="store_true", help="Sign a license with the provided private key")
    ap.add_argument("--private-key-b64", type=str, default=None, help="Base64-encoded private key for signing")
    ap.add_argument("--tier", type=str, choices=["PRO", "ENT"], help="License tier")
    ap.add_argument("--expires", type=str, help="Expiry YYYYMMDD (UTC)")
    ap.add_argument("--name", type=str, help="Customer name or org")
    args = ap.parse_args()

    if args.gen_keypair:
        sk_b64, pk_b64 = gen_keypair()
        print(json.dumps({
            "private_key_b64": sk_b64,
            "public_key_b64": pk_b64,
            "env_hint": {
                "CAMELEON_PUBKEY_B64": pk_b64
            }
        }, indent=2))
        return

    if args.sign:
        if not (args.private_key_b64 and args.tier and args.expires and args.name):
            raise SystemExit("--sign requires --private-key-b64, --tier, --expires, --name")
        lic_b64 = sign_license(args.private_key_b64, args.tier, args.expires, args.name)
        print(json.dumps({
            "license_key_b64": lic_b64,
            "usage": "python -m cameleon_dp.cli license activate --key <license_key_b64>"
        }, indent=2))
        return

    ap.print_help()


if __name__ == "__main__":
    main()


