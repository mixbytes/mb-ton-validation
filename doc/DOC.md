# Miscellaneous info


## Move validator to another machine

[TODO] - written very fast, check it later

- on target machine
    - build and prepare validator to run as fullnode

- on source validator machine
    - disable automatic (or cron) launch of script ```validator_msig.sh <STAKE_AMOUNT>``` that participates in validator elections to later repeat in on new validator
    - backup ```$HOME/ton-keys```
    - stop validator on source machine ```pkill -f validator-engine```
    - (optional) remove large log to skip it's copying ```mv /var/ton-work/node.log /tmp```
    - copy whole ```/var/ton-work``` to new validator machine
    - copy ```$HOME/ton-keys``` to new validator machine

- on target validator machine
    - (optional) make right ```chown``` on ```/var/ton-work``` and ```$HOME/ton-keys```, according to user, running validator
    - rename files in ```$HOME/ton-keys/``` containing old hostname to new hostname. For example ```<old_hostname>.addr``` to ```<new_hostname.addr``` and so on
    - open ```/var/ton-work/db/config.json``` and change ```ip: 12344556``` string to decimal representation of ip of new validator. For example, if your new IP is ```62.192.13.19``` you can do it with ```echo 66.102.13.19 | tr . '\n' | awk '{s = s*256 + $1} END{print s}'```
    - launch ```validator_msig.sh <STAKE_AMOUNT>``` command (like on surce validator) to check it works normally. (it opreates you files in ```$HOME/ton-keys```
    - launch ```validator-engine``` with run, check log. There will be errors first 5-10 minutes, then it should to begin validate
    - add ```validator_msig.sh <STAKE_AMOUNT>``` launch command to cron (or make it llaunch automatically). 


