# spider-version
- version:1.0.0 - 增加公用登录函数，防止过多线程协程下线 
   + EasyMethod.RoboEasyLogin 
   + asyMethod.getCookie 
   + 多线程协程容易造成IO堵塞，造成程序假死， 建议单线程。必要时可多进程
   + updateTime:2018-11-02

- version:1.0.1 - 修改登录逻辑，增加redis缓存回溯。
 + 存放地址是的seen:code,
 + 目的回溯已经爬取的code进行过滤。
 + updateTime:2018-11-04

- version:1.0.2 - 禁用多线程。开启多进程协程此程序无需通信
 + 每个频道配备一个用户
 + updateTime:2018-11-05
        
- version:1.0.2.1 - 禁用多线程。开启多进程协程此程序无需通信
 + 每个频道配备一个用户, 开多会卡停顿。待解决
 + updateTime:2018-11-05
