from enum import Enum

class FrameChannels(Enum):
    Channel_Vz = 0,
    Channel_Phase1 = 1,
    Channel_Phase2 = 2,
    Channel_Rms1 = 3,
    Channel_Rms2 = 4,
    Channel_WorkFunction = 5,
    Channel_VHall = 6,
    Channel_IHall = 7,
    Channel_Spare3 = 8,
    Channel_Spare4 = 9,
    Channel_Vpd = 10,
    Channel_VpdRef = 11,
    Channel_VpdSig = 12,
    Channel_Spare8 = 13,
    Channel_Spare9 = 14,
    Channel_Spare10 = 15,
    Channel_FN10 = 16,
    Channel_FN = 17,
    Channel_FL = 18,
    Channel_FT = 19,
    Channel_DeltaF = 20,
    Channel_ITunnel = 21,

    Channel_Custom1 = 31,
    Channel_Custom2 = 32,
    Channel_Custom3 = 33,
    Channel_Custom4 = 34,
    Channel_Custom5 = 35,

   
def GetAPIResponseKeyForChannel(channel:FrameChannels):
    if channel == FrameChannels.Channel_Vz:
        return "Vz"
    if channel == FrameChannels.Channel_Phase1:
        return "Lia1Phase"
    if channel == FrameChannels.Channel_Phase2:
        return "Lia2Phase"
    if channel == FrameChannels.Channel_Rms1:
        return "Lia1RMS"
    if channel == FrameChannels.Channel_Rms2:
        return "Lia2RMS"
    if channel == FrameChannels.Channel_WorkFunction:
        return "WorkFunction"
    if channel == FrameChannels.Channel_VHall:
        return "VHall"
    if channel == FrameChannels.Channel_IHall:
        return "IHall"
    if channel == FrameChannels.Channel_ITunnel:
        return "It"
    if channel == FrameChannels.Channel_Spare3:
        return "Spare3"
    if channel == FrameChannels.Channel_Spare4:
        return "Spare4"
    if channel == FrameChannels.Channel_Vpd:
        return "Vpd"
    if channel == FrameChannels.Channel_VpdRef:
        return "VpdRef"
    if channel == FrameChannels.Channel_VpdSig:
        return "VpdSig"
    if channel == FrameChannels.Channel_Spare8:
        return "Spare8"
    if channel == FrameChannels.Channel_Spare9:
        return "Spare9"
    if channel == FrameChannels.Channel_Spare10:
        return "Spare10"
    if channel == FrameChannels.Channel_FN10:
        return "Fnx10"
    if channel == FrameChannels.Channel_FN:
        return "Fn"
    if channel == FrameChannels.Channel_FL:
        return "Fl"
    if channel == FrameChannels.Channel_FT:
        return "Ft"
    if channel == FrameChannels.Channel_DeltaF:
        return "DeltaF"
    return ""
