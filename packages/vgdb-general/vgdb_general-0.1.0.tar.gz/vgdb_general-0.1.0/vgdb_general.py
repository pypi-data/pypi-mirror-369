import requests


def smart_http_request(
    s: requests.Session,
    url="",
    method="get",
    params=None,
    headers=None,
    data=None,
    json=None,
    tries=10,
    verify=False,
):
    i = 1
    status_code = 0
    result = None
    if url:
        while (not result) and i <= tries and status_code != 200:
            i += 1
            try:
                if method == "get":
                    result = s.get(url, params=params, headers=headers, verify=verify)
                if method == "post":
                    result = s.post(
                        url, data=data, json=json, headers=headers, verify=verify
                    )
                status_code = result.status_code
            except:
                pass
    return (status_code, result)
