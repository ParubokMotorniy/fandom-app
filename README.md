# fandom-app

*Developer guidelines*:
+ If any 3rdparty service needs to be registered with consul - add its configuration file to `consul/3rdparty_services`
+ Similarly, if any key-value data is needed service-wise from consul - add it in JSON format (or whatever parasable format you want) to `consul/configs`

+ Once you merge your service into master - make sure the corresponding dummy entry in the compose file is replaced with the real service (mind the host addresses).
+ The same goes for the nginx configuration - as of now it makes calls to 'presumed' endpoints. Replace those with real ones on merge

+ Both the basic frontend and nginx assume that the user is now only capable of uploading simple html files with embedded images.

Old design:

![old](https://github.com/user-attachments/assets/57c50d6f-8519-491a-89c0-198dae81d249)

Refactored design:

![new](https://github.com/user-attachments/assets/d8e56c42-de4f-4025-a1a1-1562160d7b73)


