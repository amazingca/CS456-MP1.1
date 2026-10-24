## CS456-MP1.1

### service.py

**Required installed modules:**
- bcrypt
- flask

Please use `python service.py --help` for the help message along with parameters.

#### Credential pair generation & default test credentials

For testing, you can generate your own bcrypt hash using the provided argument:

`python service.py --passhash=<passphrase>`

This is for testing purposes so you can embed your own credentials in the CSV of your choice. The one in this repository (`creds.csv`) contains the following default credentials:

| Username | Password |
| -------- | -------- |
| test     | `test`   |
| admin    | `password` |

#### Quickstart command

To get up and running quickly, you can use the following command to use this default credential file, bind to port `2048` on `0.0.0.0`, and declare the heartbeat monitor at `192.168.255.255:44444`:

```python service.py --hash-file=creds.csv --host-ip=0.0.0.0 --host-port=2048 --heartbeat-ip=192.168.255.255 --heartbeat-port=44444```

#### Testing in the browser

The primary means of verifying credentials can be done at `http://localhost:2048/login`, provided that you use the quickstart command listed above. Normally, the browser will ask you to provide a username and password, but you can also provide them by following the according URI structure:

```http://<username>:<passphrase>@localhost:2048/login```
