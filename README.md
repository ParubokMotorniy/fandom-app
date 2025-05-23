# fandom-app

Overview of services:
+ `api-gateway` - all requests to the app are proxied through this service. Authentication of requests also happens here if needed, by asking `auth-service`.
+ `auth-service` - takes care of user registration, issuing of session tokens, login etc.
+ `page-adding-service` - new pages are forwarded to this service. It generates a unique ID for the page to be used across the app, and then forwards the page through `kafka` topics to `search-service` (priorly striping off image cintent of the page) and `page-retrievers`.
+ `page-retrievers` - this cluster of services takes care of serving pages at user request by IDs. If one fails - requests will be forwarded to its buddies.
+ `search-service` - this service runs its own instance of `elasticsearch` for quick indexing and retrieval (based on a query string) of pages. When presented with a query string, it generates a list of links to the relevant pages.

*Important*

For `search-service` to work one has to copy the http certificate from elasticsearch to the `search` container. 

Old design:
![old](https://github.com/user-attachments/assets/57c50d6f-8519-491a-89c0-198dae81d249)

Refactored design:
![new](https://github.com/user-attachments/assets/d8e56c42-de4f-4025-a1a1-1562160d7b73)
