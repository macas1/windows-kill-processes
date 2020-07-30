import os, wmi, ctypes, sys

# SETTINGS
list_name = "blacklist.txt"
output_space = 2

# END SETTINGS

def split_app_str(app_str):    
    if "#" in app_str:
        app_str = app_str.split("#")[0]
    
    for l in [" &", "& "]:
        while l in app_str:
            app_str = app_str.replace(l, "&")

    return app_str.strip().lower().split("&")

def get_list():
    out = []
    with open(list_name, "r") as f:
        for line in f.readlines():
            if not line:
                continue

            out.append(line)

    out = list(dict.fromkeys(out))

    for i in range(len(out)):
        out[i] = split_app_str(out[i])
    return out

def get_tasks():
    # Get process name list
    processes = wmi.WMI().Win32_Process()
    tasks = []
    for p in processes:
        tasks.append(p.name)

    # Remove duplicates and sort from list
    tasks = list(dict.fromkeys(tasks))
    return tasks

def get_real_apps(tasks, apps):
    out = []
    for task in tasks:
        task = task.lower()
        for app in apps:
            found = True
            for section in app:
                if section not in task:
                    found = False
                    break

            if found:
                out.append(task)
                break

    out = list(dict.fromkeys(out))
    out.sort()
    return out

def extend_str(string, length):
    while len(string) < length:
        string += " "

    return string[0:length]

def longest(str_arr):
    long = -1
    for s in str_arr:
        if len(s) > long:
            long = len(s)
    return long

def kill(tasks):
    for t in tasks:
        os.system("taskkill /f /im " + t)

def print_killed(before, after, attempts):
    col = longest(["TASK_NAME"] + before)
    col += output_space

    print("\n" + extend_str("TASK_NAME", col) + "STATUS")
    print("-"*(col+12))
    
    for task in before:
        prefix = "KILLED"
        if task in after:
            prefix = "ALIVE"
            if task in attempts:
                prefix += " (ATTEMPTED)"

        print(extend_str(task, col) + prefix)

def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def handle_admin():
    if not is_admin():
        if(ctypes.windll.shell32.ShellExecuteW(None, "runas", sys.executable, " ".join(sys.argv), None, 1) != 5):
            sys.exit(0)
        
def main():
    # Get admin priv or run without it
    handle_admin()

    # Get lists
    tasks = get_tasks()
    apps = get_list()
    to_kill = get_real_apps(tasks, apps)

    # Kill tasks and print summary
    kill(to_kill)
    print_killed(tasks, get_tasks(), to_kill)
    input("\nProcess complete, press enter to continue.")

if __name__ == "__main__":
    main()
