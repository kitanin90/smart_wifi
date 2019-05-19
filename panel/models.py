from django.db import models
from django.db.models import Sum

from panel.const import BYTES_IN_MB


class Building(models.Model):
    name = models.CharField(max_length=255)
    address = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Faculty(models.Model):
    name = models.CharField(max_length=255)
    building = models.ForeignKey("Building", on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name


class Client(models.Model):
    lastname = models.CharField(max_length=255)
    firstname = models.CharField(max_length=255)
    patronymic = models.CharField(max_length=255)
    username = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=255)

    telephone = models.CharField(max_length=255)

    faculty = models.ForeignKey("Faculty", on_delete=models.DO_NOTHING)

    def fullname(self):
        return "{} {} {}".format(self.lastname, self.firstname, self.patronymic)

    def __str__(self):
        return self.fullname()

    def get_traffic_from_date(self, date):
        return Session.objects.filter(acctstarttime__gte=date, username=self.username).aggregate(
            download=Sum("acctinputoctets") / BYTES_IN_MB,
            upload=Sum("acctoutputoctets") / BYTES_IN_MB
        )


class ClientParameter(models.Model):
    username = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.username, self.attribute)


class ClientReply(models.Model):
    username = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.username, self.attribute)


class Group(models.Model):
    name = models.CharField(max_length=64, unique=True)


class UserGroup(models.Model):
    username = models.CharField(max_length=64)
    groupname = models.CharField(max_length=64)
    priority = models.IntegerField(default=1)


class GroupParameter(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.groupname, self.attribute)


class GroupReply(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.groupname, self.attribute)


class Session(models.Model):
    acctsessionid = models.CharField(max_length=64)
    acctuniqueid = models.CharField(max_length=32)

    username = models.CharField(max_length=64)

    realm = models.CharField(max_length=64, null=True)

    nasipaddress = models.CharField(max_length=15)
    nasportid = models.CharField(max_length=15, null=True)
    nasporttype = models.CharField(max_length=32, null=True)

    acctstarttime = models.DateTimeField(null=True)
    acctupdatetime = models.DateTimeField(null=True)
    acctstoptime = models.DateTimeField(null=True)

    acctinterval = models.IntegerField(null=True)
    acctsessiontime = models.IntegerField(null=True)

    acctauthentic = models.CharField(max_length=32, null=True)

    connectinfo_start = models.CharField(max_length=50, null=True)
    connectinfo_stop = models.CharField(max_length=50, null=True)

    acctinputoctets = models.BigIntegerField(null=True)
    acctoutputoctets = models.BigIntegerField(null=True)

    calledstationid = models.CharField(max_length=50)
    callingstationid = models.CharField(max_length=50)

    acctterminatecause = models.CharField(max_length=32)

    servicetype = models.CharField(max_length=32, null=True)
    framedprotocol = models.CharField(max_length=32, null=True)
    framedipaddress = models.CharField(max_length=15)


class AuthLog(models.Model):
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    reply = models.CharField(max_length=32)
    authdate = models.DateTimeField()

    def __str__(self):
        return "{} {}".format(self.username, self.reply)


class NAS(models.Model):
    name = models.CharField(max_length=32)
    ip = models.CharField(max_length=15)
    type = models.CharField(max_length=30, blank=True, null=True)
    ports = models.IntegerField(null=True)
    secret = models.CharField(max_length=60)
    server = models.CharField(max_length=64, blank=True, null=True)
    mac = models.CharField(max_length=50)

    building = models.ForeignKey("Building", on_delete=models.DO_NOTHING)

    def __str__(self):
        return "{} ({})".format(self.name, self.building.name)

    def get_traffic_from_date(self, date):
        return Session.objects.filter(acctstarttime__gte=date, calledstationid=self.mac).aggregate(
            download=Sum("acctinputoctets") / BYTES_IN_MB,
            upload=Sum("acctoutputoctets") / BYTES_IN_MB
        )
