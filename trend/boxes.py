# -*- coding: utf-8 -*-
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.utils import timezone
from django.utils.translation import ugettext as _


from suit_dashboard import Box, realtime

from .widgets import MachineInfoWidget, MachineUsageWidget, MemberRegistrations


class MenuBox(Box):
    title = _('Menu')
    template = 'trend/menu.html'

    @property
    def context(self):
        if hasattr(self, '_context'):
            return self._context
        from .site import DashboardSite
        return {'urls': DashboardSite().get_urls()[:5]}


class MachineInfoBox(Box):
    title = _('TWEETS COLLECTED')
    description = _('Counting tweets collected from sources')
    widgets = [MachineInfoWidget()]


class MachineUsageBox(Box):
    title = _('Machine usage')
    widgets = [realtime(MachineUsageWidget())]


class RegistrationsBox(Box):
    title = _('Member registration')
    description = _('The member registration rate over time.')
    widgets = [MemberRegistrations()]


class LoggedInUsersBox(Box):
    title = _('Logged in users')
    template = 'trend/loggedin.html'

    @property
    def context(self):
        sessions = Session.objects.filter(expire_date__gte=timezone.now())
        uid_list = []

        # Build a list of user ids from that query
        for session in sessions:
            data = session.get_decoded()
            uid_list.append(data.get('_auth_user_id', None))

        # Query all logged in users based on id list
        member_list = User.objects.filter(id__in=uid_list)

        return {'logged_in': member_list}
