# mb-ton-validation
TON validation infrastructure scripts


## Multisig autosigner

### Description 
This script automatially signs all messages, awaiting confirmations on given multisig contract address.
It uses pre-configured ```tonos-cli``` utility. Full logic is mostly described in script comments and messages.

### How it works

In few words, when run, script:

- checks extstance of executable and config file for ```tonos-cli``` utility
- checks existance of .abi and .keys.json files, required by ```tonos-cli``` to interact with given contract
- asks pending transactions for multisig address, passed to script
- sends transaction to multisig contract, confirming found transasction id

### How to setup

1. It's better to have separate catalog for each validator, for example "./validator1"
2. You need to have address of you multisig contract like "-1:ab1f1e8daf784ba59d9ae6266bbadda7a0b63a1d5d38eed5c9a11161861eb1cd"
3. You need to configure ```tonos-cli``` utility to work form this dir, preconfigured it using ```tonos-cli config --url <URL> --abi <PATH_TO_ABI> --keys <PATH_TO_KEYS_FILE>```. There sould be a config file like ```tonlabs-cli.conf.json``` with all these values in ths dir.
4. File with keys should contain keypair (public/secret) for one of multisig custodians
5. you can run script with ```python3 <PATH_TO_SCRIPT>/freeton_multisig_autosigner.py --multisig-addr="-1:ab1f1e8daf784ba59d9ae6266bbadda7a0b63a1d5d38eed5c9a11161861eb1cd"```
6. To automate autosigning of multisig tranasctions, you can use ```watch``` shell command ot add to crontab something like 
```cd /home/validator/validator1 && python3 /home/validator/mb-ton-validation/scripts/freeton_multisig_autosigner.py --multisig-addr="-1:ab1f1e8daf784ba59d9ae6266bbadda7a0b63a1d5d38eed5c9a11161861eb1cd" >> ./autosign-validator1.log 2>&1```

[WARNING] Due to bug/feature in arguments parsing in Python3 you must pass multisig address parameter, containig '-1' in the beginning, like "-1:XXXXXXXXXXXXXX" with '=' sign. Note '=' in examples above

### [TODO] 
- check destination address of confirming transaction to sign only election transaction
- wait for stable ```tonos-cli``` to make complete pack of checks
- make script monitor and confirm transactions without cron or watch, as a usual service


## To be continued with other scripts
