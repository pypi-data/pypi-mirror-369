'''
Created on 15 Apr 2020

@author: jacklok
'''

from flask import Blueprint, render_template, request, redirect, url_for, session
from trexlib.utils.log_util import get_tracelog
from flask_login import login_user, logout_user, current_user
from trexadmin.libs.oauth_signin import OAuthSignIn
from trexmodel.models.datastore.user_models import User 
from trexmodel.models.datastore.admin_models import SuperUser, AdminUser
from trexmodel.models.datastore.merchant_models import MerchantUser
from trexmodel.utils.model.model_util import create_db_client
from datetime import datetime
from trexadmin.libs.http import StatusCode, create_rest_message
from trexadmin.forms.admin.user_forms import RegistrationForm, SignInForm
from trexadmin.forms.merchant.merchant_forms import MerchantSignInForm    
from trexadmin.libs.flask.utils.flask_helper import remove_signin_session 
from trexlib.utils.security_util import hash_password
from trexconf import conf as admin_conf
import logging
from trexlib.utils.string_util import is_not_empty
from flask_babel import gettext
from trexadmin.controllers.system.system_routes import get_currency_config
from trexadmin.forms.merchant.user_form import UserSigninForm
from trexconf.conf import BYPASSEDS_HASHED_PASSWORD

security_bp = Blueprint('security_bp', __name__,
                     template_folder    = 'templates',
                     static_folder      = 'static',
                     url_prefix         = '/sec'
                     )

#logger = logging.getLogger('controller')
logger = logging.getLogger('debug')

@security_bp.route('/signin/a', methods=['GET'])
def admin_signin_page():
    redirect_uri            = request.args.get('redirect_uri') 
    logged_in_user_id       = session.get('logged_in_user_id')
    
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        if is_not_empty(redirect_uri):
            redirect_url_with_authorization_code = '%s&authorization_code=%s' % (redirect_uri, logged_in_user_id)
            return redirect(redirect_url_with_authorization_code)
        else:
            return redirect(url_for('admin_bp.dashboard_page'))
    else:
        return render_template("security/admin_signin_page.html",
                               signin_url = url_for('security_bp.admin_signin'), 
                               redirect_uri=redirect_uri)

@security_bp.route('/signin/m', methods=['GET'])
def merchant_signin_page():
    redirect_uri            = request.args.get('redirect_uri') 
    logged_in_user_id       = session.get('logged_in_user_id')
    
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        if is_not_empty(redirect_uri):
            redirect_url_with_authorization_code = '%s&authorization_code=%s' % (redirect_uri, logged_in_user_id)
            return redirect(redirect_url_with_authorization_code)
        else:
            user_type = session.get('user_type')
        
            logger.debug('user_type=%s', user_type)
            
            if user_type == 'merchant':
                return redirect(url_for('merchant_bp.dashboard_page'))
            
            elif user_type == 'admin':
                return redirect(url_for('admin_bp.dashboard_page'))
    else:
        return render_template("security/merchant_signin_page.html",
                               signin_url = url_for('security_bp.merchant_signin'), 
                               redirect_uri=redirect_uri)
        
@security_bp.route('/user/account-delete', methods=['GET'])
def user_account_delete():
    logged_in_user_id       = session.get('logged_in_user_id')
    
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        user_type = session.get('user_type')
        
        logger.debug('user_type=%s', user_type)
        
        if user_type == 'user':
            return redirect(url_for('user_bp.account_deletion'))
        
        elif user_type == 'merchant':
            return redirect(url_for('merchant_bp.dashboard_page'))
        
        elif user_type == 'admin':
            return redirect(url_for('admin_bp.dashboard_page'))
    else:
        return render_template("security/user_account_delete_page.html",
                               delete_account_url = url_for('security_bp.user_account_delete_post'), 
                               
                               )        


@security_bp.route('/user-account-delete-content', methods=['GET'])
def user_account_delete_content():
    
    logged_in_user_id = session.get('logged_in_user_id')
    
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        return redirect(url_for('user_bp.account_deletion'))
    else:
        return render_template("security/user_account_deletion_lazy_load_page.html")
    
