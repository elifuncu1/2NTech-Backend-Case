# tasks.py
from celery import shared_task
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
@shared_task
def send_late_notification(user_id, late_minutes):
    # Kullanıcıyı bulma
    user = User.objects.get(id=user_id)
    channel_layer = get_channel_layer()
    message = f'{user.username} personeli {late_minutes} dakika gec kaldi.'
    
    # WebSocket üzerinden mesaj gönderme
    async_to_sync(channel_layer.group_send)(
        'notifications', 
        {
            'type': 'send_notification',
            'message': message,
        }
    )
    return "Notification sent via WebSocket"
@shared_task
def send_leave_notification(user_id):
    try:
        # Kullanıcıyı bulma
        user = User.objects.get(id=user_id)
        # WebSocket üzerinden mesaj göndermek için channel layer'ı kullanıyoruz
        channel_layer = get_channel_layer()
        message = f'{user.username} personelinin yıllık izni 3 günden az kaldı. Lütfen kontrol edin.'
        
        # WebSocket üzerinden bildirim gönderme
        async_to_sync(channel_layer.group_send)(
            'notifications', 
            {
                'type': 'send_notification',
                'message': message,
            }
        )
        return "Notification sent via WebSocket"
    except User.DoesNotExist:
        return "User not found"
