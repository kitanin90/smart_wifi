from django.db import models
from django.db.models import Sum

from panel.const import BYTES_IN_MB
from django.utils import timezone
from datetime import datetime


class Building(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    address = models.CharField(max_length=255, verbose_name="Адрес")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Корпус'
        verbose_name_plural = 'Корпусы'


class Faculty(models.Model):
    name = models.CharField(max_length=255, verbose_name="Название")
    building = models.ForeignKey("Building", on_delete=models.DO_NOTHING, verbose_name="Корпус")

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Факультет'
        verbose_name_plural = 'Факультеты'


class Client(models.Model):
    lastname = models.CharField(max_length=255, blank=True, verbose_name="Фамилия")
    firstname = models.CharField(max_length=255, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=255, blank=True, verbose_name="Отчество")
    username = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=255, blank=True, verbose_name="Статус")

    sms_auth = models.BooleanField(default=False, verbose_name="СМС авторизация")

    telephone = models.CharField(max_length=255, verbose_name="Телефон")

    faculty = models.ForeignKey("Faculty", blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name="Факультет")

    def fullname(self):
        return "{} {} {}".format(self.lastname, self.firstname, self.patronymic) if not self.sms_auth else self.username

    def __str__(self):
        return self.fullname()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    def get_traffic_from_date(self, date):
        return Session.objects.filter(acctstarttime__gte=date, username=self.username).aggregate(
            download=Sum("acctinputoctets") / BYTES_IN_MB,
            upload=Sum("acctoutputoctets") / BYTES_IN_MB
        )

    def get_time_from_date(self, date):
        return Session.objects.filter(acctstarttime__gte=date, username=self.username).aggregate(
            time=Sum("acctsessiontime") / 60
        )

    def get_password(self):
        return ClientParameter.objects.get(username=self.username, attribute="Cleartext-Password").value

    def get_last_10_sessions(self):
        return Session.objects.filter(username=self.username).order_by("-acctstarttime")[:10]


class ClientParameter(models.Model):
    username = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.username, self.attribute)

    class Meta:
        verbose_name = 'Параметры клиента'
        verbose_name_plural = 'Параметры клиентов'


class ClientReply(models.Model):
    username = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.username, self.attribute)

    class Meta:
        verbose_name = 'Настройки клиента'
        verbose_name_plural = 'Настройки клиентов'


class Group(models.Model):
    name = models.CharField(max_length=64, unique=True)

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class UserGroup(models.Model):
    username = models.CharField(max_length=64)
    groupname = models.CharField(max_length=64)
    priority = models.IntegerField(default=1)

    class Meta:
        verbose_name = 'Группа клиента'
        verbose_name_plural = 'Группы клиентов'


class GroupParameter(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.groupname, self.attribute)

    class Meta:
        verbose_name = 'Параметры группы'
        verbose_name_plural = 'Параметры групп'


class GroupReply(models.Model):
    groupname = models.CharField(max_length=64)
    attribute = models.CharField(max_length=64)
    op = models.CharField(max_length=2)
    value = models.CharField(max_length=255)

    def __str__(self):
        return "{} {}".format(self.groupname, self.attribute)

    class Meta:
        verbose_name = 'Настройки группы'
        verbose_name_plural = 'Настройки групп'


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

    class Meta:
        verbose_name = 'Сессия'
        verbose_name_plural = 'Сессии'

    def get_start_time(self):
        return self.acctstarttime

    def get_end_time(self):
        if self.acctstoptime is None:
            return ""

        return self.acctstoptime

    def get_traffic(self):
        return round((self.acctinputoctets + self.acctoutputoctets) / BYTES_IN_MB)

    def get_router(self):
        return NAS.objects.get(mac=self.calledstationid)

    def get_status(self):
        return "Работает" if self.acctterminatecause == "" else self.acctterminatecause

    def get_client(self):
        return Client.objects.get(username=self.username)

    def get_flows(self):
        start_time = self.acctstarttime.timestamp()
        end_time = self.acctstoptime

        if end_time is None:
            end_time = datetime.today()

        return Flow.objects.filter(srcaddr=self.framedipaddress, unix_secs__gte=start_time,
                                   unix_secs__lte=end_time.timestamp()).order_by("-unix_secs")


class Flow(models.Model):
    unix_secs = models.IntegerField(default=0)
    unix_nsecs = models.IntegerField(default=0)
    sysuptime = models.IntegerField(default=0)
    exaddr = models.CharField(max_length=45, default="0")
    dflows = models.IntegerField(default=0, null=True)
    dpkts = models.IntegerField(default=0)
    doctets = models.IntegerField(default=0)
    first = models.IntegerField(default=0)
    last = models.IntegerField(default=0)
    engine_type = models.IntegerField(default=0)
    engine_id = models.IntegerField(default=0)
    srcaddr = models.CharField(max_length=45, default="0")
    dstaddr = models.CharField(max_length=45, default="0")
    nexthop = models.CharField(max_length=45, default="0")
    input = models.IntegerField(default=0)
    output = models.IntegerField(default=0)
    srcport = models.IntegerField(default=0)
    dstport = models.IntegerField(default=0)
    prot = models.IntegerField(default=0)
    tos = models.IntegerField(default=0)
    tcp_flags = models.IntegerField(default=0)
    src_mask = models.IntegerField(default=0)
    dst_mask = models.IntegerField(default=0)

    class Meta:
        unique_together = ('unix_secs', 'srcaddr', 'dstaddr', 'srcport', 'dstport')

    def get_time(self):
        return timezone.make_aware(datetime.fromtimestamp(self.unix_secs),
                                   timezone.get_current_timezone())


class AuthLog(models.Model):
    username = models.CharField(max_length=64)
    password = models.CharField(max_length=64)
    reply = models.CharField(max_length=32)
    authdate = models.DateTimeField()

    def __str__(self):
        return "{} {}".format(self.username, self.reply)

    class Meta:
        verbose_name = 'Лог авторизации'
        verbose_name_plural = 'Логи авторизации'


class NAS(models.Model):
    name = models.CharField(max_length=32, verbose_name="Название")
    ip = models.CharField(max_length=15, verbose_name="IP")
    type = models.CharField(max_length=30, blank=True, null=True, verbose_name="Тип")
    ports = models.IntegerField(null=True, verbose_name="Порт")
    secret = models.CharField(max_length=60, verbose_name="Токен")
    server = models.CharField(max_length=64, blank=True, null=True, verbose_name="Сервер")
    mac = models.CharField(max_length=50, verbose_name="MAC")

    building = models.ForeignKey("Building", on_delete=models.DO_NOTHING, verbose_name="Корпус")

    def __str__(self):
        return "{} ({})".format(self.name, self.building.name)

    class Meta:
        verbose_name = 'Роутер'
        verbose_name_plural = 'Роутеры'

    def get_traffic_from_date(self, date):
        return Session.objects.filter(acctstarttime__gte=date, calledstationid=self.mac).aggregate(
            download=Sum("acctinputoctets") / BYTES_IN_MB,
            upload=Sum("acctoutputoctets") / BYTES_IN_MB
        )

    def get_last_10_sessions(self):
        return Session.objects.filter(calledstationid=self.mac).order_by("-acctstarttime")[:10]
