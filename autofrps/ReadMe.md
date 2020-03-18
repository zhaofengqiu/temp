## 修改远程密码
密码在`/etc/frps.ini`中，只要修改其中的`token`即可
## 启动frps
采用进程保护
启动的方式：
```
supervisorctl reload 
```
## 停止frps
```
supervisorctl stop all 
```
