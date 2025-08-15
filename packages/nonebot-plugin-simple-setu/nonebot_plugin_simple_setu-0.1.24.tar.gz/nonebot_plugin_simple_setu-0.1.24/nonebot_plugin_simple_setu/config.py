from pydantic import BaseModel


class Config(BaseModel):
    """Plugin Config Here"""
    #选择色图api
    #0为lolicon
    #1为jitsu
    #在某些情况下jitsu比lolicon快
    simple_setu_api_url :int= 0
