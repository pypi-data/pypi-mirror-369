import base64
from Crypto.Signature import pkcs1_15
from Crypto.PublicKey import RSA
from Crypto.Hash import SHA256


def generate_signature(api_key, timestamp, nonce, method, url_path, body, private_key_string):
    # Step 1: Generate the string to be signed
    public_param_string = f"api_key={api_key},timestamp={timestamp},nonce={nonce}"
    sign_string = f"{public_param_string}\n{method.upper()}\n{url_path}\n{body}\n"

    # Step 2: Load the private key from the string
    private_key = RSA.import_key(private_key_string)

    # Step 3: Create the SHA256 hash
    hash_obj = SHA256.new(sign_string.encode('utf-8'))

    # Step 4: Sign the hash with the private key using SHA256withRSA
    signature = pkcs1_15.new(private_key).sign(hash_obj)

    # Step 5: Encode the signature with Base64
    signature_base64 = base64.b64encode(signature).decode('utf-8')

    return signature_base64


def verify_signature(public_key_pem_str, signature_base64_str, message_str):
    # 将字符串转换为字节串
    public_key_pem = public_key_pem_str.encode('utf-8')
    signature = base64.b64decode(signature_base64_str)  # 将Base64字符串解码为字节串
    message = message_str.encode('utf-8')

    # 加载公钥
    public_key = RSA.import_key(public_key_pem)

    # 对消息进行SHA256哈希
    h = SHA256.new(message)

    # 验证签名
    try:
        pkcs1_15.new(public_key).verify(h, signature)
        return True
    except (ValueError, TypeError):
        return False


def object2dict(params, except_key=None):
    if not except_key:
        except_key = []
    params_dict = {}
    for key, value in params.__dict__.items():
        if key not in except_key and value is not None:
            params_dict[key] = value
    return params_dict


def generate_authorization_header(api_key, timestamp, nonce, signature):
    return f"BENPAY-SHA256-RSA2048 api_key={api_key},timestamp={timestamp},nonce={nonce},signature={signature}"