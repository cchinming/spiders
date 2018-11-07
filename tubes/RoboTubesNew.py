#-*- coding: UTF-8 -*-
import sys
reload(sys)
sys.setdefaultencoding('utf-8')
import os
currentUrl = os.path.dirname(__file__)
parentUrl = os.path.abspath(os.path.join(currentUrl, os.pardir))
sys.path.append(parentUrl)
from spiders.RoboSpider import Robo
from middles.middleAssist import mysqlAssist, logAsisst,ssdbAssist
from items.iMqIMData import iMqIMDataCollectItem
from BaseTubes import  BaseTubes
import time
import threading
tlock = threading.Lock()
DEFAULT_NAME_PREFIX = "test_"

class RoboTubes(BaseTubes):
    def __init__(self, platid=None, taskid=None, objid=None,logger=None):
        BaseTubes.__init__(self, platid = platid, taskid= taskid,
                           objid =  objid)
        self.obj = Robo()
        self.sql = mysqlAssist.immysql()
        self.ssdb= ssdbAssist.SSDBsession()
        self.channelCode = None
        self.redis = ""
        self.Logger = logAsisst.imLog(logger)()
        self.pick_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())

    def tubes_allchannel(self):
        for i in self.obj.parseChannelItem():
            if "R" in i["code"]:
                self.channelCode = i["code"]
                self.sql.insert(tbName="t_ext_data_channel",
                                channel_name = i["source"],
                                plat_id = self.plat_id,
                                channel_code = i["code"])

                self.tubes_menus(i["code"])

    def tubes_menus(self, code):
        for i in self.obj.parseItem(code):
            if i["value"]:
                self.sql.insert(tbName="t_ext_plat_menu",
                                plat_id = self.plat_id,
                                channel_code = self.channelCode,
                                name = i["source"],
                                code = i["code"],
                                p_code = None if code == self.channelCode else code)
                self.tubes_menus(i["code"])
            else:
                self.sql.insert(tbName="t_ext_plat_menu",
                                plat_id=2,
                                channel_code=self.channelCode,
                                name=i["source"],
                                code=i["code"],
                                p_code=code,
                                ext=i["ext"])

    def tubes_detail(self, code, **kwargs):

        try:
            dataflow = self.obj.parse(code=code, retries=0)


            data = map(None, dataflow["data"].keys(), dataflow["data"].values())
            tlock.acquire()
            self.sql.insert(tbName="t_ext_data_obj",
                            plat_id = self.plat_id,
                            name = dataflow["ext"]["name"],
                            code = kwargs["pcode"],
                            frequence_mode = dataflow["frequency"],
                            frequence = dataflow["value"],
                            unit = dataflow["unit"],
                            data_source = dataflow["source"],
                            note = dataflow["pcode"],
                            update_time = dataflow["update_time"],
                            start_time  = dataflow["start_time"],
                            end_time    = dataflow["end_time"],
                            is_end = dataflow["is_end"],
                            ext = str(dataflow["ext"]),
                            pick_time = self.pick_time)
            tid = self.sql.query("select id from t_ext_data_obj where \
                           code='%s' and plat_id=%s"%(kwargs["pcode"], self.plat_id))
            tt = "insert into t_ext_data_node( obj_id, time_t, amo) values (%s" % tid[0][0]

            tt = tt + ",%s, %s)"
            print(tt)

            self.ssdb.setname("s_o_d_i_%d"%tid[0][0])
            print(self.ssdb.name)
            map(self.ssdb.Hset, data)


            self.sql.executemany(tt, tuple(data))
            tlock.release()
        except Exception as e:
            print(e)
        else:
            return dataflow["data"]

    def tubes_heartbeat(self, offset,feature= None):

        if feature is None:
            tmp = self.sql.query("select code, ext from t_ext_plat_menu\
                                    where ext like '%%{%%' order by id\
                                     limit %d, 1000" % (offset))
        else:
            tmp = self.sql.query("select code, ext from t_ext_plat_menu\
                                where ext like '%%{%%' and channel_code='%s' order by id\
                                 limit %d, 1000" % ( feature, offset))

        for i in tmp:
            yield i

    def tmp_crawl(self, feature = None):
        count = feature["offset"]*10000
        MAX_COUNT = count + 10000
        retry = 0
        feature = feature["feature"]
        while True:

            if count >= MAX_COUNT:
                print("<>")
                break
            tmp = self.tubes_heartbeat(count, feature)
            if tmp is None:
                retry += 1
                if retry > 50:
                    break

                self.Logger.info("Waiting Sleep 500 sec")
                time.sleep(500)
                continue
            retry = 0
            print(">>>")
            for i in tmp :
                print(i)
                try:
                    pcode = i[0]
                    code  = eval(i[1])["indicId"]
                    self.tubes_detail(code=code, pcode=pcode)
                except Exception as e:
                    self.Logger.error(e)
                else:
                    time.sleep(0.08)
            count += 1000

    def Tubes(self, taskinfo):
        import datetime

        try:
            self.plat_id = taskinfo["plat_id"]
            code = eval(taskinfo["obj_ext"])["indicId"]
            dataflow = self.obj.parse(code=code, retries=0)
            taskinfo['report_time'] = '%s' % datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            taskinfo["data"] = dataflow["data"]
            taskinfo['process_code'] = os.getpid()

        except Exception as e:
            self.Logger.error(["TubesError[%d]"%os.getpid(), e])

        else:
            return taskinfo

    def __del__(self):
        self.Logger.info("-----[%d] END-----"%os.getpid())
        del self.sql



def f(t):
    import requests
    for i in range(3):
        print(requests.get(t), t, i)
        time.sleep(1)

if __name__ == '__main__':

    #({"feature":"632815","offset":0*10000}
    from gevent import  monkey
    import gevent
    monkey.patch_all()
    p = RoboTubes(platid=2)
    # for i in range(1, 23):
    #     print(0)
    #     p.tmp_crawl({"feature":"632815","offset":i})

    tt = [gevent.spawn(p.tmp_crawl, {"feature":"632815","offset":i}) for i in range(23)]
    gevent.joinall(tt)