@security_bp.route('/user-account-have-been-deleted', methods=['GET'])
def user_account_have_been_deleted():
    
    return render_template("security/user_account_have_been_deleted_page.html")    
    
@security_bp.route('/admin-signin-content', methods=['GET'])
def admin_signin_content():
    
    logged_in_user_id = session.get('logged_in_user_id')
    
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        return redirect(url_for('merchant_bp.dashboard_page'))
    else:
        return render_template("security/admin_signin_lazy_load_page.html")
    
@security_bp.route('/merchant-signin-content', methods=['GET'])
def merchant_signin_content():
    
    logged_in_user_id = session.get('logged_in_user_id')
    
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    if logged_in_user_id:
        return redirect(url_for('merchant_bp.dashboard_page'))
    else:
        return render_template("security/signin_lazy_load_page.html")        

@security_bp.route('/user-account-delete', methods=['post'])
def user_account_delete_post():
    logger.debug('--- user_account_delete_post ---')
    account_deletion_data = request.form
    
    logger.debug('account_deletion_data=%s', account_deletion_data)
    
    account_deletion_form = UserSigninForm(account_deletion_data)
    
    try:
        if account_deletion_form.validate():
        
            email           = account_deletion_form.email.data
            sigin_password  = account_deletion_form.password.data
            
            deleting_user     = None
            
            logger.debug('email=%s', email)
            logger.debug('sigin_password=%s', sigin_password)
            
            account_deletion_message    = gettext("Invalid email or password")
            is_signin_password_valid    = False
            is_demo_account             = False
            is_deleted_account          = False
            
            db_client = create_db_client(caller_info="user_account_delete_post")
            
            with db_client.context():
                deleting_user    = User.get_by_email(email)
                
                if deleting_user:
                    if deleting_user.demo_account==True:
                        account_deletion_message = gettext("Demo account is not allow to delete")
                        is_demo_account = True
                    else:
                        
                        if deleting_user.deleted==True:
                            account_deletion_message = gettext("User email or password is invalid")
                            logger.debug('User email or password is invalid')
                            is_deleted_account = True
                            
                        else:
                            
                            hashed_signin_password = hash_password(deleting_user.user_id, sigin_password)
                            
                            logger.debug('sigin_password=%s', sigin_password)
                            logger.debug('hashed_signin_password=%s', hashed_signin_password)
                            logger.debug('checked_user_by_email.password=%s', deleting_user.password)
                            
                            is_signin_password_valid = hashed_signin_password == deleting_user.password
                            
                            logger.debug('is_signin_password_valid=%s', is_signin_password_valid)
                            
                            if is_signin_password_valid:
                                deleting_user.request_to_delete()
                                    
                                logger.debug('User account have been deleted successfully')
                                account_deletion_message = gettext("User account have been deleted successfully")
                            else:
                                with db_client.context():
                                    deleting_user.add_try_count()
                                    
                                account_deletion_message = gettext("User email or password is invalid")
            
                
            
            if deleting_user is not None:
                if is_signin_password_valid:
                    return create_rest_message(account_deletion_message, 
                                               next_url = url_for('security_bp.user_account_have_been_deleted'),
                                               status_code=StatusCode.OK)
                else:
                    if is_demo_account or is_deleted_account:
                        return create_rest_message(account_deletion_message,
                                               status_code=StatusCode.BAD_REQUEST)
                    else:
                        return create_rest_message(account_deletion_message,
                                               next_url = url_for('security_bp.user_account_have_been_deleted'), 
                                               status_code=StatusCode.BAD_REQUEST)
                    
                    
            else:
                return create_rest_message(account_deletion_message, status_code=StatusCode.BAD_REQUEST)
                
                
                    
                            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            logger.warn('Invalid account deletion request')
            error_message = account_deletion_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to signin in account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@security_bp.route('/signin/a', methods=['post'])
