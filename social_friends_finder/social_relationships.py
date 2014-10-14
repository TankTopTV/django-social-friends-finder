from django.contrib.auth.models import User
from utils import setting

from models import SocialFollow, UserSocialFollow
if setting("SOCIAL_FRIENDS_USING_ALLAUTH", False):
    USING_ALLAUTH = True
    from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken
else:
    USING_ALLAUTH = False

import facebook
import twitter

import logging
logger = logging.getLogger(__name__)


def update(user, provider=None):
    """ Look for this user's relationships with existing users.

    This should be called when a new user joins or connects a social network (you probably don't want to do this
    synchronously - better to trigger it via Celery).
    """

    if not USING_ALLAUTH:
        # TODO: this isn't currently implemented unless you're using django-allauth
        logger.error("Can't update social relationship without django-allauth")
        return

    user_social_accounts = SocialAccount.objects.filter(user=user)
    if provider:
        user_social_accounts = user_social_accounts.filter(provider=provider)
    for social_user in user_social_accounts:
        if social_user.provider == 'twitter':
            new_twitter_relationships(social_user)
        elif social_user.provider == 'facebook':
            new_facebook_relationships(social_user)


def new_facebook_relationships(social_user):
    social_app = SocialApp.objects.get_current('facebook')
    try:
        token = SocialToken.objects.get(app=social_app, account=social_user)
        graph = facebook.GraphAPI(token.token)
        friends = graph.get_connections("me", "friends")
    except Exception, e:
        # TODO! We had a problem getting Facebook info. This could be because the token is no longer valid,
        # in which case we might like the option to alert the user and get them to re-authenticate
        logger.error("Problem getting Facebook data for {0}".format(social_user.user))
        logger.info("{0}".format(e))
        return

    # Friends comes back as a dictionary
    if 'data' not in friends:
        return

    # Putting in a try just in case the data format changes or something
    try:
        friend_ids = tuple(friend['id'] for friend in friends['data'])

        for social_friend in SocialAccount.objects.filter(provider='facebook', uid__in=friend_ids):
            if SocialFollow.new_follow(social_user, social_friend):
                # TODO! Ideally this would trigger a signal so that we can tell the user that they have new friends using this service
                continue
    except:
        pass


def new_twitter_relationships(social_user):
    social_app = SocialApp.objects.get_current('twitter')
    consumer_key = social_app.client_id
    consumer_secret = social_app.secret
    try:
        token = SocialToken.objects.get(app=social_app, account=social_user)
        api = twitter.Api(consumer_key=consumer_key,
                          consumer_secret=consumer_secret,
                          access_token_key=token.token,
                          access_token_secret=token.token_secret)
    except Exception, e:
        # TODO! We had a problem getting Twitter info. This could be because the token is no longer valid,
        # in which case we might like the option to alert the user and get them to re-authenticate
        logger.error("Problem getting Twitter data for {0}".format(social_user.user))
        logger.info("{0}".format(e))
        return

    # For Twitter we might want to notify any existing users who follow this user that she has arrived.
    # This returns up to 5000 followers.  Arguably we should page through this and get more but this will do to get started.
    friends = api.GetFollowerIDs(user_id=social_user.uid, stringify_ids=True)

    # Are any of these followers already on the service?
    social_friends = SocialAccount.objects.filter(provider='twitter', uid__in=friends)
    for social_friend in social_friends:
        if SocialFollow.new_follow(social_friend, social_user):
            # TODO! We might want to tell the friend that this user has joined the service, maybe this should trigger a signal
            continue

    # We also want to set up relationships in the other direction i.e. people this user follows who are already on
    # the service.  We don't send notifications but this could be used to populate, say, a page of the people this user
    # knows who are already on NowVia.

    friends = api.GetFriendIDs(user_id=social_user.uid, stringify_ids=True)

    # Are any of these friends already on the service?
    social_friends = SocialAccount.objects.filter(provider='twitter', uid__in=friends)
    for social_friend in social_friends:
        if social_friend and SocialFollow.new_follow(social_user, social_friend):
            # TODO! We might want to tell the user that this friend is already on the service, again this could trigger a signal
            continue





