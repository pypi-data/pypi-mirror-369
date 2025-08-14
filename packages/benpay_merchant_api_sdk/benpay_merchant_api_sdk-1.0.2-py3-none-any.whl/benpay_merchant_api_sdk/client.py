import json
import time
import uuid
import requests
from urllib.parse import urljoin
import benpay_merchant_api_sdk.param.benpay_merchant_param as benpay_param
import benpay_merchant_api_sdk.utils as utils


class BenpayMerchantClient:
    def __init__(self, api_key, merchant_private_key_string, platform_public_key_string, server="https://api.benfenpay.com"):
        self.api_key = api_key
        self.merchant_private_key_string = merchant_private_key_string
        self.platform_public_key_string = platform_public_key_string
        self.server = server

    def _do_res(self, response):
        # 验证签名
        if response.headers.get('benpay-signature'):
            # 要验证的信息
            nonce = response.headers['benpay-nonce']
            timestamp = response.headers['benpay-timestamp']
            signature = response.headers['benpay-signature']
            message = f"{timestamp}\n{nonce}\n{response.text}\n"
            is_valid = utils.verify_signature(self.platform_public_key_string, signature, message)
            if is_valid:
                return response
            else:
                raise ValueError("signature Fail")
        else:
            return response

    def _do_req(self, method, path, params=None, **kwargs):
        params = params or {}
        timestamp = int(time.time() * 1000)
        nonce = uuid.uuid4().hex
        method = method.upper()

        if method not in ["GET", "POST"]:
            raise ValueError("method must be GET or POST")

        headers = self._gen_params(method, path, timestamp, nonce, params)
        url = urljoin(self.server, path)

        if method == "GET":
            response = requests.get(url, headers=headers, data=json.dumps(params).encode('utf-8'), timeout=5)
        else:
            response = requests.post(url, headers=headers, data=json.dumps(params).encode('utf-8'), timeout=5)

        return self._do_res(response)

    def _gen_params(self, method: str, url_path: str, timestamp: int, nonce: str, params: dict) -> dict:
        # Generate the signature
        signature = utils.generate_signature(self.api_key, timestamp, nonce, method, url_path, json.dumps(params), self.merchant_private_key_string)

        # Generate the Authorization header
        authorization_header = utils.generate_authorization_header(self.api_key, timestamp, nonce, signature)
        headers = {
            "Authorization": authorization_header,
            "Content-Type": "application/json"
        }
        return headers

    def create_pay_order(self, params: benpay_param.CreatePayOrderParam):
        return self._do_req("POST", "/v1/payment/create", utils.object2dict(params))

    def get_order_info(self, params: benpay_param.GetPayOrderInfoParam):
        return self._do_req("POST", "/v1/payment/info", utils.object2dict(params))

    def get_order_list(self, params: benpay_param.GetPayOrderListParam):
        return self._do_req("POST", "/v1/payment/list", utils.object2dict(params))

    def handler_webhook(self, response: requests.Response):
        return self._do_res(response)



