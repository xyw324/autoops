from django.shortcuts import HttpResponse, render
from django import views
import json
from taskdo import models
from taskdo import utils
from taskdo.utils.base import RedisCon, MongoCon
from taskdo.utils import ansible_api
import traceback


class AdhocTask(views.View):
    def get(self, request):
        return render(request, 'info.html')

    def post(self, request):
        result = {}
        jobs = request.body
        init_jobs = json.loads(jobs)
        # {'taskid':'289675','mod_type':'shell','exec_args':'sleep 100','group_name':'test','sn_key':['b847h4774b']}
        taskid = init_jobs.get("taskid")
        mod_type = ["mod_type"] if not init_jobs["mod_type"] else "shell"
        sn_keys = init_jobs["sn_key"]
        exec_args = init_jobs[u"exec_args"]
        group_name = init_jobs[u"group_name"] if not init_jobs[u"group_name"] else "test"
        if not sn_keys or not taskid or not exec_args:
            result = {'status': "failed", "code": "002", "info": u"传入的参数mod_type不匹配！"}
            return HttpResponse(json.dumps(result), content_type='application/json')
        else:
            adlog = MongoCon.InsertAdhocLog(taskid=taskid)
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
                    cn = utils.prpcrypt()
                    hosts_ip = []
                    for host in hosts_obj:
                        sshpasswd = cn.decrypt(host.ssh_userpasswd)
                        if host.ssh_type in (1, 2):
                            hosts_list.append(
                                {"hostname": host.sn_key, "ip": host.ssh_hostip, "port": host.ssh_host_port,
                                 "username": host.ssh_username, "ssh_key": host.ssh_rsa})
                            hosts_ip.append(host.sn_key)
                    resource[group_name] = {"hosts": hosts_list, "vars": vars_dic}
                    adlog.record(statuid=10004)
                    # 任务锁检查
                    lockstatus = RedisCon.DsRedis.get(rkey='tasklock')
                    if lockstatus is False or lockstatus == '1':
                        adlog.record(statuid=40005)
                    else:
                        # 开始执行任务
                        RedisCon.DsRedis.setlock("tasklock", 1)
                        job = ansible_api.ANSRunner(resource=resource, redisKey='1')
                        job.run_model(host_list=hosts_ip, module_name=mod_type, module_args=exec_args)
                        res = job.get_model_result()
                        adlog.record(statuid=19999, input_con=res)
                        adlog.record(statuid=20000)
                        RedisCon.DsRedis.setlock("tasklock", 0)
                        result = {"status": "success", "info": res}
            except Exception as e:
                print(traceback.print_exc())
                RedisCon.DsRedis.setlock("tasklock", 0)
                result = {"status": "failed", "code": "005", "info": e}
            finally:
                return HttpResponse(json.dumps(result), content_type="application/json")


class AdhocTaskLog(views.View):

    def get(self, request):
        pass

    def post(self, request):
        return HttpResponse('OK')