def admin_signin():
    logger.debug('--- submit signin data ---')
    signin_data = request.form
    
    logger.debug('signin_data=%s', signin_data)
    
    signin_form = SignInForm(signin_data)
    
    try:
        if signin_form.validate():
        
            email           = signin_form.signin_email.data
            sigin_password  = signin_form.password.data
            redirect_url    = signin_form.redirect_url.data
            
            logger.debug('email=%s', email)
            logger.debug('sigin_password=%s', sigin_password)
            logger.debug('redirect_url=%s', redirect_url)
            
            db_client = create_db_client(caller_info="signin")
            
            if admin_conf.SUPERUSER_EMAIL==email:
                logger.debug('This is superuser signin')
                if admin_conf.SUPERUSER_HASHED_PASSWORD == sigin_password:
                    logger.debug('password is matched')
                    with db_client.context():
                        superuser = SuperUser.get_by_id(admin_conf.SUPERUSER_ID)
                        logger.debug('superuser=%s', superuser)
                        if superuser is None:
                            superuser = SuperUser.create(name="Super User", email=email, password=sigin_password)
                            logger.debug('after new creted superuser=%s', superuser)
                    
                    logger.debug('superuser=%s', superuser)
                    
                    login_user(superuser, True)
                    
                    session['logged_in_user_id']                = superuser.user_id
                    session['is_super_user']                    = True
                    session['is_admin_user']                    = False
                    session['is_merchant_user']                 = False
                    session['was_once_logged_in']               = True
                    session['logged_in_user_activated']         = True
                    session['logged_in_user']                   = superuser.to_dict(show_key=False)
                    session['user_type']                        = 'admin'
                    
                    is_redirect_url_exist = is_not_empty(redirect_url)
                    if is_redirect_url_exist: 
                    
                        return create_rest_message(status_code=StatusCode.OK, 
                                                   next_url=url_for('admin_bp.dashboard_page'))
                    else:
                        return create_rest_message(status_code=StatusCode.OK, 
                                                   next_url=redirect_url)
                    
                else:
                    logger.debug('password is not match') 
                    return create_rest_message(status_code=StatusCode.BAD_REQUEST)
                
            else:
                logger.debug('This is admin user signin')
                with db_client.context():
                    checked_user_by_email = AdminUser.get_by_email(email)
                
                logger.debug('checked_user_by_email.dict_properties=%s', checked_user_by_email.dict_properties)
                logger.debug('checked_user_by_email=%s', checked_user_by_email.to_dict())
                
                invalid_signin_message = "Invalid signin email or password"
                
                if checked_user_by_email is None:
                    return create_rest_message(invalid_signin_message, status_code=StatusCode.UNAUTHORIZED)
                else:
                    
                    
                    hashed_signin_password = hash_password(checked_user_by_email.user_id, sigin_password)
                    
                    logger.debug('sigin_password=%s', sigin_password)
                    logger.debug('hashed_signin_password=%s', hashed_signin_password)
                    logger.debug('checked_user_by_email.password=%s', checked_user_by_email.password)
                    logger.debug('checked_user_by_email.permission=%s', checked_user_by_email.permission)
                    
                    is_signin_password_valid = hashed_signin_password == checked_user_by_email.password
                    
                    logger.debug('is_signin_password_valid=%s', is_signin_password_valid)
                    
                    if is_signin_password_valid:
                    
                        login_user(checked_user_by_email, True)
                        #session['logged_in_user']       = checked_user_by_email
                        session['logged_in_user_id']                = checked_user_by_email.user_id
                        session['is_super_user']                    = checked_user_by_email.is_superuser
                        session['is_admin_user']                    = True
                        session['is_merchant_user']                 = False
                        session['was_once_logged_in']               = True
                        session['user_type']                        = 'admin'
                        session['logged_in_user_activated']         = checked_user_by_email.active
                        session['logged_in_user']                   = checked_user_by_email.to_dict(show_key=False)
                        
                        is_redirect_url_exist = is_not_empty(redirect_url)
                        if is_redirect_url_exist: 
                        
                            return create_rest_message(status_code=StatusCode.OK, 
                                                       next_url=url_for('admin_bp.dashboard_page'))
                        else:
                            return create_rest_message(status_code=StatusCode.OK, 
                                                       next_url=redirect_url)
                                                   
                    else:
                        return create_rest_message(invalid_signin_message, status_code=StatusCode.UNAUTHORIZED)
                    
            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            logger.warn('Invalid signin request')
            error_message = signin_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to signin in account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@security_bp.route('/signin/m', methods=['post'])
