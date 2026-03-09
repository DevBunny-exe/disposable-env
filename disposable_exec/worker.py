import time

from disposable_exec.logs import write_log
from disposable_exec.queue import dequeue_job
from disposable_exec.results import save_result
from disposable_exec.status import set_status
from disposable_exec.runtime import run_script_in_docker


print("Worker started...")


while True:
    job = dequeue_job()

    if not job:
        time.sleep(0.2)
        continue

    execution_id = job["execution_id"]
    code = job["script"]
    key_id = job["key_id"]

    set_status(execution_id, "running")

    try:
        output = run_script_in_docker(code, timeout=10)

        write_log(
            execution_id,
            key_id,
            output["stdout"],
            output["stderr"],
            output["exit_code"],
            output["duration"]
        )

        save_result(execution_id, output)

        if output["exit_code"] == -1:
            set_status(execution_id, "failed")
        else:
            set_status(execution_id, "finished")

        print("Job finished")

    except Exception as e:
        set_status(execution_id, "failed")

        save_result(
            execution_id,
            {
                "stdout": "",
                "stderr": str(e),
                "exit_code": -1,
                "duration": 0
            }
        )
