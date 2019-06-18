from django.shortcuts import HttpResponse, render
from django import views
import time
import json
from taskdo import models
from taskdo.utils.base import MongoCon
from django_redis import get_redis_connection
from taskdo.utils import ansible_api
import traceback


class AdhocTask(views.View):
    def get(self, request):
        hostgroup_list = models.HostGroup.objects.all()
        return render(request, 'info.html', {'hostgroups': hostgroup_list})

    def post(self, request):
        result = {}
        current_time = time.time()
        current_second = str(current_time).split(".")[0]
        init_jobs = {'mod_type': 'shell', 'exec_args': 'touch /tmp/a.txt', 'group_name': 'test01', 'sn_key': []}
        init_jobs['taskid'] = current_second
        ip_list = request.POST.get("iplist")
        for i in ip_list.split():
            host_obj = models.VirtualServerInfo.objects.filter(server_ip=i)[0]
            if host_obj:
                current_sn_keys = host_obj.sn
                init_jobs['sn_key'].append(current_sn_keys)
        # {'taskid':'289675','mod_type':'shell','exec_args':'sleep 100','group_name':'test','sn_key':['b847h4774b']}
        taskid = init_jobs.get("taskid")
        mod_type = ["mod_type"] if not init_jobs["mod_type"] else "shell"
        sn_keys = init_jobs["sn_key"]
        exec_args = init_jobs["exec_args"]
        group_name = init_jobs[u"group_name"] if not init_jobs[u"group_name"] else "test"
        if not sn_keys or not taskid or not exec_args:
            result = {'status': "failed", "code": "002", "info": u"传入的参数mod_type不匹配！"}
            return HttpResponse(json.dumps(result), content_type='application/json')
        else:
            adlog = MongoCon.InsertAdhocLog(taskid=taskid)
        redis = get_redis_connection("default")
        if mod_type not in ['shell', 'yum', 'copy']:
            result = {'status': "failed", "code": "003", "info": u"传入的参数不完整！"}
            adlog.record(statuid=10008)
        else:
            try:
                sn_keys = set(sn_keys)
                hosts_obj = models.ConnectionInfo.objects.filter(sn_key__in=sn_keys)
                adlog.record(statuid=10000)
                if len(sn_keys) != len(hosts_obj):
                    adlog.record(statuid=40004)
                else:
                    adlog.record(statuid=10002)
                    resource = {}
                    hosts_list = []
                    vars_dic = {}
                    # cn = prpcrypt()
                    hosts_ip = []
                    for host in hosts_obj:
                        sshpasswd = host.ssh_userpasswd
                        # sshpasswd = cn.decrypt(ssh_password)
                        if host.ssh_type in (0, 1, 2):
                            hosts_list.append(
                                {"hostname": host.sn_key, "ip": host.ssh_hostip, "port": host.ssh_host_port,
                                 "username": host.ssh_username, "password": sshpasswd})
                            hosts_ip.append(host.ssh_hostip)
                    resource[group_name] = {"hosts": hosts_list, "vars": vars_dic}
                    adlog.record(statuid=10004)
                    # 任务锁检查
                    lockstatus = redis.get('tasklock')
                    if lockstatus is False or lockstatus == '1':
                        adlog.record(statuid=40005)
                    else:
                        # 开始执行任务
                        redis.set("tasklock", 1)
                        print(redis.get('tasklock'))
                        job = ansible_api.ANSRunner(resource=resource, redisKey='1')
                        job.run_model(host_list=hosts_ip, module_name=mod_type, module_args=exec_args)
                        res = job.get_model_result()
                        adlog.record(statuid=19999, input_con=res)
                        adlog.record(statuid=20000)
                        redis.set("tasklock", 0)
                        result = {"status": "success", "info": res}
                        print(result)
            except Exception as e:
                print(traceback.print_exc())
                redis.set("tasklock", 0)
                result = {"status": "failed", "code": "005", "info": e}
                print(result)
            finally:
                return HttpResponse(json.dumps(result), content_type="application/json")
        # return HttpResponse('OK')


# Create your views here.
def adhoc_task_log(request):
    if request.method == "GET":
        taskid = request.GET.get("taskid")
        result = {}
        if taskid:
            rlog = MongoCon.InsertAdhocLog(taskid=taskid)
            res = rlog.getrecord()
            print(res)
            result = {"status": "success", 'taskid': taskid, "info": res}
        else:
            result = {"status": "failed", "info": u"没有传入taskid值"}
        res = json.dumps(result)
        return HttpResponse(result, content_type="application/json")
