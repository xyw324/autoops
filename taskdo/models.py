from django.db import models


# 用户登录信息表(虚拟机)
class ConnectionInfo(models.Model):
    # 用户连接相关信息
    ssh_username = models.CharField(max_length=10, default='', verbose_name='ssh用户名', null=True)
    ssh_userpasswd = models.CharField(max_length=40, default='', verbose_name='ssh用户密码', null=True)
    # ssh_hostip = models.CharField(max_length=40, default='', verbose_name='ssh登录的ip', null=True)
    ssh_host_port = models.CharField(max_length=10, default='', verbose_name='ssh登录的端口', null=True)
    # ssh_rsa = models.CharField(max_length=64, default='', verbose_name='ssh私钥')
    # rsa_pass = models.CharField(max_length=64, default='', verbose_name='私钥的密钥')
    # 0-登录失败,1-登录成功
    ssh_status = models.IntegerField(default=0, verbose_name='用户连接状态,0-登录失败,1-登录成功')
    # 0-密码登录, 1-rsa登录,2-dsa登录,3-ssh_rsa登录
    ssh_type = models.IntegerField(default=0, verbose_name='用户连接类型, 0-密码登录, 1-rsa登录,2-dsa登录,3-ssh_rsa登录')
    # 唯一对象标示
    sn_key = models.CharField(max_length=256, verbose_name="唯一设备ID", default="")

    def __str__(self):
        return self.ssh_username

    class Meta:
        verbose_name = '用户登录信息表'
        verbose_name_plural = verbose_name


# 虚拟设备信息
class VirtualServerInfo(models.Model):
    # server_name = models.CharField(max_length=15, verbose_name=u'服务器名')
    server_ip = models.CharField(max_length=40, verbose_name='服务器IP')
    # 机器的类型 0=kvm,2=虚拟资产,3=网络设备 0=其他类型(未知)
    # server_type = models.CharField(max_length=80, default='', verbose_name=u'服务器类型:kvm,Vmware,Docker,others')
    system_type = models.CharField(max_length=32, default='centos', verbose_name='操作系统类型')
    system_ver = models.CharField(max_length=30, default='', verbose_name='操作系统版本')
    sys_hostname = models.CharField(max_length=15, verbose_name='操作系统主机名')
    mac = models.CharField(max_length=512, default='', verbose_name='MAC地址')
    sn = models.CharField(max_length=256, verbose_name=u'SN-主机的唯一标识', default='')
    group_name = models.ForeignKey(to='HostGroup')
    # 用户登录系统信息
    conn_vir = models.ForeignKey(to='ConnectionInfo')

    def __str__(self):
        return self.server_ip

    class Meta:
        verbose_name = '虚拟设备表'
        verbose_name_plural = verbose_name


class HostGroup(models.Model):
    group = models.CharField(max_length=32, verbose_name='主机组名称')

    def __str__(self):
        return self.group

    class Meta:
        verbose_name = '主机组表'
        verbose_name_plural = verbose_name
