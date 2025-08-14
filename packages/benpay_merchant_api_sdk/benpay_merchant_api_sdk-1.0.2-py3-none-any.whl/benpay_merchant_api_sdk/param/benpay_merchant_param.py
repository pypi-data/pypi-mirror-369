class CreatePayOrderParam:
    def __init__(self):
        self.coin = None
        self.amount = None
        self.merchant_order_no = None
        self.merchant_note = None


class GetPayOrderInfoParam:
    def __init__(self):
        self.payment_id = None


class GetPayOrderListParam:
     def __init__(self):
        self.page = None
        self.limit = None
        self.offset = None
        self.order_by = None
        self.created_at_begin = None
        self.created_at_end = None
        self.payment_id = None
        self.merchant_order_no = None