from app.models import MappedOrder, OrderRequest


def map_order_payload(order: OrderRequest) -> MappedOrder:
    return MappedOrder(
        external_order_id=order.order_id,
        client_name=order.customer_name,
        client_email=order.customer_email,
        total_amount=order.amount,
        currency=order.currency.lower(),
        source_platform=order.source.lower(),
    )
