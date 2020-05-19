#/usr/bin/python3

import argparse
import re
import json
import os
from freeton_validator_utils import *

# [TODO] - deal with these variables later, after stable version of tonos-cli
TONOS_EXECUTABLE = './tonos-cli'
TONOS_CONFIG = './tonlabs-cli.conf.json'
TONOS_URL = 'https://main.ton.dev' # 'https://net.ton dev' for developers network

def check_tonos_cli_configuration():
    
    # ./tonos-cli exists?  
    if (not os.path.isfile(TONOS_EXECUTABLE)):
         fail_with_return_code_and_mesage(3, "[ERROR] Cannot find 'tonos-cli' executable."
                                             "Current working dir is: '{}', check if file '{}' is present here"
                                            .format(os.getcwd(), TONOS_EXECUTABLE))

    # [WARN] This part can change often with changes in tonos-cli configuration
    # Modify or disable these checks, but pay special attention to part with PRIVATE KEYS
    # hust check your tonos-cli can sign messages to your multisig. 
    
    #  config for ./tonos-cli exists?
    if (not os.path.isfile(TONOS_CONFIG)):
         fail_with_return_code_and_mesage(4, "[ERROR] Cannot find 'tonos-cli' config."
                                             "Current working dir is: '{}', check if file '{}' is present here"
                                            .format(os.getcwd(), TONOS_CONFIG))
    
    # ./tonlabs-cli.conf.json is a JSON file? 
    tonos_config = {}
    with open(TONOS_CONFIG) as json_file:
        try:
            tonos_config = json.load(json_file)
        except: # [TODO] handle different exceptions
            fail_with_return_code_and_mesage(66, "[ERROR] Cannot load 'tonos-cli' JSON config from '{}'"
                                             "Check if internal format of this file is JSON"
                                             .format(TONOS_CONFIG))

    # is 'url' key present and set and looks like 'http
    if (not tonos_config.get('url')):
        fail_with_return_code_and_mesage(67, "[ERROR] 'url' value is not set in config '{}'"
                                             "Set it with 'tonos-cli config --url <URL>' to something like 'https://main.ton.dev' "
                                             " and it will be stored in config"
                                            .format(TONOS_CONFIG))
 
    if (not tonos_config.get('abi_path')):
        fail_with_return_code_and_mesage(68, "[ERROR] 'abi' value is not set in config '{}' "
                                             "Set it with 'tonos-cli config --abi <PATH_TO_ABI_FILE>' "
                                             "to something like 'SafeMultisigWallet.abi.json'"
                                             " and it will be stored in config"
                                            .format(TONOS_CONFIG))

    if (not os.path.isfile(tonos_config['abi_path'])):
         fail_with_return_code_and_mesage(69, "[ERROR] .abi.json file '{}', from config file '{}' doesnt exist. "
                                              "Find it github repo, containing code and ABI of calling multisig contract"
                                            .format(tonos_config['abi'], TONOS_CONFIG))

    if (not tonos_config.get('keys_path')):
        fail_with_return_code_and_mesage(71, "[ERROR] 'keys_path' value is not set in config '{}'"
                                             "Set it with 'tonos-cli config --keys <PATH_TO_KEYS_FILE>' "
                                             " with path to file with public and private key "
                                             " and it will be stored in config"
                                            .format(TONOS_CONFIG))

    if (not os.path.isfile(tonos_config['keys_path'])):
         fail_with_return_code_and_mesage(72, "[ERROR] keys file '{}' for config file '{}' doesnt exist"
                                              "Make it existing with right keys in it"
                                              "(allowed to confirm transacitons in given multisig contract)"
                                            .format(tonos_config['keys'], TONOS_CONFIG))

    return(True)


