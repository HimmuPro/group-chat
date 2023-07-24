import json

from django.contrib.auth.models import User
from channels.generic.websocket import AsyncWebsocketConsumer
from asgiref.sync import sync_to_async
from django.utils import timezone
from .models import Group, Message
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):

    @database_sync_to_async
    def get_message(self, message_id):
        try:
            # Assuming you have a Message model, replace 'Message' with your actual model name
            return Message.objects.get(id=message_id)
        except Message.DoesNotExist:
            return None

    @database_sync_to_async
    def update_message_likes(self, message_id, likes):
        try:
            # Assuming you have a Message model, replace 'Message' with your actual model name
            message = Message.objects.get(id=message_id)
            message.likes = likes
            message.save()
        except Message.DoesNotExist:
            pass

    async def connect(self):
        self.group_name = self.scope['url_route']['kwargs']['group_name']
        self.group_name_2 = 'chat_%s' % self.group_name

        await self.channel_layer.group_add(
            self.group_name_2,
            self.channel_name
        )

        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.group_name_2,
            self.channel_name
        )

    # Receive message from WebSocket
    async def receive(self, text_data):
        data = json.loads(text_data)
        action = data.get('action')

        if action == 'like':
            message_id = data.get('message_id')
            username = data.get('username')
            group = data.get('group')

            message = await self.get_message(message_id)
            if message:
                # Update the message likes count
                message.likes += 1
                await self.update_message_likes(message_id, message.likes)

                # Broadcast the updated like count to all connected clients
                await self.send(text_data=json.dumps({
                    'action': 'like',
                    'message_id': message_id,
                    'likes': message.likes,
                }))

        else:
            message = data['message']
            username = data['username']
            group = data['group']
            timestamp = timezone.now().strftime('%Y-%m-%d %H:%M:%S')
            await self.save_message(username, group, message, timestamp)

            # await self.save_message(username, group, message)

            # Send message to group group
            await self.channel_layer.group_send(
                self.group_name_2,
                {
                    'type': 'chat_message',
                    'message': message,
                    'username': username,
                    'timestamp': timestamp
                }
            )

    # Receive message from group group
    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        timestamp = event['timestamp']

        # Send message to WebSocket
        await self.send(text_data=json.dumps({
            'message': message,
            'username': username,
            'timestamp': timestamp
        }))

    @sync_to_async
    def save_message(self, username, group, message, timestamp):
        user = User.objects.get(username=username)
        group = Group.objects.get(slug=group)
        # message = f"{message} [{timestamp}]\n"
        Message.objects.create(user=user, group=group, content=message, timestamp=timestamp)
