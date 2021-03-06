from django.contrib import admin

from panel.models import Building, Faculty, Client, ClientParameter, Session, NAS, ClientReply, AuthLog, \
    GroupParameter, GroupReply, UserGroup, Flow, Group

admin.site.register(Building)
admin.site.register(Faculty)
admin.site.register(Group)

admin.site.register(Client)
admin.site.register(ClientParameter)
admin.site.register(ClientReply)

admin.site.register(GroupParameter)
admin.site.register(GroupReply)

admin.site.register(UserGroup)

admin.site.register(Session)
admin.site.register(Flow)

admin.site.register(NAS)

admin.site.register(AuthLog)


