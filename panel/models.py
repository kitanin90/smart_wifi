from django.core.exceptions import ObjectDoesNotExist
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


class Group(models.Model):
    name = models.CharField(max_length=255, blank=True, verbose_name="Название")
    # faculty = models.ForeignKey("Faculty", verbose_name="Факультет",  on_delete=models.DO_NOTHING)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = 'Учебная группа'
        verbose_name_plural = 'Учебные группы'


class Client(models.Model):
    lastname = models.CharField(max_length=255, blank=True, verbose_name="Фамилия")
    firstname = models.CharField(max_length=255, blank=True, verbose_name="Имя")
    patronymic = models.CharField(max_length=255, blank=True, verbose_name="Отчество")
    username = models.CharField(max_length=64, unique=True)
    status = models.CharField(max_length=255, blank=True, verbose_name="Статус")

    sms_auth = models.BooleanField(default=False, verbose_name="СМС авторизация")

    telephone = models.CharField(max_length=255, verbose_name="Телефон", blank=True)

    faculty = models.ForeignKey("Faculty", blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name="Факультет")

    group = models.ForeignKey("Group", blank=True, null=True, on_delete=models.DO_NOTHING, verbose_name="Группа")

    def fullname(self):
        return "{} {} {}".format(self.lastname, self.firstname, self.patronymic) if not self.sms_auth else self.username

    def __str__(self):
        return self.fullname()

    class Meta:
        verbose_name = 'Клиент'
        verbose_name_plural = 'Клиенты'

    @staticmethod
    def translit(username):
        ru = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd',
            'е': 'e', 'ё': 'e', 'ж': 'j', 'з': 'z', 'и': 'i', 'й': "i",
            'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o',
            'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u',
            'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh',
            'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'u', 'я': 'ya', '-': '-', ".": "", " ": ""
        }

        username = username.replace("ь", "")
        username = username.replace("ъ", "")

        result = ""

        for s in username:
            if s.isupper():
                result += ru[s.lower()].capitalize()
            else:
                result += ru[s]

        return result

    @staticmethod
    def translit_for_repeater(username_for_repeater):
        ru = {
            'а': 'a', 'б': 'b', 'в': 'v', 'г': 'g', 'д': 'd', 'q': 'q', 'w': 'w', 'e': 'e',
            'е': 'e', 'ё': 'e', 'ж': 'j', 'з': 'z', 'и': 'i', 'й': "i",  'r': 'r', 't': 't', 'y': 'y', 'u': 'u',
            'к': 'k', 'л': 'l', 'м': 'm', 'н': 'n', 'о': 'o', 'i': 'i', 'o': 'o', 'p': 'p', 'a': 'a', 's': 's',
            'п': 'p', 'р': 'r', 'с': 's', 'т': 't', 'у': 'u', 'd': 'd', 'f': 'f', 'g': 'g', 'h': 'h', 'j': 'j',
            'ф': 'f', 'х': 'h', 'ц': 'c', 'ч': 'ch', 'ш': 'sh', 'k': 'k', 'l': 'l', 'z': 'z', 'x': 'x', 'c': 'c',
            'щ': 'shch', 'ы': 'y', 'э': 'e', 'ю': 'u', 'я': 'ya', '-': '-', ".": "", " ": "", '_':'_',  'v': 'v',
            'b': 'b', 'n': 'n', 'm': 'm'
        }

        username_for_repeater = username_for_repeater.replace("ь", "")
        username_for_repeater = username_for_repeater.replace("ъ", "")

        result = ""

        for s in username_for_repeater:
            if s.isupper():
                result += ru[s.lower()].capitalize()
            else:
                result += ru[s]

        return result

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

    @staticmethod
    def translit_pass(value):

        ru = {
            '0': '0', '1': '1', '2': '2', '3': '3', '4': '4', '5': '5', '6': '6', '7': '7', '8': '8', '9': '9',
            'а': 'a', 'a': 'a', 'б': 'b', 'b': 'b', 'в': 'v', 'v': 'v', 'г': 'g', 'g': 'g', 'д': 'd', 'd': 'd',
            'е': 'e', 'e': 'e', 'ё': 'e', 'ж': 'j', 'j': 'j', 'з': 'z', 'z': 'z', 'и': 'i', 'i': 'i', 'й': "i",
            'к': 'k', 'k': 'k', 'л': 'l', 'l': 'l', 'м': 'm', 'm': 'm', 'н': 'n', 'n': 'n', 'о': 'o',
            'o': 'o', 'п': 'p', 'p': 'p', 'р': 'r', 'r': 'r', 'т': 't', 't': 't', 'у': 'u', 'ц': 'c', 'c': 'c',
            'u': 'u', 'ф': 'f', 'f': 'f', 'х': 'h', 'h': 'h', 'ч': 'ch', 'ch': 'ch', 'ш': 'sh', 'с': 's', 's': 's',
            'sh': 'sh', 'щ': 'shch', 'ы': 'y', 'y': 'y', 'э': 'e', 'ю': 'u', 'я': 'ya', '-': '-', '.': '', ' ': '',
            '/': '/'
        }

        value = value.replace("ь", "")
        value = value.replace("ъ", "")

        result = ""

        for s in value:
            if s.isupper():
                result += ru[s.lower()].capitalize()
            else:
                result += ru[s]

        return result


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

    @staticmethod
    def get_value(groupname, paramname, multiply):
        try:
            return int(GroupReply.objects.get(groupname=groupname, attribute=paramname).value) // multiply
        except ObjectDoesNotExist:
            return None


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
    exaddr = models.CharField(max_length=45, default="0")

    srcaddr = models.CharField(max_length=45, default="0")
    dstaddr = models.CharField(max_length=45, default="0")

    srcport = models.IntegerField(default=0)
    dstport = models.IntegerField(default=0)
    prot = models.IntegerField(default=0)

    class Meta:
        unique_together = ('unix_secs', 'srcaddr', 'dstaddr', 'srcport', 'dstport')

    def get_time(self):
        return timezone.make_aware(datetime.fromtimestamp(self.unix_secs),
                                   timezone.get_current_timezone())

    def get_protocol(self):
        if self.prot == 6:
            return "TCP"
        elif self.prot == 17:
            return "UDP"
        else:
            return "Unknown"


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


class Feedback(models.Model):
    username = models.CharField(max_length=64, verbose_name="username")
    telephone = models.CharField(max_length=255, verbose_name="Телефон")
    title = models.CharField(max_length=150, verbose_name="Заголовок")
    description = models.TextField(blank=True, verbose_name="Текст")
    date_pub = models.DateTimeField(auto_now_add=True, verbose_name="Дата публикации")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ["-date_pub"]
