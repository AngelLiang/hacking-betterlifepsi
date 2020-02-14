from psi.app.models import EnumValues
from psi.app import const, service


class PurchaseOrderService(object):
    """采购单服务"""
    @staticmethod
    def create_expense_receiving(po):
        """创建支出和收货单"""
        if po.status.code == const.PO_ISSUED_STATUS_KEY:
            # 判断采购单状态是否已经提交
            logistic_exp, goods_exp = PurchaseOrderService.create_expenses(po)
            db = service.Info.get_db()
            if logistic_exp is not None:
                db.session.add(logistic_exp)
            if goods_exp is not None:
                db.session.add(goods_exp)
            # 创建收货单，如果不存在的话
            receiving = PurchaseOrderService.create_receiving_if_not_exist(po)
            if receiving is not None:
                db.session.add(receiving)
            return logistic_exp, goods_exp, receiving

    @staticmethod
    def create_expenses(po):
        """
        Create expense from purchase order
        Create one record for the goods amount, one record for logistic amount
        :return: The logistic expense and goods expense
        """
        from psi.app.models import Expense
        expenses = po.expenses
        # 物流支出
        logistic_exp = None
        # 默认物流支出类型
        default_logistic_exp_type = EnumValues.get(const.DEFAULT_LOGISTIC_EXPENSE_TYPE_KEY)
        # 默认货物支出类型
        default_goods_exp_type = EnumValues.get(const.DEFAULT_GOODS_EXPENSE_TYPE_KEY)
        # 默认物流支出状态
        default_logistic_exp_status = EnumValues.get(const.DEFAULT_LOGISTIC_EXPENSE_STATUS_KEY)
        # 默认货物支出状态
        default_goods_exp_status = EnumValues.get(const.DEFAULT_GOODS_EXPENSE_STATUS_KEY)
        # 货物支出
        goods_exp = None
        if expenses is None:
            expenses = dict()

        # 遍历采购单关联的支出，根据支出类型覆盖相关的支出
        for expense in expenses:
            if (expense.category_id == default_logistic_exp_type.id) and (po.logistic_amount != 0):
                logistic_exp = expense
                logistic_exp.amount = po.logistic_amount
            elif (expense.category_id == default_goods_exp_type.id) and (po.goods_amount != 0):
                goods_exp = expense
                goods_exp.amount = po.goods_amount

        # 如果没有对应的支出类型则创建
        if (logistic_exp is None) and (po.logistic_amount is not None and po.logistic_amount != 0):
            # 创建发货物流支出
            logistic_exp = Expense(po.logistic_amount, po.order_date,
                                   default_logistic_exp_status.id,
                                   default_logistic_exp_type.id)
        if (goods_exp is None) and (po.goods_amount is not None and po.goods_amount != 0):
            # 创建货物采购支出
            goods_exp = Expense(po.goods_amount, po.order_date,
                                default_goods_exp_status.id,
                                default_goods_exp_type.id)
        if logistic_exp is not None:
            logistic_exp.purchase_order = po
            logistic_exp.organization = po.organization
        if goods_exp is not None:
            goods_exp.purchase_order = po
            goods_exp.organization = po.organization
        return logistic_exp, goods_exp

    @staticmethod
    def create_receiving_if_not_exist(po):
        """
        Draft receiving document is created from purchase order only
         if there's no associated receiving exists for this PO.
        :param model: the Purchase order model
        :return: Receiving document if a new one created, or None
        """
        from psi.app.models import Receiving
        receivings = po.po_receivings
        if receivings is None or len(receivings) == 0:
            recv = Receiving.create_draft_recv_from_po(po)
            return recv
        return None
