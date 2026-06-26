from datetime import datetime

def maru_race_status_fallback(recommend_data=None, race_hint=None):
    if recommend_data:
        return {'status':'추천 있음','message':'저장된 추천 표시','data':recommend_data}
    if race_hint:
        return {'status':'경주 있음 / 추천 생성 대기','message':f'{race_hint} 경주 일정 감지. 수집/분석 후 추천 표시','data':None}
    return {'status':'추천 대기','message':'경주 일정 수집 또는 추천 생성 필요','data':None}
