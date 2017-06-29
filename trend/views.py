import calendar
import time
import math
from suit_dashboard import DashboardView, Grid, Row, Column, Box, Widget, realtime
import json
from trend.boxes import MachineUsageBox, MachineInfoBox, MenuBox, RegistrationsBox, LoggedInUsersBox
from trend.widgets import RandomCurveWidget
from django.shortcuts import render
from datetime import datetime, timedelta
#from trend.models import (Foo, Ref)

"""
def fooview(request):
    foos = Foo.objects.all()
    refs = Ref.objects.all()
    return render(
      request, 'trend/foo.html',
      {'types_list': foos, 'refs': refs}
    )

def search(request):
    if request.is_ajax():
        tags = request.GET.getlist('tags[]', '')
        #print(tags)
        if tags != '':
            results = Ref.objects.filter(foo__name__in=tags).distinct()
            return render(
              request, 'trend/random_curve.html',
              {'results': results, 'tags': tags}
            )
    return render(request, 'random_curve.html', {})
"""

class HomeView(DashboardView):
    template_name = 'trend/main.html'
    crumbs = ({'url': 'admin:index', 'name': 'Home'}, )
    grid = Grid(Row(Column(MenuBox())))


class MachineView(HomeView):
    crumbs = ({'url': 'admin:overview', 'name': 'Overview'}, )
    grid = Grid(
        Row(
            Column(MachineInfoBox(), width=6)))


class UserView(HomeView):
    crumbs = ({'url': 'admin:users', 'name': 'Users'}, )
    grid = Grid(
        Row(
            Column(RegistrationsBox(), width=6),
            Column(LoggedInUsersBox(), width=6)))


class DemoView(HomeView):
    crumbs = ({'url': 'admin:demo1', 'name': 'Demo boxes'}, )
    grid = Grid(
        Row(
            Column(
                Box(title='Demo paragraph', widgets=[Widget(
                    html_id='paragraph_widget',
                    content='This is an example of paragraph render.',
                    template='trend/paragraph.html')]),
                Box(title='Demo list', widgets=[Widget(
                    html_id='list_widget',
                    content=['This is', 'an example of', 'list render.'],
                    template='trend/list.html')]), width=6),
            Column(
                Box(title='Demo table', widgets=[Widget(
                    html_id='table_widget',
                    content=[
                        ['This', 'is', 'an example'],
                        ['of', 'table', 'render']],
                    template='trend/table.html')]), width=6)))

def gen_data(param, speed, v0):
    data = [v0]
    for i in range(14):
        val =+ abs(math.sin(i*speed+param))+data[-1]
        data.append(val)
    return data

class RandomCurveView(DemoView):
    crumbs = ({'url': 'admin:curve', 'name': 'Trends'},)
    grid = Grid(
        Row(Column(Box(widgets=[realtime(RandomCurveWidget())]))))

    def get_context_data(self, **kwargs):
        context = super(RandomCurveView, self).get_context_data(**kwargs)
        context["page"] = self.request.GET.get("page") or "Trending now"
        base = datetime.now()
        date_list = [calendar.timegm((base-timedelta(hours=3*x)).utctimetuple()) for x in range(0, 15)[1:]]
        data = []
        context["data"] = data #json.dumps(data)
        return context
