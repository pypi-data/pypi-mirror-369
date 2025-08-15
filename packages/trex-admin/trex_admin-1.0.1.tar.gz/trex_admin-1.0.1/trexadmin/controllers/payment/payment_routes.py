'''
Created on 2 Nov 2020

@author: jacklok
'''

from trexadmin.conf import PAYMENT_GATEWAY_APP_KEY, PAYMENT_GATEWAY_SECRET_KEY
from flask import Blueprint, render_template, request, jsonify, url_for, current_app, request, redirect
from trexlib.utils.log_util import get_tracelog
from trexlib.utils.string_util import boolify
from trexlib.utils.crypto_util import encrypt_json, decrypt_json
from trexmodel.utils.model.model_util import create_db_client
from trexadmin.libs.http import StatusCode
from trexadmin.forms.payment.payment_forms import PaymentForm
from trexpayment.util.payment_util import encrypt_payment_details, decrypt_payment_details
from flask_babel import gettext
import logging, json
import stripe
import os

stripe_keys = {
  'secret_key'      : PAYMENT_GATEWAY_SECRET_KEY,
  'publishable_key' : PAYMENT_GATEWAY_APP_KEY
}

stripe.api_key      = stripe_keys['secret_key']


STRIPE_PUBLISHABLE_KEY = PAYMENT_GATEWAY_APP_KEY

payment_bp = Blueprint('payment_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/payment'
                     )

logger = logging.getLogger('debug')


stripe.api_key = os.environ.get("STRIPE_SECRET_KEY")
webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET")

'''
Blueprint settings here
'''
@payment_bp.context_processor
def payment_bp_inject_settings():
    return dict(
                side_menu_group_name    = "payment"
                )


@payment_bp.route('/stripe-webhook', methods=['POST', 'GET'])
def stripe_payment_webhook():
    payload = request.data.decode("utf-8")
    received_sig = request.headers.get("Stripe-Signature", None)
    logger.info('payload=%s', payload)
    logger.info('received_sig=%s', received_sig)
    logger.info('api key=%s', stripe.api_key)
    logger.info('webhook_secret=%s', webhook_secret)
    payment_intent = None
    
    try:
        event = stripe.Webhook.construct_event(
                    payload, received_sig, webhook_secret
                )
        
        
        logger.debug('event=%s', event)
        
        
        if event['type'] == 'payment_intent.amount_capturable_updated':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.canceled':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.created':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.partially_funded':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.payment_failed':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.processing':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.requires_action':
            payment_intent = event['data']['object']
        elif event['type'] == 'payment_intent.succeeded':
            payment_intent = event['data']['object']
        else:
            
            logger.debug('Unhandled event type %s', event['type'])
        
        logger.debug('payment_intent=%s', payment_intent)
        
        return jsonify(success=True)
        
    except ValueError:
        logger.error("Error while decoding event!")
        return "Bad payload", 400
    
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature!")
        return "Bad signature", 400

@payment_bp.route('/client-subscription', methods=['GET'])
def enter_client_id():
    return render_template("payment/enter_client_id.html",
                           page_url                         = url_for('payment_bp.enter_client_id')
                           )

@payment_bp.route('/show-subscription-plan/<client_id>', methods=['GET'])
def show_subscription_plan(client_id):
    
    return render_template("payment/subscription_plan.html", 
                           page_title                       = gettext('Subscription Plan'),
                           page_url                         = url_for('payment_bp.show_subscription_plan', client_id=client_id),
                           retention_plan_checkout_url      = url_for('payment_bp.create_subscription_plan_checkout', subscription_plan='retention_annual', client_id=client_id),
                           conversion_plan_checkout_url     = url_for('payment_bp.create_subscription_plan_checkout', subscription_plan='conversion_annual', client_id=client_id),
                           expansion_plan_checkout_url      = url_for('payment_bp.create_subscription_plan_checkout', subscription_plan='expansion_annual', client_id=client_id),
                           )