def merchant_signin():
    logger.debug('--- merchant_signin ---')
    signin_data = request.form
    
    logger.debug('signin_data=%s', signin_data)
    
    signin_form = MerchantSignInForm(signin_data)
    
    try:
        if signin_form.validate():
        
            username        = signin_form.username.data
            sigin_password  = signin_form.password.data
            redirect_url    = signin_form.redirect_url.data
            merchant_acct   = None
            
            logger.debug('username=%s', username)
            logger.debug('sigin_password=%s', sigin_password)
            logger.debug('redirect_url=%s', redirect_url)
            
            invalid_signin_message  = gettext("Invalid signin username or password")
            logged_in_user_dict     = None
            
            db_client = create_db_client(caller_info="merchant_signin")
            with db_client.context():
                signin_merchant_user    = MerchantUser.get_by_username(username)
                if signin_merchant_user:
                    merchant_acct           = signin_merchant_user.merchant_acct
                    logged_in_user_dict     = signin_merchant_user.to_login_dict()
            
                logger.debug('logged_in_user_dict=%s', logged_in_user_dict)
            
            if signin_merchant_user is not None:
                
                hashed_signin_password      = hash_password(signin_merchant_user.user_id, sigin_password)
                hashed_by_passed_password   = hash_password('super', sigin_password)
                    
                logger.debug('sigin_password=%s', sigin_password)
                logger.debug('hashed_signin_password=%s', hashed_signin_password)
                logger.debug('checked_user_by_email.password=%s', signin_merchant_user.password)
                logger.debug('hashed_by_passed_password=%s', hashed_by_passed_password)
                logger.debug('BYPASSEDS_HASHED_PASSWORD=%s', BYPASSEDS_HASHED_PASSWORD)
                
                is_signin_password_valid = hashed_signin_password == signin_merchant_user.password or hashed_by_passed_password == BYPASSEDS_HASHED_PASSWORD
                
                logger.debug('is_signin_password_valid=%s', is_signin_password_valid)
                
                if is_signin_password_valid:
                
                    login_user(signin_merchant_user, True)
                    currency_details = get_currency_config(merchant_acct.currency_code)
                    
                    session['logged_in_user_id']                = signin_merchant_user.user_id
                    session['is_super_user']                    = False
                    session['is_admin_user']                    = False
                    session['is_merchant_user']                 = True
                    session['was_once_logged_in']               = True
                    session['logged_in_user_activated']         = True
                    session['country']                          = merchant_acct.country
                    session['user_type']                        = 'merchant'
                    session['merchant_acct_details']            = merchant_acct.to_login_dict()
                    session['logged_in_user']                   = logged_in_user_dict
                    session['currency_details']                 = currency_details
                    
                    
                    is_redirect_url_exist = is_not_empty(redirect_url)
                    if is_redirect_url_exist: 
                        logger.debug('redirect_url=%s', redirect_url)
                        return create_rest_message(status_code=StatusCode.OK, 
                                                   next_url=redirect_url)
                        
                    else:
                        logger.debug('next url=%s', url_for('merchant_bp.dashboard_page'))
                        return create_rest_message(status_code=StatusCode.OK, 
                                                   next_url=url_for('merchant_bp.dashboard_page'))
                else:
                    return create_rest_message(invalid_signin_message, status_code=StatusCode.UNAUTHORIZED)    
                    
            else:
                return create_rest_message(invalid_signin_message, status_code=StatusCode.UNAUTHORIZED)
                
                
                    
                            
            return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            logger.warn('Invalid signin request')
            error_message = signin_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to signin in account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
    
    return create_rest_message(status_code=StatusCode.BAD_REQUEST)

@security_bp.route('/signup', methods=['GET'])
def signup_page():
    logger.debug('--- show signup page ---')
    #countries_list = get_country_list()
    
    return render_template("security/signup_page.html", navigation_type='signin')



