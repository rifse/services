# Services
Service setup guide

## Service configuration

Prepare files:
1. $ mkdir -p ~/.config/systemd/user
2. $ mv ticker_service ~/.config/user/ticker.service

Run services:<br/>
3. $ systemctl --user enable ticker_service<br/>
4. $ systemctl --user daemon-reload<br/>
5. $ systemctl --user start ticker_service<br/>
6. Do the same for other user services.<br/>

Set persistence after user logout:<br/>
7. $ sudo loginctl enable-linger $USER<br/>

Useful commands:<br/>
1. $ systemctl status some_service<br/>
2. $ journalctl --user-unit some_service<br/>
