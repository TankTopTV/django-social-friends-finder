# -*- coding: utf-8 -*-
import datetime
from south.db import db
from south.v2 import SchemaMigration
from django.db import models


class Migration(SchemaMigration):

    def forwards(self, orm):
        # Adding model 'SocialFollow'
        db.create_table(u'social_friends_finder_socialfollow', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('social_user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='social_followers', to=orm['socialaccount.SocialAccount'])),
            ('follows', self.gf('django.db.models.fields.related.ForeignKey')(related_name='social_followees', to=orm['socialaccount.SocialAccount'])),
        ))
        db.send_create_signal(u'social_friends_finder', ['SocialFollow'])

        # Adding unique constraint on 'SocialFollow', fields ['social_user', 'follows']
        db.create_unique(u'social_friends_finder_socialfollow', ['social_user_id', 'follows_id'])

        # Adding model 'UserSocialFollow'
        db.create_table(u'social_friends_finder_usersocialfollow', (
            (u'id', self.gf('django.db.models.fields.AutoField')(primary_key=True)),
            ('user', self.gf('django.db.models.fields.related.ForeignKey')(related_name='followers', to=orm['auth.User'])),
            ('follows', self.gf('django.db.models.fields.related.ForeignKey')(related_name='followees', to=orm['auth.User'])),
        ))
        db.send_create_signal(u'social_friends_finder', ['UserSocialFollow'])

        # Adding unique constraint on 'UserSocialFollow', fields ['user', 'follows']
        db.create_unique(u'social_friends_finder_usersocialfollow', ['user_id', 'follows_id'])


    def backwards(self, orm):
        # Removing unique constraint on 'UserSocialFollow', fields ['user', 'follows']
        db.delete_unique(u'social_friends_finder_usersocialfollow', ['user_id', 'follows_id'])

        # Removing unique constraint on 'SocialFollow', fields ['social_user', 'follows']
        db.delete_unique(u'social_friends_finder_socialfollow', ['social_user_id', 'follows_id'])

        # Deleting model 'SocialFollow'
        db.delete_table(u'social_friends_finder_socialfollow')

        # Deleting model 'UserSocialFollow'
        db.delete_table(u'social_friends_finder_usersocialfollow')


    models = {
        u'auth.group': {
            'Meta': {'object_name': 'Group'},
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '80'}),
            'permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'})
        },
        u'auth.permission': {
            'Meta': {'ordering': "(u'content_type__app_label', u'content_type__model', u'codename')", 'unique_together': "((u'content_type', u'codename'),)", 'object_name': 'Permission'},
            'codename': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'content_type': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['contenttypes.ContentType']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '50'})
        },
        u'auth.user': {
            'Meta': {'object_name': 'User'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'email': ('django.db.models.fields.EmailField', [], {'max_length': '75', 'blank': 'True'}),
            'first_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'groups': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Group']", 'symmetrical': 'False', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'is_active': ('django.db.models.fields.BooleanField', [], {'default': 'True'}),
            'is_staff': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'is_superuser': ('django.db.models.fields.BooleanField', [], {'default': 'False'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'default': 'datetime.datetime.now'}),
            'last_name': ('django.db.models.fields.CharField', [], {'max_length': '30', 'blank': 'True'}),
            'password': ('django.db.models.fields.CharField', [], {'max_length': '128'}),
            'user_permissions': ('django.db.models.fields.related.ManyToManyField', [], {'to': u"orm['auth.Permission']", 'symmetrical': 'False', 'blank': 'True'}),
            'username': ('django.db.models.fields.CharField', [], {'unique': 'True', 'max_length': '30'})
        },
        u'contenttypes.contenttype': {
            'Meta': {'ordering': "('name',)", 'unique_together': "(('app_label', 'model'),)", 'object_name': 'ContentType', 'db_table': "'django_content_type'"},
            'app_label': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'model': ('django.db.models.fields.CharField', [], {'max_length': '100'}),
            'name': ('django.db.models.fields.CharField', [], {'max_length': '100'})
        },
        u'social_friends_finder.socialfollow': {
            'Meta': {'unique_together': "(('social_user', 'follows'),)", 'object_name': 'SocialFollow'},
            'follows': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'social_followees'", 'to': u"orm['socialaccount.SocialAccount']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'social_user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'social_followers'", 'to': u"orm['socialaccount.SocialAccount']"})
        },
        u'social_friends_finder.socialfriendlist': {
            'Meta': {'object_name': 'SocialFriendList'},
            'friend_ids': ('django.db.models.fields.CommaSeparatedIntegerField', [], {'max_length': '21845', 'blank': 'True'}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user_social_auth': ('django.db.models.fields.related.OneToOneField', [], {'related_name': "'social_auth'", 'unique': 'True', 'to': u"orm['socialaccount.SocialAccount']"})
        },
        u'social_friends_finder.usersocialfollow': {
            'Meta': {'unique_together': "(('user', 'follows'),)", 'object_name': 'UserSocialFollow'},
            'follows': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'followees'", 'to': u"orm['auth.User']"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'related_name': "'followers'", 'to': u"orm['auth.User']"})
        },
        u'socialaccount.socialaccount': {
            'Meta': {'unique_together': "(('provider', 'uid'),)", 'object_name': 'SocialAccount'},
            'date_joined': ('django.db.models.fields.DateTimeField', [], {'auto_now_add': 'True', 'blank': 'True'}),
            'extra_data': ('allauth.socialaccount.fields.JSONField', [], {'default': "'{}'"}),
            u'id': ('django.db.models.fields.AutoField', [], {'primary_key': 'True'}),
            'last_login': ('django.db.models.fields.DateTimeField', [], {'auto_now': 'True', 'blank': 'True'}),
            'provider': ('django.db.models.fields.CharField', [], {'max_length': '30'}),
            'uid': ('django.db.models.fields.CharField', [], {'max_length': '255'}),
            'user': ('django.db.models.fields.related.ForeignKey', [], {'to': u"orm['auth.User']"})
        }
    }

    complete_apps = ['social_friends_finder']