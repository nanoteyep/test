import paramiko

command_dir = 'volume1/notitia/_Trademark_Data/TrademarkReport\(idx\)/'
next_task = {'AGENT' : 'APPLICANT',
             'APPLICANT' : 'TB_KT10',
             'TB_KT10' : 'TB_KT11',
             'TB_KT11' : 'TB_KT13',
             'TB_KT13' : 'TB_KT14',
             'TB_KT14' : 'TB_KT15',
             'TB_KT15' : '.'}
log_dir = './read_log.txt'

def create_log(year, date, task):
    log_file = open(log_dir, 'w')
    log_file.write(year + ' ' + date + ' ' + task)
    log_file.close()

# initialize log
# create_log('2021', '20211231', 'AGENT')

log_file = open(log_dir)
log_info = log_file.readline().split(' ')
latest_year = str(log_info[0])
latest_date = str(log_info[1])
current_task = str(log_info[2])

try:
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy)
    ssh.connect(hostname="219.240.18.95", username="notitia", password="note2022@SB", port=40022)

    # operation code
    stdin, stdout, stderr = ssh.exec_command('ls ' + command_dir)
    years = stdout.readlines()
    for year in years:
        dir_year = str(year).replace('\n', '')
        year = str(dir_year[-4:])
        if year == '2021':
            # in case of 2021 only
            if int(year) >= int(latest_year) and current_task != 'TB_KT15':
                year_dir = command_dir + '상표\ 공보\(서지\)_' + year + '/'
                stdin, stdout, stderr = ssh.exec_command('ls ' + year_dir)
                tasks = stdout.readlines()
                for task in tasks:
                    dir_task = str(task).replace('\n', '')
                    task = str(dir_task[14:-1])
                    if current_task == task:
                        task_dir = year_dir + dir_task + '/' + task + '.txt'
                        # txt_to_DB(task_dir, task)
                        current_task = next_task[current_task]
                        create_log(year, '20211231', current_task)
                    elif current_task == '.':
                        current_task = 'AGENT'
        else:
            # in case after 2022
            if int(year) >= int(latest_year):
                year_dir = command_dir + '상표\ 공보\(서지\)_' + year + '/'
                stdin, stdout, stderr = ssh.exec_command('ls ' + year_dir)
                dates = stdout.readlines()
                for date in dates:
                    date = str(date).replace('\n', '')
                    if int(date) >= int(latest_date):
                        date_dir = year_dir + date + '/' + date + '/'
                        stdin, stdout, stderr = ssh.exec_command('ls ' + date_dir)
                        tasks = stdout.readlines()
                        for task in tasks:
                            task = str(task).replace('\n', '')
                            task = str(task[:-4])
                            if current_task == task:
                                file_dir = date_dir + task + '.txt'
                                # txt_to_DB(file_dir, task)
                                current_task = next_task[current_task]
                                create_log(year, date, current_task)
                            elif current_task == '.':
                                current_task = 'AGENT'
                        # task initialize
                        current_task = 'AGENT'

    print('task ended')
    # operation code end

    ssh.close()
except Exception as err:
    print("ssh connect failed")