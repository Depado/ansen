# -*- coding: utf-8 -*-

from flask import redirect, url_for
from flask_login import current_user
from flask_admin import AdminIndexView, expose


class AuthMixin(object):
    """
    Mixin used to prevent access to model admins if the user isn't a superuser.
    """
    def is_accessible(self):
        return not current_user.is_anonymous and current_user.is_superuser


class AuthIndex(AdminIndexView):
    """
    Onlys allow access to the admin interface if the user is logged in and is a superuser.
    """
    @expose('/')
    def index(self):
        if not current_user.is_anonymous and current_user.is_superuser:
                return super(AuthIndex, self).index()
        return redirect(url_for('index'))
