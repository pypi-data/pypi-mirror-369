'''
Created on 29 Mar 2024

@author: jacklok
'''

from flask import Blueprint
import logging
from whatsapp import WhatsApp, Message
from flask import request, Response
from trexadmin.conf import WHATSAPP_TOKEN, WHATSAPP_PHONE_NUMBER_ID,\
    WHATSAPP_VERIFY_TOKEN

facebook_api_bp = Blueprint('facebook_api_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/facebook/api'
                     )

logger = logging.getLogger('controller')

messenger = WhatsApp(WHATSAPP_TOKEN,
                     phone_number_id=WHATSAPP_PHONE_NUMBER_ID)
VERIFY_TOKEN = WHATSAPP_VERIFY_TOKEN

'''
Blueprint settings here
'''
@facebook_api_bp.context_processor
def facebook_webhook_bp_inject_settings():
    return dict(
                
                )
@facebook_api_bp.route("/webhook/", methods=["GET"])
def whatsapi_verify_token():
    if request.args.get("hub.verify_token") == VERIFY_TOKEN:
        logger.info("Verified webhook")
        challenge = request.args.get("hub.challenge")
        return str(challenge)
    
    logger.error("Webhook Verification failed")
    return "Invalid verification token"


@facebook_api_bp.route("/webhook/", methods=["POST"])
def whatsapi_hook():
    # Handle Webhook Subscriptions
    data = request.get_json()
    if data is None:
        return Response(status=200)
    logging.info("Received webhook data: %s", data)
    changed_field = messenger.changed_field(data)
    if changed_field == "messages":
        new_message = messenger.is_message(data)
        if new_message:
            msg = Message(instance=messenger, data=data)
            mobile = msg.sender
            name = msg.name
            message_type = msg.type
            logger.info(
                f"New Message; sender:{mobile} name:{name} type:{message_type}"
            )
            if message_type == "text":
                message = msg.content
                name = msg.name
                logger.info("Message: %s", message)
                m = Message(instance=messenger, to=mobile,
                            content="Hello World")
                m.send()

            elif message_type == "interactive":
                message_response = msg.interactive
                if message_response is None:
                    return Response(status=400)
                interactive_type = message_response.get("type")
                message_id = message_response[interactive_type]["id"]
                message_text = message_response[interactive_type]["title"]
                logger.info(
                    f"Interactive Message; {message_id}: {message_text}")

            elif message_type == "location":
                message_location = msg.location
                if message_location is None:
                    return Response(status=400)
                message_latitude = message_location["latitude"]
                message_longitude = message_location["longitude"]
                logger.info("Location: %s, %s",
                             message_latitude, message_longitude)

            elif message_type == "image":
                image = msg.image
                if image is None:
                    return Response(status=400)
                image_id, mime_type = image["id"], image["mime_type"]
                image_url = messenger.query_media_url(image_id)
                if image_url is None:
                    return Response(status=400)
                image_filename = messenger.download_media(image_url, mime_type)
                logger.info(f"{mobile} sent image {image_filename}")

            elif message_type == "video":
                video = msg.video
                if video is None:
                    return Response(status=400)
                video_id, mime_type = video["id"], video["mime_type"]
                video_url = messenger.query_media_url(video_id)
                if video_url is None:
                    return Response(status=400)
                video_filename = messenger.download_media(video_url, mime_type)
                logger.info(f"{mobile} sent video {video_filename}")

            elif message_type == "audio":
                audio = msg.audio
                if audio is None:
                    return Response(status=400)
                audio_id, mime_type = audio["id"], audio["mime_type"]
                audio_url = messenger.query_media_url(audio_id)
                if audio_url is None:
                    return Response(status=400)
                audio_filename = messenger.download_media(audio_url, mime_type)
                logger.info(f"{mobile} sent audio {audio_filename}")

            elif message_type == "document":
                file = msg.document
                if file is None:
                    return Response(status=400)
                file_id, mime_type = file["id"], file["mime_type"]
                file_url = messenger.query_media_url(file_id)
                if file_url is None:
                    return Response(status=400)
                file_filename = messenger.download_media(file_url, mime_type)
                logger.info(f"{mobile} sent file {file_filename}")
            else:
                logging.info(f"{mobile} sent {message_type} ")
                logger.info(data)
        else:
            delivery = messenger.get_delivery(data)
            if delivery:
                logger.info(f"Message : {delivery}")
            else:
                logger.info("No new message")
    return "OK", 200 

