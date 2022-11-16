from typing import Optional

from sqlmodel import Field, SQLModel


class MeetingBase(SQLModel):
    callid: str
    conf_create_time: str
    conf_start_time: str
    conf_end_time: str
    joinUrl: str
    meeting_Code: str
    subject: str
    isBroadcast: str
    auto_Admitted_Users: str
    outer_Meeting_Auto_Admitted_Users: Optional[str] = Field(default=None)
    isEntryExitAnnounced: bool
    allowedPresenters: str
    allowMeetingChat: str
    allowTeamworkReactions: bool
    allowAttendeeToEnableMic: bool
    allowAttendeeToEnableCamera: bool
    recordAutomatically: bool
    confid: str
    toll_no: str
    dialurl: str
    host: str
    hostRole: str


class Meeting(MeetingBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
