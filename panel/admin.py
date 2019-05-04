from django.contrib import admin

from panel.models import Building, Faculty, Client, ClientParameter, Session, NAS, ClientReply, AuthLog, Group, \
    GroupParameter, GroupReply, UserGroup

admin.site.register(Building)
admin.site.register(Faculty)

admin.site.register(Client)
admin.site.register(ClientParameter)
admin.site.register(ClientReply)

admin.site.register(Group)
admin.site.register(GroupParameter)
admin.site.register(GroupReply)

admin.site.register(UserGroup)

admin.site.register(Session)

admin.site.register(NAS)

admin.site.register(AuthLog)
