from typing import Optional

import httpx
import uvicorn
import msal
from starlette.middleware.sessions import SessionMiddleware
from fastapi import FastAPI, Request, Form
from fastapi.responses import RedirectResponse, HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi_msal import MSALAuthorization, MSALClientConfig
from fastapi_msal.models import AuthToken

# Added by Jim Lynn
from fastapi.staticfiles import StaticFiles


class AppConfig(MSALClientConfig):
    # You can find more Microsoft Graph API endpoints from Graph Explorer
    # https://developer.microsoft.com/en-us/graph/graph-explorer
    # endpoint: str = "https://graph.microsoft.com/v1.0/users"  # This resource requires no admin consent
    endpoint: str = "https://graph.microsoft.com/v1.0/me/onlineMeetings"
    login_path = "/login"  # default is '/_login_route'
    logout_path = "/logout"  # default is '/_logout_route'


config = AppConfig(_env_file="app_config.env")

app = FastAPI()
app.add_middleware(SessionMiddleware, secret_key=config.client_credential)
auth = MSALAuthorization(client_config=config)
app.include_router(auth.router)

# app.mount added by Jim Lynn
# static directory was added by Jim Lynn
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")
user_name = 'Jim Lynn'


@app.get("/", response_class=HTMLResponse)
async def index(request: Request):
    token: Optional[AuthToken] = await auth.get_session_token(request=request)
    if not token or not token.id_token_claims:
        return RedirectResponse(url=config.login_path)
    context = {
        "request": request,
        "user": token.id_token_claims,
        "version": msal.__version__,
        "user_name": user_name
    }
    return templates.TemplateResponse(name="index.html", context=context)

#  This route was discontinued and replaced with handleForm.  This route used a hard coded date and time, rather
#       than allowing the user to select the meeting date and time.
@app.get("/schedulecall")
async def schedulecall(request: Request):
    # below variables are only used before we do actual web service call - Jim Lynn
    host = 'jim.lynn@lynnlabsinc.onmicrosoft.com'
    confid = '91857-1949-1111'
    tollno = '+1 929-352-1691'
    dialurl = 'https:/dialin.teams.microsoft.com/6666666'

    my_parameters = {
        "startDateTime": "2022-12-12T14:30:34.2444915-07:00",
        "endDateTime": "2022-12-12T15:00:34.2464912-07:00",
        "subject": "My Meeting",
        "lobbyBypassSettings": {
                                "scope": "organization",
                                "isDialInBypassEnabled": "true"
        }
    }

    token: Optional[AuthToken] = await auth.handler.get_token_from_session(request=request)
    if not token or not token.access_token:
        return RedirectResponse(url=config.login_path)
    async with httpx.AsyncClient() as client:
        #  resp = await client.get(
        #      config.endpoint, headers={"Authorization": "Bearer " + token.access_token},
        #  )
        resp = await client.post(
            config.endpoint, json=my_parameters, headers={"Authorization": "Bearer " + token.access_token,
                                                          "Content-type": "application/json"},
        )
    graph_data = resp.json()
    #  uncomment the print below if you want to see the
    #    json returned from POST above
    print(graph_data)

    if 'error' in graph_data:
        print("error found")
        errorcode = graph_data['error']['code']
        jsondata = graph_data['error']['innerError']

        context = {"request": request, "errorCode": errorcode, "jsonData": jsondata}
        return templates.TemplateResponse(name="errorFound.html", context=context)
    #
    confid = graph_data['audioConferencing']['conferenceId']
    tollno = graph_data['audioConferencing']['tollNumber']
    dialurl = graph_data['audioConferencing']['dialinUrl']
    host = graph_data['participants']['organizer']['upn']
    context = {"request": request, "host": host, "confid": confid, "tollno": tollno, "dialurl": dialurl}
    return templates.TemplateResponse(name="results.html", context=context)


@app.post("/handleForm")
async def handleForm(request: Request):
    formdata = await request.form()

    #  added the ":00.0000000-07:00" to make the datetime-local work in graph call using UTC.
    starttime = formdata.get('startTime')
    starttime += ":00.0000000-07:00"
    endtime = formdata.get('endTime')
    endtime += ":00.0000000-07:00"

    my_parameters = {
        "startDateTime": starttime,
        "endDateTime": endtime,
        "subject": formdata.get('subject'),
        "lobbyBypassSettings": {
            "scope": "organization",
            "isDialInBypassEnabled": "true"
        }
    }
    print(my_parameters)

    token: Optional[AuthToken] = await auth.handler.get_token_from_session(request=request)
    if not token or not token.access_token:
        return RedirectResponse(url=config.login_path)
    async with httpx.AsyncClient() as client:
        resp = await client.post(
            config.endpoint, json=my_parameters, headers={"Authorization": "Bearer " + token.access_token,
                                                          "Content-type": "application/json"},
        )
    graph_data = resp.json()
    #  uncomment the print below if you want to see the
    #    json returned from POST above
    print(graph_data)

    if 'error' in graph_data:
        print("error found")
        errorcode = graph_data['error']['code']
        jsondata = graph_data['error']['innerError']

        context = {"request": request, "errorCode": errorcode, "jsonData": jsondata}
        return templates.TemplateResponse(name="errorFound.html", context=context)
    #
    confid = graph_data['audioConferencing']['conferenceId']
    tollno = graph_data['audioConferencing']['tollNumber']
    dialurl = graph_data['audioConferencing']['dialinUrl']
    host = graph_data['participants']['organizer']['upn']
    context = {"request": request, "host": host, "confid": confid, "tollno": tollno, "dialurl": dialurl}
    return templates.TemplateResponse(name="results.html", context=context)


if __name__ == "__main__":
    uvicorn.run("app:app", host="localhost", port=3000, reload=True)