@payment_bp.route('/create-subscription-plan-checkout/<subscription_plan>/client-id/<client_id>', methods=['GET'])
def create_subscription_plan_checkout(subscription_plan, client_id):
    target_url = 'https://payment-dev.penefit.com/checkout/create/{subscription_plan}/merchant_acct/{client_id}'.format(subscription_plan=subscription_plan, client_id=client_id)
    return redirect(target_url)
    
    '''
    subscription_plan_items = []
    
    if subscription_plan.startswith('retention'):
        subscription_plan_items = [
                                    {
                                      'price_data': {
                                        'currency': 'myr',
                                        'product_data': {
                                          'name': 'Retention Plan Annual Subscription',
                                        },
                                        'unit_amount': 144000,
                                      },
                                      'quantity': 1,
                                    }
                                    ]
    elif subscription_plan.startswith('conversion'):
        subscription_plan_items = [
                                    {
                                      'price_data': {
                                        'currency': 'myr',
                                        'product_data': {
                                          'name': 'Conversion Plan Annual Subscription',
                                        },
                                        'unit_amount': 216000,
                                      },
                                      'quantity': 1,
                                    }
                                    ]
    elif subscription_plan.startswith('expansion'):
        subscription_plan_items = [
                                    {
                                      'price_data': {
                                        'currency': 'myr',
                                        'product_data': {
                                          'name': 'Expansion Plan Annual Subscription',
                                        },
                                        'unit_amount': 288000,
                                      },
                                      'quantity': 1,
                                    }
                                    ]
    
    
    logger.debug('subscription_plan_items=%s', subscription_plan_items)
    
    session = stripe.checkout.Session.create(
                                payment_method_types    = ['card'],
                                line_items              = subscription_plan_items,
                                client_reference_id     = client_id,
                                metadata                = {
                                                            'client_key'        : client_id,
                                                            'product_code'      : subscription_plan,
                                                            },
                                mode                    = 'payment',
                                success_url             = 'https://payment-dev.penefit.com/payment/subscribe-plan-success',
                                cancel_url              = 'https://payment-dev.penefit.com/payment/subscribe-plan-cancel',
                                )

    logger.debug('session.id=%s', session.id)

    return render_template("payment/subcription_plan_checkout.html", 
                           payment_key      = STRIPE_PUBLISHABLE_KEY,
                           session_id       = session.id,    
                           )
    '''

@payment_bp.route('/subscribe-plan-success', methods=['GET'])
def subscribe_plan_success():
    
    return render_template("payment/subscribe_plan_success.html", 
                           )    
    
@payment_bp.route('/subscribe-plan-cancel', methods=['GET'])
def subscribe_plan_cancel():
    
    return render_template("payment/subscribe_plan_success.html", 
                           )    


@payment_bp.route('/test-stripe-checkout/<encrypted_payment_details>', methods=['POST'])
def test_stripe_checkout(encrypted_payment_details):

    
    payment_data = request.form
    
    logger.debug('payment_data=%s', payment_data)
    logger.debug('encrypted_payment_details=%s', encrypted_payment_details)
    
    payment_details = decrypt_payment_details(encrypted_payment_details)
    
    logger.debug('payment_details=%s', payment_details)
    
    payment_amount  = payment_details.get('amount')
    currency_code   = payment_details.get('currency')
    desc            = payment_details.get('desc')
    
    logger.debug('payment_amount=%s', payment_amount)
    logger.debug('currency_code=%s', currency_code)
    
    customer = stripe.Customer.create(
        email       = request.form.get('stripeEmail'),
        source      = request.form.get('stripeToken'),
    )

    stripe.Charge.create(
        customer    = customer.id,
        amount      = payment_amount,
        currency    = currency_code,
        description = desc,
        
    )

    return render_template("payment/stripe_payment_checkout.html", 
                           page_title       = gettext('Stripe Payment Checkout'),
                           amount           = payment_amount,
                           )    