def get_awaiting_msig_tx(msig_addr):
    # receive ONE transaction, awaiting confirmation in multisig
    print(timestamp() + "[INFO] Checking transactions from addr: {}".format(msig_addr))

    shell_cmd_get_tx_id = ' '.join([TONOS_EXECUTABLE, #  join "./tonos-cli" \
                           'run',                   # "read" type of contract method (for "write" methods use "call")
                           msig_addr,               # address of multisig contract
                           'getTransactionIds',     # name of calling method
                           "'{}'"])                 # arguments passed to method in JSON format

    # run command like 
    # ./tonos-cli run -1:ab1f1e8daf784ba59d9ae6266bbadda7a0b63a1d5d38eed5c9a11161861eb1cd getTransactionIds '{}'
    print(timestamp() + "[DEBUG] Shell running command: {:s}".format(shell_cmd_get_tx_id))
    result_output = run_shell_command_and_capture_output(shell_cmd_get_tx_id)
    
    # Part of output, containing transactions ids (usually simple)
    # ```
    # Running get-method...
    # Succeeded.
    # Result: {
    #   "fees": null,
    #   "output": {
    #	  "ids": ["0xfeb70af84cbd0c41", "0xaeb714aa8db520c1"]
    #   }
    # ```

    success_marker_regexp = re.compile(r'^\s*Succeeded.\s*$', re.MULTILINE) # add this to be sure, that call was successfull
    succeded  = success_marker_regexp.search(result_output)
    if (not succeded):
        fail_with_return_code_and_mesage(2, "[ERROR] Run method to multisig_addr was not succseeded, "
                                            "cannot find regexp '{}' in output:\n "
                                            "{:s}\n"
                                            "Failed cmd: ```{:s}```"
                                            .format(success_marker_regexp, result_output, shell_cmd_get_tx_id))

    # find string like "ids": ["0xfeb70af84cbd0c41", "0xaeb714aa8db520c1"]
    find_tx_id_regexp = re.compile(r'^\s+"ids":\s+\["(0x[0-9a-f]{16})"', re.MULTILINE)
    matches = find_tx_id_regexp.findall(result_output)
    
    return matches[0] if matches else None


def confirm_awaiting_msig_tx(msig_addr, tx_id):
    print(timestamp() + "[INFO] Trying to confirm tx_id {} on addr: {:s}".format(tx_id, msig_addr))

    call_params = "\'" + json.dumps({ "transactionId": tx_id}) + "\'"
    shell_cmd_confirm_tx_id = ' '.join([TONOS_EXECUTABLE, #  join "./tonos-cli" \
                              'call',                   # "write" type of contract method (for "read" methods use "run")
                              msig_addr,                # address of multisig contract
                              'confirmTransaction',     # name of calling method
                              call_params])        # arguments passed to method in JSON format
    
    print(timestamp() + "[DEBUG] Shell running command: {:s}".format(shell_cmd_confirm_tx_id))
    confirm_result = run_shell_command_and_capture_output(shell_cmd_confirm_tx_id)

    success_marker_regexp = re.compile(r'^\s*Succeeded.\s*$', re.MULTILINE) # add this to be sure, that call was successfull
    succeded  = success_marker_regexp.search(confirm_result)
    if (not succeded):
        fail_with_return_code_and_mesage(3, "[ERROR] Call confirmation method to multisig_addr was not succseeded, "
                                            "cannot find regexp '{}' in output:\n "
                                            "{:s}\n"
                                            "Failed cmd: ```{:s}```"
                                            .format(success_marker_regexp, confirm_output, shell_cmd_confirm_tx_id))


    return True


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Script to automatiaclly sign multisig transactions',
                                        prefix_chars='--', allow_abbrev=False)

    # [WARN] Due to bug/feature in argparse for Python3 
    # you must pass multisig address parameter, containig '-1' in the beginning, like "-1:XXXXXXXXXXXXXX" with '=' sign
    # EXAMPLE: 
    # ```
    # $ python3 ../scripts/freeton_multisig_autosigner.py --multisig-addr="-1:ab1f1e8daf784ba59d9ae6266bbadda7a0b63a1d5d38eed5c9a11161861eb1cd"
    # ```    
    # !!!! note the "=" sign in --multisig-addr

    parser.add_argument('--multisig-addr',
                            type=str,
                            help = 'address of multisig to sign transaction. Warning. Set it like --multisig-addr="-1:deadbeef111...." to Python correctly parse it',
                            required = True)

    args = parser.parse_args()

    # check existance of executable, config, options in
    # exits with non-zero code if something not present
    check_tonos_cli_configuration()
    
    confirm_tx_id = get_awaiting_msig_tx(args.multisig_addr)

    if (not confirm_tx_id):
        print(timestamp() + "[INFO] Call to {} succeeded, but no transactions to sign was found. "
              "Exiting normally.".format(args.multisig_addr))
        exit(0)

    print(timestamp() + "[INFO] Found tx_id: {}, awating for confirmation on mulisig addr: {}"
          .format(confirm_tx_id, args.multisig_addr))
    
    result_of_confirm = confirm_awaiting_msig_tx(args.multisig_addr, confirm_tx_id)
    print(timestamp() + "[DEBUG] Output of confirm command:\n")
    print(result_of_confirm)

    exit(0)

