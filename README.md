# Services
Service setup guide

## Service configuration

### Prepare files:
```shell
mv .config ~/
```

### Run services:<br/>
```shell
systemctl --user enable placeHolder.service
systemctl --user daemon-reload
systemctl --user start placeHolder.service
```
Do the same for other user services.

#### Set persistence after user logout:
```shell
sudo loginctl enable-linger $USER
```

## Useful commands:
```shell
systemctl status anyName.service
journalctl --user-unit anyName.service
```
