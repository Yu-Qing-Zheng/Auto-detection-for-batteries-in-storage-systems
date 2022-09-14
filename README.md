## 运行条件
> 列出运行该项目所必须的条件和相关依赖  
1. pip install -r requirements.txt



## 运行说明
> 说明如何运行和使用你的项目，建议给出具体的步骤说明
1. 电芯电量异常检测：
python ./diagnose_trigger_service.py
2. 钉钉机器人:
python ./energy_trigger_pusher.py


## docker部署

项目目录下运行如下命令

'''
docker build -f ./dockerfile.yaml  -t auto_diagnose_triger .

docker run --name auto_diagnose_trigger -d auto_diagnose_triger
'''
