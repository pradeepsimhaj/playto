from core.models import IdempotencyKey

def get_existing(merchant, key):
    try:
        return IdempotencyKey.objects.get(merchant=merchant, key=key)
    except IdempotencyKey.DoesNotExist:
        return None


def save_response(merchant, key, response, status):
    IdempotencyKey.objects.create(
        merchant=merchant,
        key=key,
        response_body=response,
        status_code=status
    )