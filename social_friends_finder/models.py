from django.db import models
from utils import setting

if setting("SOCIAL_FRIENDS_USING_ALLAUTH", False):
    USING_ALLAUTH = True
    from allauth.socialaccount.models import SocialAccount as UserSocialAuth
    from allauth.socialaccount.models import SocialAccount
else:
    USING_ALLAUTH = False
    from social_auth.models import UserSocialAuth
from django.contrib.auth.models import User
from social_friends_finder.utils import SocialFriendsFinderBackendFactory


class SocialFriendsManager(models.Manager):

    def assert_user_is_social_auth_user(self, user):
        if not isinstance(user, UserSocialAuth):
            raise TypeError("user must be UserSocialAuth instance, not %s" % user)

    def fetch_social_friend_ids(self, social_auth_user):
        """
        fetches the user's social friends from its provider
        user is an instance of UserSocialAuth
        returns collection of ids

        this method can be used asynchronously as a background process (celery)
        """

        # Type check
        self.assert_user_is_social_auth_user(social_auth_user)

        # Get friend finder backend
        friends_provider = SocialFriendsFinderBackendFactory.get_backend(social_auth_user.provider)

        # Get friend ids
        friend_ids = friends_provider.fetch_friend_ids(social_auth_user)

        return friend_ids

    def existing_social_friends(self, user_social_auth=None, friend_ids=None):
        """
        fetches and matches social friends
        if friend_ids is None, then fetches them from social network

        Return:
            User collection
        """
        # Type check
        self.assert_user_is_social_auth_user(user_social_auth)

        if not friend_ids:
            friend_ids = self.fetch_social_friend_ids(user_social_auth)

        # Convert comma sepearated string to the list
        if isinstance(friend_ids, basestring):
            friend_ids = eval(friend_ids)

        # Match them with the ones on the website
        if USING_ALLAUTH:
            return User.objects.filter(socialaccount__uid__in=friend_ids).all()
        else:
            return User.objects.filter(social_auth__uid__in=friend_ids).all()

    def get_or_create_with_social_auth(self, social_auth):
        """
        creates and saves model instance with collection of UserSocialAuth

        Raise:
            NotImplemetedError
        """
        # Type check
        self.assert_user_is_social_auth_user(social_auth)

        # Fetch the record
        try:
            social_friend_list = self.filter(user_social_auth=social_auth).get()
        except:
            # if no record found, create a new one
            friend_ids = self.fetch_social_friend_ids(social_auth)

            social_friend_list = SocialFriendList()
            social_friend_list.friend_ids = friend_ids
            social_friend_list.user_social_auth = social_auth
            social_friend_list.save()

        return social_friend_list

    def get_or_create_with_social_auths(self, social_auths):
        """
        creates and saves model instance with collection of UserSocialAuth

        Raise:
            NotImplemetedError
        """
        social_friend_coll = []
        for sa in social_auths:
            social_friend = self.get_or_create_with_social_auth(sa)
            social_friend_coll.append(social_friend)

        return social_friend_coll


class SocialFriendList(models.Model):

    user_social_auth = models.OneToOneField(UserSocialAuth, related_name="social_auth")
    friend_ids = models.CommaSeparatedIntegerField(max_length=21845, blank=True, help_text="friends ids separated by commas")

    objects = SocialFriendsManager()

    def __unicode__(self):
        return "%s on %s" % (self.user_social_auth.user.username, self.user_social_auth.provider)

    def existing_social_friends(self):
        return SocialFriendList.objects.existing_social_friends(self.user_social_auth, self.friend_ids)

class SocialFollow(models.Model):
    # User A follows / is interested in user B on social network
    # This is unidirectional to allow for networks like Twitter, where B might not give a monkeys about A
    # So where relationships are two-way friendships (like Facebook) there need to be two entries in this table
    social_user = models.ForeignKey(SocialAccount, related_name="social_followees")
    follows = models.ForeignKey(SocialAccount, related_name="social_followers")

    # A pair of users could have multiple relationships on different social networks.
    # But there should only be one of these between any pair of IDs because they refer to SocialAccount.
    class Meta:
        unique_together = ('social_user', 'follows')

    @classmethod
    def new_follow(cls, social_user, social_follows):
        # Return False if we already know that this user follows the other on any social network

        # These social accounts had better be on the same social network
        assert(social_user.provider == social_follows.provider)
        provider = social_user.provider

        try:
            sf = cls.objects.get(social_user=social_user, follows=social_follows)
            return False
        except SocialFollow.DoesNotExist:
            pass

        sf = SocialFollow()
        sf.social_user = social_user
        sf.follows = social_follows
        sf.save()

        # For Facebook, a relationship is always two-way (if I am friends with you, you're friends with me too)
        # TODO!! Should have a more generic way of saying whether a follow relationship is symmetrical
        if provider == "facebook":
            sf2 = SocialFollow()
            sf2.social_user = social_follows
            sf2.follows = social_user
            sf2.save()

        # Now check to see if this relationship already exists at a user level.  (There might be a previously-existing
        # follow based on knowing each other through another social network)
        try:
            usf = UserSocialFollow.objects.get(user=social_user.user, follows=social_follows.user)
            return False

        except UserSocialFollow.DoesNotExist:
            usf = UserSocialFollow()
            usf.user = social_user.user
            usf.follows = social_follows.user
            usf.save()

            if provider == "facebook":
                usf2 = UserSocialFollow()
                usf2.user = social_follows.user
                usf2.follows = social_user.user
                usf2.save()

            return True # It's a new following relationship


class UserSocialFollow(models.Model):
    # User A follows / is interested in user B because of a relationship on a social network
    # Again this is unidirectional
    user = models.ForeignKey(User, related_name="followees")
    follows = models.ForeignKey(User, related_name="followers")

    class Meta:
        unique_together = ('user', 'follows')

    def __unicode__(self):
        return "{0} follows {1}".format(self.user, self.follows)




