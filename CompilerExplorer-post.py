import requests
import pdb
import logging
import os


def compile_and_check_output(compiler_id, source_filename, args=' -O0', oracle=None):
    compile_retcode, expected_retcode, expected_output = oracle
    try:
        # Read source file
        with open(source_filename, 'r') as file:
            source_code = file.read()

        # Compiler Explorer API endpoint
        api_url = "https://godbolt.org/api/compiler/{compiler_id}/compile"
        
        # post arguments
        params = {
            "source": source_code,
            "options": {
                "userArguments": args,
                "filters": {
                    "intel": True,
                    "demangle": True,
                    "directives": True,
                    "execute": True,
                    "comments": True,
                    "labels": True
                }
            },
            "compilerOptions": {
                "executorRequest": True
            }
        }
        
        # send POST request
        response = requests.post(api_url.format(compiler_id=compiler_id), json=params)
        
        # debug information
        logging.debug(f"Status Code: {response.status_code}, Response Text:{response.text}")

        # process responses
        if response.status_code == 200:
            try:
                # get execution exit code
                if response.text.find("# Execution result with exit code") < 0:
                    execution_retcode = ""
                else:
                    retcode_sindex = response.text.find("# Execution result with exit code") + len("# Execution result with exit code")
                    retcode_eindex = response.text.find("# Standard out:")
                    if retcode_eindex < 0:
                        execution_retcode = response.text[retcode_sindex:].strip()
                    else:
                        execution_retcode = response.text[retcode_sindex:retcode_eindex].strip()

                # get execution output
                if response.text.find("# Standard out:") < 0:
                    execution_output = ""
                else:
                    output_sindex = response.text.find("# Standard out:") + len("# Standard out:")
                    output_eindex = response.text.find("# Standard err:")
                    if output_eindex < 0:
                        execution_output = response.text[output_sindex:].strip()
                    else:
                        execution_output = response.text[output_sindex:output_eindex].strip()

                # get standard errcode
                if response.text.find("# Standard err:") < 0:
                    execution_errcode = ""
                else:
                    errcode_index = response.text.find("# Standard err:") + len("# Standard err:")
                    execution_errcode = response.text[errcode_index:].strip()

                # pdb.set_trace()
                # if oracle is not None, check whether the output is consistent
                if oracle is not None:
                    if execution_output == expected_output and execution_retcode == expected_retcode:
                        logging.info(f'({compiler_id}) [Match] Execution output: {execution_output}, Execution retcode: {execution_retcode}, Execution errcode: {execution_retcode}')
                        return True
                    else:
                        logging.info(f'({compiler_id}) [UNMatch] Execution output: {execution_output}, Execution retcode: {execution_retcode}, Execution errcode: {execution_retcode}')
                        return False
                else:
                    # if oracle is None, chech whether the code can be compiled successfully. 
                    return True
            except Exception as e:
                logging.error("Error processing response:", e)
                return False
        else:
            logging.error(f"Error: {response.status_code}, {response.text}")
            return False
    
    except FileNotFoundError as fnf_error:
        logging.error(f"File not found: {fnf_error}")
        return False

    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return False

avers = {'trunk': ['cgsnapshot'], 
                '14': ['cg141'], 
                '13': ['cg132', 'cg131'], 
                '12': ['cg123', 'cg122', 'cg121'], 
                '11': ['cg114', 'cg113', 'cg112', 'cg111'], 
                '10': ['cg105', 'cg104', 'cg103', 'cg102', 'cg101'], 
                 '9': ['cg95', 'cg94', 'cg93', 'cg92', 'cg91'], 
                 '8': ['cg85', 'cg84', 'cg83', 'cg82', 'cg81'], 
                 '7': ['cg75', 'cg74', 'cg73', 'cg72', 'cg71'], 
                 '6': ['cg65', 'cg63', 'cg62', 'cg6'], 
                 '5': ['cg540', 'cg530', 'cg520', 'cg510'],
                 '4.9': ['cg494', 'cg493', 'cg492', 'cg491', 'cg490'], 
                 '4.8': ['cg485', 'cg484', 'cg483', 'cg482', 'cg481'], 
                 '4.7': ['cg474', 'cg473', 'cg472', 'cg471'], 
                 '4': ['cg464', 'cg453', 'cg447', 'cg412', 'cg404', 'cg346']
            }


def checkEachVersions(source_filename, args=None, oracle=None):
    for key in avers.keys():
        for compiler_id in avers[key]:

            is_successful = compile_and_check_output(compiler_id=compiler_id, source_filename=source_filename, args=args, oracle=oracle)

            if is_successful:
                print(f'{compiler_id} success')
            else:
                print(f'{compiler_id} failed')


# example code
source_filename = os.path.join(os.getcwd(), '114551.c') # the bug-triggering test program
args = '-O3'  ### the bug-triggering optimization flag
oracle = ('0', '0', '')  # the compilation return code, the expected output, execution return code

logging.basicConfig(filename="compilerexplorer.log", level=logging.INFO)

checkEachVersions(source_filename, args, oracle)
