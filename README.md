## installation
> pip install -r requirements.txt



## How to use:
start the service to download datalog from mongoDB, and calculate the (dis)charging energy over the last week to judge if the electric storage systems are abnormal. If it is a ``yes'', send a ``trigger flag'' to MySQL.
> python ./diagnose_trigger_service.py
start the service to query the ``trigger flag'' in MySQL, analyze the State of Charge and the State of Health of each battery in the system with error, draw plots showing results, and give final solutions to the errors.
> python ./diagnose_running_service.py

The algorithms written in the Python code for SOX calculations refer to https://www.coursera.org/specializations/algorithms-for-battery-management-systems 