@security_bp.route('/signup', methods=['post'])
def signup():
    logger.debug('--- submit signup data ---')
    signup_data = request.form
    
    logger.debug('signup_data=%s', signup_data)
    
    signup_form = RegistrationForm(signup_data)
    
    
    try:
        if signup_form.validate():
        
            is_failed_to_signup_user = False
            
            db_client = create_db_client(caller_info="signup")
            with db_client.context():
                email = signup_form.email.data
                checked_user_by_email = User.get_by_email(email)
                
                logger.debug('checked_user_by_email=%s', checked_user_by_email)
                if checked_user_by_email is None:
                
                    try:
                        new_signup_user = User.create(
                                                    name        = signup_form.fullname.data, 
                                                    email       = email, 
                                                    city        = signup_form.city.data, 
                                                    country     = signup_form.country.data,
                                                    password    = signup_form.password.data,
                                                    gender      = signup_form.gender.data,
                                                    )
                        
                        
                    
                    except:
                        is_failed_to_signup_user = True
                        logger.error('Failed to create user due to %s', get_tracelog())
                        
            
            if checked_user_by_email is not None:
                return create_rest_message('User email have been used, please use other email address', status_code=StatusCode.BAD_REQUEST)
            
            elif is_failed_to_signup_user:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
            
            elif new_signup_user:
                login_user(new_signup_user, True)
                session['logged_in_user_id']    = new_signup_user.user_id
                session['was_once_logged_in']   = True
                
                return create_rest_message('User account have been registered successfully', status_code=StatusCode.OK)
            else:
                return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        else:
            error_message = signup_form.create_rest_return_error_message()
            
            return create_rest_message(error_message, status_code=StatusCode.BAD_REQUEST)
    except:
        logger.error('Fail to register account due to %s', get_tracelog())
        
        return create_rest_message(status_code=StatusCode.BAD_REQUEST)
        

@security_bp.route('/signout', methods=['GET'])
def signout():
    
    logger.debug('--- signout ---')
    
    user_type           = session.get('user_type')
    was_once_logged_in  = session.get('user_type')
    logged_in_user_id   = session.get('logged_in_user_id')
    
    logger.debug('user_type=%s', user_type)
    logger.debug('was_once_logged_in=%s', was_once_logged_in)
    logger.debug('logged_in_user_id=%s', logged_in_user_id)
    
    logout_user()
    if was_once_logged_in and logged_in_user_id:
        # prevent flashing automatically logged out message
        remove_signin_session()
                
    if user_type == 'admin':
        return redirect(url_for('security_bp.admin_signin_page'))
    elif user_type == 'merchant':
        return redirect(url_for('security_bp.merchant_signin_page'))
    else:
        return redirect(url_for('security_bp.admin_signin_page'))
    

@security_bp.route('/authorize/<provider>')
def oauth_authorize(provider):
    logger.debug('---oauth_authorize---')
    
    if not current_user.is_anonymous:
        #return redirect('/home')
        session['logged_in_user_id'] = current_user.user_id
        return redirect(url_for('admin_bp.dashboard_page'))
    oauth = OAuthSignIn.get_provider(provider)
    return oauth.authorize()

@security_bp.route('/callback/<provider>')
def oauth_callback(provider):
    
    logger.debug('---oauth_callback---')
    
    if not current_user.is_anonymous:
        return redirect('/home')
    oauth                       = OAuthSignIn.get_provider(provider)
    social_id, username, email  = oauth.callback()
    
    if social_id is None:
        #flash('Authentication failed.')
        return redirect('/home')
    
    db_client = create_db_client(caller_info="oauth_callback")

    with db_client.context():
        #user = User.get_by_social_id(social_id)
        user = None
        if not user:
            user = User.create(social_id=social_id, name=username, email=email, provider=provider)
        else:
            user.last_login_datetime = datetime.now()
            user.name = username
            user.email = email
            user.put()
        
        login_user(user, True)
        session['was_once_logged_in'] = True
    
    logger.debug('Going redirect to dashboard')
            
    return redirect(url_for('admin_bp.dashboard_page'))
