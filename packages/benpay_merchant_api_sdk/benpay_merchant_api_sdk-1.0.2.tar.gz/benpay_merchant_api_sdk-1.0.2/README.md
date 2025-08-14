# Python SDK for Benpay merchant API

# API Documentation
- [Official documentation](https://docs.benpay.org/zh-Hans/BenPay/Doc/api_doc/)

# Installation

```bash
pip install benpay_merchant_api_sdk
```

# Usage
> Consider `/v1/payment/create` as a reference, the full code can be located in the demo directory.
* Get api key info

https://www.benpay.org/paymvp/business

* create order
```python
import config
import sys
import uuid

sys.path.append("../../")
from benpay_merchant_api_sdk.client import BenpayMerchantClient
import benpay_merchant_api_sdk.param.benpay_merchant_param as benpay_param


client = BenpayMerchantClient(
    api_key=config.API_KEY,
    server=config.SERVER,
    merchant_private_key_string=config.MERCHANT_PRIVATE_KEY_STRING,
    platform_public_key_string=config.PLATFORM_PUBLIC_KEY_STRING
)

param = benpay_param.CreatePayOrderParam()
param.coin = "BUSD"
param.amount = "0.1"
param.merchant_order_no = uuid.uuid4().hex
param.merchant_note = "22222"

resp = client.create_pay_order(param)

if resp.status_code == 200:
    print(resp.json())
else:
    print(resp.text)
```%
